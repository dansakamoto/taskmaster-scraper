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
existingData = f"data/step2_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

# Iterate through all episodes, find task lists
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            sleep(random.uniform(0.5, 2))
            print("\nScanning episode: " + episodeKey)
            req = Request(episode["url"], headers=headers)
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

            soup2 = soup.select_one("#taskmaster-intro > blockquote")
            if soup2 != None:
                episode["taskmasterIntro"] = soup2.string

            soup2 = soup.select_one("#assistant-intro > blockquote")
            if soup2 != None:
                episode["assistantIntro"] = soup2.string

            soup2 = soup.select_one("#taskmaster-signoff > blockquote")
            if soup2 != None:
                episode["taskmasterSignoff"] = soup2.string

            soup2 = soup.select(
                "#tasks > div.task > div.taskInfo > div.taskCardTaskTitle > h3.taskLink > a"
            )
            tasks = {}
            for item in soup2:
                print(f"found task: {item.string}\nurl: {item['href']}")
                tasks[item.string] = {"url": baseUrl + item["href"]}

            if tasks != {}:
                episode["tasks"] = tasks


# Cleanup episodes without tasks, then seasons without episodes
for versionKey in list(allVersions):
    for seasonKey in list(allVersions[versionKey]["seasons"]):
        for episodeKey in list(
            allVersions[versionKey]["seasons"][seasonKey]["episodes"]
        ):
            if (
                "tasks"
                not in allVersions[versionKey]["seasons"][seasonKey]["episodes"][
                    episodeKey
                ]
            ):
                del allVersions[versionKey]["seasons"][seasonKey]["episodes"][
                    episodeKey
                ]
        if allVersions[versionKey]["seasons"][seasonKey]["episodes"] == {}:
            del allVersions[versionKey]["seasons"][seasonKey]

# Relocate results from previous run
if os.path.isfile("data/step3_results.json"):
    os.rename(
        "data/step3_results.json",
        f"archived/step3_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/step3_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting step 3 results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()
print("\nDone!")
