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
existingData = f"data/step3_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

# Iterate through all tasks, find task data and attempts lists
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            for taskKey, task in episode["tasks"].items():
                sleep(random.uniform(0.5, 2))
                print("\nScanning task: " + taskKey)
                print(task["url"] + "\n")
                req = Request(task["url"], headers=headers)
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
                soup2 = soup.find("div", {"id": "aboutTask"})
                print(f"found task description for task: " + taskKey)
                task["description"] = str(soup2)

                attempts = []

                soup2 = soup.select("#attempts > div.attempt > p.attemptTitle > a")
                if len(soup2) > 0:
                    for item in soup2:
                        print(f"found attempt: {item.string}\nurl: {item['href']}")
                        attempts.append(
                            {"attemptTitle": item.string, "url": baseUrl + item["href"]}
                        )

                soup2 = soup.select("#attemptList > ul > li")
                if len(soup2) > 0:
                    for item in soup2:
                        print(f"found attempt: {item.string}\n(No URL)")
                        attempts.append({"description": item.string})

                if len(attempts) > 0:
                    task["attempts"] = attempts


# Relocate results from previous run
if os.path.isfile("data/step4_results.json"):
    os.rename(
        "data/step4_results.json",
        f"archived/step4_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/step4_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting step 4 results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()

print("\nDone!")
