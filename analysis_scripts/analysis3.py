from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# Load results from previous step
existingData = f"data/cleanup_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

elements = {}

# Iterate through all attempts, find attempt descriptions
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            for taskKey, task in episode["tasks"].items():
                if "notes" not in task:
                    continue

                soup = BeautifulSoup(task["description"], "html.parser")

                struct = ""
                soup = soup.find("p")

                if str(soup) not in elements:
                    elements[str(soup)] = 1
                else:
                    elements[str(soup)] += 1


for k, v in elements.items():
    if v > 10:
        print(v)
        print(k)
