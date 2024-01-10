from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# CONFIG
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

allSeasons = {}

# DEBUG
skipTo = 3
if skipTo > 0:
    debugData = f"data/step{skipTo-1}_results.json"
    with open(debugData, "r") as f:
        allSeasons = json.load(f)
        f.close()

"""
STEP 1: collect seasons
"""
if skipTo <= 1:
    soup = soup.select("#seasonsandspecials > div.season > p.seasonTitle > a")
    print("Loading seasons list...")
    for r in soup:
        if r.string in blacklist:
            continue
        season = {}
        season["url"] = baseUrl + r["href"]
        allSeasons[r.string] = season

"""
STEP 2: collect episodes
"""
if skipTo <= 2:
    unaired = []
    for k, s in allSeasons.items():
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
                print("(unaired...)")
                unaired.append(k)
                continue
            print("(it's a special)")
            episodes.append({"title": "(special)", "url": s["url"]})
        else:
            soup = soup.select("#episodes > div.episode > p.episodeTitle > a")
            for a in soup:
                print(f"found episode: {a.string}")
                episodes.append({"title": a.string, "url": baseUrl + a["href"]})
        allSeasons[k]["episodes"] = episodes

    for k in unaired:
        allSeasons.pop(k)

"""
STEP 3: collect tasks
"""
if skipTo <= 3:
    for skey, svalue in allSeasons.items():
        for episode in svalue["episodes"]:
            sleep(random.uniform(2,5))
            print("\nScanning " + episode["title"])
            req = Request(episode["url"], headers=headers)
            html_page = urlopen(req).read()
            soup = BeautifulSoup(html_page, "html.parser")
            soup2 = soup.select("#tasks > div.task > div.taskInfo > div.taskCardTaskTitle > h3.taskLink > a")
            tasks = []
            for item in soup2:
                print(f"found task: {item.string}\nurl: {item['href']}")
                tasks.append({"title": item.string, "url": baseUrl + item["href"]})
            episode["tasks"] = tasks
        

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
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allSeasons, indent=2, ensure_ascii=False))
    f.close()
print("\nDone!")
