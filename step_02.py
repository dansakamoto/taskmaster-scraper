from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# Load config
configFile = f"config.json"
with open(configFile, "r") as f:
    config = json.load(f)
    baseUrl = config["baseUrl"]
    headers = config["headers"]
    attemptLimit = config["attemptLimit"]
    f.close()

# Load results from previous step
existingData = f"data/step1_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

# Iterate through all seasons, find episode lists
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        sleep(random.uniform(0.5, 2))
        print("\nScanning season: " + seasonKey)
        req = Request(season["url"], headers=headers)
        html_page = None
        attempts = 0
        while html_page == None:
            try:
                html_page = urlopen(req).read()
            except:
                attempts += 1
                if attempts >= attemptLimit:
                    input(
                        "Too many page load errors, pausing execution. Press enter to resume..."
                    )
                    attempts = 0
                print("Error loading page, retrying...")
                sleep(10)
            finally:
                attempts = 0
        soup = BeautifulSoup(html_page, "html.parser")
        soup2 = soup.select("#episodes")
        isSpecial = len(soup2) == 0

        episodes = {}
        isAired = True
        if isSpecial:
            soup2 = soup.select("#tasks")
            isAired = len(soup2) > 0
            if not isAired:
                print("(unaired...)")
                continue
            print("(it's a special)")
            episodes["_special"] = {"url": season["url"]}
        else:
            soup = soup.select("#episodes > div.episode > p.episodeTitle > a")
            for a in soup:
                print(f"found episode: {a.string}")
                episodes[a.string] = {"url": baseUrl + a["href"]}
        if isAired:
            allVersions[versionKey]["seasons"][seasonKey]["episodes"] = episodes

# Cleanup seasons without episodes
for versionKey in list(allVersions):
    for seasonKey in list(allVersions[versionKey]["seasons"]):
        if "episodes" not in allVersions[versionKey]["seasons"][seasonKey]:
            del allVersions[versionKey]["seasons"][seasonKey]

# Relocate results from previous run
if os.path.isfile("data/step2_results.json"):
    os.rename(
        "data/step2_results.json",
        f"archived/step2_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/step2_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting step 2 results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()

print("\nDone!")
