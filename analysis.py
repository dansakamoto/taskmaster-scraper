from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# Load results from previous step
existingData = f"data/final_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

elements = []

# Iterate through all attempts, find attempt descriptions
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            for taskKey, task in episode["tasks"].items():
                for t in task["taskTypes"]:
                    if t not in elements:
                        elements.append(t)


res = ""
for e in elements:
    res += '"' + e + '" | '

res = res[:-3]
print(res)
