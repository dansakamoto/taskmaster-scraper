from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import json, time, os

# Load config
configFile = f"config.json"
with open(configFile, "r") as f:
    config = json.load(f)
    baseUrl = config["baseUrl"]
    seasonBlacklist = config["seasonBlacklist"]
    headers = config["headers"]
    attemptLimit = config["attemptLimit"]
    allVersions = config["targetVersions"]
    f.close()

# Iterate through show versions, finding seasons lists
for versionKey, version in allVersions.items():
    seasons = {}

    req = Request(version["url"], headers=headers)
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, "lxml")

    soup = soup.select("#seasonsandspecials > div.season > p.seasonTitle > a")
    print("Loading seasons list...")
    for r in soup:
        if r.string in seasonBlacklist:
            continue
        season = {}
        season["url"] = baseUrl + r["href"]

        print(f"found season: {r.string}")
        seasons[r.string] = {"url": baseUrl + r["href"]}

    allVersions[versionKey]["seasons"] = seasons

# Relocate results from previous run
if os.path.isfile("data/step1_results.json"):
    os.rename(
        "data/step1_results.json",
        f"archived/step1_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/step1_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
with open(fName, "w") as f:
    print("\nWriting step 1 results to file " + fName)
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()

print("\nDone!")
