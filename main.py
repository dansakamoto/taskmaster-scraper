from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time

# CONFIG
debug = True
baseUrl = "https://taskmaster.info"
rootUrl = "https://taskmaster.info/show.php?id=1"
blacklist = ["Edinburgh Does... Taskmaster"]
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}

# load base URL
req = Request(rootUrl, headers=headers)
html_page = urlopen(req).read()
soup = BeautifulSoup(html_page, "lxml")

"""
STEP 1: collect seasons
"""
soup = soup.select("#seasonsandspecials > div.season > p.seasonTitle > a")
seasons = {}
print("Loading seasons list...")
for r in soup:
    if r.string in blacklist:
        continue
    season = {}
    season["url"] = baseUrl + r["href"]
    seasons[r.string] = season

"""
STEP 2: collect episodes
"""
for k, s in seasons.items():
    sleep(random.uniform(2, 5))
    print("\nScanning " + k)
    req = Request(s["url"], headers=headers)
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, "html.parser")
    soup2 = soup.select("#episodes")
    isSpecial = len(soup2) == 0

    episodes = []
    if isSpecial:
        soup2 = soup.select("#tasks")
        isUnaired = len(soup2) == 0
        if isUnaired:
            print("(unaired, skipping the rest...)")
            break
        print("(it's a special)")
        episodes.append({"title": "(special)", "url": s["url"]})
    else:
        soup = soup.select("#episodes > div.episode > p.episodeTitle > a")
        for a in soup:
            print(f"found episode: {a.string}")
            episodes.append({"title": a.string, "url": baseUrl + a["href"]})
    seasons[k]["episodes"] = episodes

"""
STEP 3: collect tasks
TBC
"""

"""
STEP 4: collect task data
TBC
"""

"""
STEP 5 (optional): analyze/filter/format task data
TBC
"""

"""
Save the results
"""
fName = f"outputs/out-{time.time()}.json"
print("\nWriting results to file " + fName)
out = open(fName, "w")
out.write(json.dumps(seasons, indent=2, ensure_ascii=False))
out.close()
print("\nDone!")
