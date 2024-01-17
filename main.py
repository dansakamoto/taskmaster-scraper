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
attempts = 0
attemptLimit = 5

# load base URL
req = Request(rootUrl, headers=headers)
html_page = urlopen(req).read()
soup = BeautifulSoup(html_page, "lxml")

allSeasons = {}

# DEBUG
skipTo = 4
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
        print("\nScanning season: " + k)
        req = Request(s["url"], headers=headers)
        html_page = None
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
            sleep(random.uniform(2, 5))
            print("\nScanning episode: " + episode["title"])
            req = Request(episode["url"], headers=headers)
            html_page = None
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
            soup2 = soup.select(
                "#tasks > div.task > div.taskInfo > div.taskCardTaskTitle > h3.taskLink > a"
            )
            tasks = []
            for item in soup2:
                print(f"found task: {item.string}\nurl: {item['href']}")
                tasks.append({"title": item.string, "url": baseUrl + item["href"]})
            episode["tasks"] = tasks

"""
STEP 4: collect task data
"""
if skipTo <= 4:
    for skey, svalue in allSeasons.items():
        for episode in svalue["episodes"]:
            for task in episode["tasks"]:
                sleep(random.uniform(2, 5))
                print("\nScanning task: " + task["title"])
                req = Request(task["url"], headers=headers)
                html_page = None
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
                soup2 = soup.find("div", {"class": "description"})
                children = soup2.findChildren()
                taskBriefs = []
                newBrief = {}
                hrFlag = False
                for c in children:
                    for br in c.findAll("br"):
                        br.replace_with("\n")
                    classes = c.get("class")
                    if (
                        classes != None
                        and classes[0] != "taskBrief"
                        and classes[0] != "briefNote"
                    ):
                        print("ERROR: unkown class found: " + classes[0])
                        exit()
                    if hrFlag:
                        if c.name == "hr":
                            hrFlag = False
                            continue
                        elif classes != None and (
                            classes[0] == "briefNote" or classes[0] == "taskBrief"
                        ):
                            print("ERROR! Funky task structure")
                            exit()
                    if c.name == "p" and classes != None and classes[0] == "briefNote":
                        newBrief["briefNote"] = c.string
                    elif (
                        c.name == "blockquote"
                        and classes != None
                        and classes[0] == "taskBrief"
                    ):
                        newBrief["taskBrief"] = c.text
                        taskBriefs.append(newBrief)
                        newBrief = {}
                        hrFlag = True
                print(taskBriefs[0]["taskBrief"])
                task["description"] = taskBriefs

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
