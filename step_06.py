from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
import random, json, time, os

# Load results from previous step
existingData = f"data/step5_results.json"
with open(existingData, "r") as f:
    allVersions = json.load(f)
    f.close()

# Iterate through all attempts, find attempt descriptions
for versionKey, version in allVersions.items():
    for seasonKey, season in version["seasons"].items():
        for episodeKey, episode in season["episodes"].items():
            if "taskmasterIntro" in episode:
                episode["taskmasterIntro"] = (
                    episode["taskmasterIntro"]
                    .replace("<blockquote>", "")
                    .replace("</blockquote>", "")
                )
            if "assistantIntro" in episode:
                episode["assistantIntro"] = (
                    episode["assistantIntro"]
                    .replace("<blockquote>", "")
                    .replace("</blockquote>", "")
                )
            if "taskmasterSignoff" in episode:
                episode["taskmasterSignoff"] = (
                    episode["taskmasterSignoff"]
                    .replace("<blockquote>", "")
                    .replace("</blockquote>", "")
                )

            for taskKey, task in episode["tasks"].items():
                soup = BeautifulSoup(task["description"], "html.parser")

                taskTypes = soup.find_all("span", {"class": "taskTypeText"})
                task["taskTypes"] = []
                for t in taskTypes:
                    task["taskTypes"].append(t.string)

                taskNotes = soup.find("div", {"id": "notes"})
                if taskNotes:
                    taskNotes = taskNotes.find("ul")
                    if taskNotes != None:
                        taskNotes = taskNotes.find_all("li")
                        task["notes"] = []
                        for n in taskNotes:
                            task["notes"].append(
                                str(n).replace("<li>", "").replace("</li>", "")
                            )

                td = soup.find("div", {"class", "description"})

                exploded = {}
                exploded["briefIntro"] = (
                    str(td.find("p")).replace("<p>", "").replace("</p>", "")
                )
                exploded["taskBriefs"] = []

                td = soup.find_all(
                    ["blockquote", "p"], {"class": ["briefNote", "taskBrief"]}
                )

                briefNote = ""
                for res in td:
                    if res.name == "p" and res.attrs["class"][0] == "briefNote":
                        briefNote = (
                            str(res)
                            .replace('<p class="briefNote">', "")
                            .replace("</p>", "")
                        )
                    elif (
                        res.name == "blockquote"
                        and res.attrs["class"][0] == "taskBrief"
                    ):
                        brief = (
                            str(res)
                            .replace('<blockquote class="taskBrief">', "")
                            .replace("</blockquote>", "")
                        )
                        briefObj = {}
                        if briefNote != "":
                            briefObj["briefNote"] = briefNote
                        briefObj["brief"] = brief

                        exploded["taskBriefs"].append(briefObj)
                        briefNote = ""

                task["description"] = exploded

                if "attempts" in task:
                    for attempt in task["attempts"]:
                        if "attemptTitle" in attempt:
                            attempt["attemptTitle"] = attempt["attemptTitle"][
                                attempt["attemptTitle"].find(">") + 1 :
                            ].replace("</a>", "")

                        if "contestants" in attempt:
                            for k, v in attempt["contestants"].items():
                                if "url" in v:
                                    if v["url"].find("https") == -1:
                                        v["url"] = "https://taskmaster.info" + v["url"]

                        attempt["description"] = (
                            attempt["description"]
                            .replace('<div id="description">', "")
                            .replace("</div>", "")
                            .replace("<li>", "")
                            .replace("</li>", "")
                        )

                        index = attempt["description"].find(
                            '<p><span class="subCredit">'
                        )
                        if index != -1:
                            attempt["description"] = attempt["description"][:index]


# Relocate results from previous run
if os.path.isfile("data/final_results.json"):
    os.rename(
        "data/final_results.json",
        f"archived/final_results_moved-{time.time()}.json",
    )

# Write results to file
fName = f"data/final_results.json"
os.makedirs(os.path.dirname(fName), exist_ok=True)
print("\nWriting final results to file " + fName)
with open(fName, "w") as f:
    f.write(json.dumps(allVersions, indent=2, ensure_ascii=False))
    f.close()

print("\nDone!")
