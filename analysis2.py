from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# Load results from previous step
existingData = f"data/cleanup_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

taskCount = 0

elements = {}

# Iterate through all attempts, find attempt descriptions
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            for taskKey, task in episode["tasks"].items():
                taskCount = taskCount + 1
                soup = BeautifulSoup(task["description"], "html.parser")

                child = soup.findChild()
                while child:
                    name = child.name
                    if "id" in child.attrs:
                        name += " id: " + child.attrs["id"]
                    elif "class" in child.attrs:
                        name += " class: " + child.attrs["class"][0]

                    if name not in elements:
                        elements[name] = 1
                    else:
                        elements[name] = elements[name] + 1

                    child = child.findNextSibling()


print("Total Tasks: " + str(taskCount))

for k, v in elements.items():
    print(str(k) + ": " + str(v))
