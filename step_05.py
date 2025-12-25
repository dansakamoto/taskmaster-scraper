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
existingData = f"data/step4_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

# Iterate through all attempts, find attempt descriptions
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            for taskKey, task in episode["tasks"].items():
                for attempt in task["attempts"]:
                    sleep(random.uniform(0.5, 2))
                    if attempt["url"] == None:
                        print("No URL found, skipping...")
                        continue
                    print("\nScanning attempt: " + attempt["attemptTitle"])
                    print("URL found: " + attempt["url"] + "\n")
                    req = Request(attempt["url"], headers=headers)
                    html_page = None
                    loadAttempts = 0
                    while html_page == None:
                        try:
                            html_page = urlopen(req).read()
                        except:
                            loadAttempts += 1
                            if loadAttempts >= attemptLimit:
                                input(
                                    "Too many page load errors, pausing execution. Press enter to resume..."
                                )
                                loadAttempts = 0
                            print("Error loading page, retrying...")
                            sleep(10)
                        finally:
                            loadAttempts = 0
                    soup = BeautifulSoup(html_page, "html.parser")
                    soup2 = soup.find("div", {"id": "description"})
                    print(f"found description for attempt: " + attempt["attemptTitle"])
                    attempt["description"] = str(soup2)

                    contestants = {}
                    soup2 = soup.select(
                        "#contestants > div.contestant > p.personName > a"
                    )
                    if len(soup2) > 0:
                        for item in soup2:
                            print(f"found contestant: {str(item)}\nurl: {item['href']}")
                            contestants[str(item)] = {"url": item["href"]}
                        attempt["contestants"] = contestants


# Relocate results from previous run
if os.path.isfile("data/step5_results.json"):
    os.rename(
        "data/step5_results.json",
        f"archived/step5_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/step5_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting step 5 results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()

print("\nDone!")
