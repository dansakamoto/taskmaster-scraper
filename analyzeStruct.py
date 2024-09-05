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
                print(task["url"] + "\n")
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
                # soup2 = soup.find("div", {"class": "description"})
                soup2 = soup.find_all("div", {"id": "aboutTask"})

                # TEST ASSUMPTIONS --------

                print("Testing assumption: number of divs with ID=aboutTask == 1")
                print("count: " + str(len(soup2)))
                if len(soup2) != 1:
                    print(
                        "EXCEPTION FOUND: unexpected number of divs with id=aboutTask"
                    )
                    exit()

                children = soup2[0].findChildren(recursive=False)

                print("Testing assumption: aboutTask has 5 or 6 children")
                print("count: " + str(len(children)))
                if len(children) != 5 and len(children) != 6:
                    print("EXCEPTION FOUND: unexpected number of children in aboutTask")
                    exit()

                print("Testing assumption: child 0 is an h1")
                print("tag: " + children[0].name)
                if children[0].name != "h1":
                    print("EXCEPTION FOUND: child 0 is wrong type")
                    exit()

                print("Testing assumption: child 1 is an image of id=coverImage")
                print("tag: " + children[1].name + ", id: " + children[1]["id"])
                if children[1].name != "img":
                    print("EXCEPTION FOUND: child 1 is wrong type")
                    exit()
                if children[1]["id"] != "coverImage":
                    print("EXCEPTION FOUND: child 1 is wrong id")
                    exit()

                print("Testing assumption: child 2 is a div of id=infoBelowTitle")
                print("tag: " + children[2].name + ", id: " + children[2]["id"])
                if children[2].name != "div":
                    print("EXCEPTION FOUND: child 2 is wrong type")
                    exit()
                if children[2]["id"] != "infoBelowTitle":
                    print("EXCEPTION FOUND: child 2 is wrong id")
                    exit()

                print("Testing assumption: child 3 is a div of class=description")
                print(
                    "tag: " + children[3].name + ", class: " + children[3]["class"][0]
                )
                if children[3].name != "div":
                    print("EXCEPTION FOUND: child 3 is wrong type")
                    exit()
                if children[3]["class"][0] != "description":
                    print("EXCEPTION FOUND: child 3 is wrong class")
                    exit()

                if len(children) == 5:
                    print(
                        "Testing assumption: child 5 out of 5 is a div of id=navLinks"
                    )
                    print("tag: " + children[4].name + ", id: " + children[4]["id"])
                    if children[4].name != "div":
                        print("EXCEPTION FOUND: child 4 is wrong type")
                        exit()
                    if children[4]["id"] != "navLinks":
                        print("EXCEPTION FOUND: child 4 is wrong id")
                        exit()

                if len(children) == 6:
                    print("Testing assumption: child 5 out of 6 is a div of id=notes")
                    print("tag: " + children[4].name + ", id: " + children[4]["id"])
                    if children[4].name != "div":
                        print("EXCEPTION FOUND: child 4 is wrong type")
                        exit()
                    if children[4]["id"] != "notes":
                        print("EXCEPTION FOUND: child 4 is wrong id")
                        exit()

                    print(
                        "Testing assumption: child 6 out of 6 is a div of id=navLinks"
                    )
                    print("tag: " + children[5].name + ", id: " + children[5]["id"])
                    if children[5].name != "div":
                        print("EXCEPTION FOUND: child 5 is wrong type")
                        exit()
                    if children[4]["id"] != "navLinks":
                        print("EXCEPTION FOUND: child 5 is wrong id")
                        exit()

                print("Testing assumption: h1 text len > 0")
                print(
                    "text: " + children[0].text + ", len: " + str(len(children[0].text))
                )
                if len(children[0].text) == 0:
                    print("EXCEPTION FOUND: h1 has no text")
                    exit()

                infoBelowTitle = children[2]

                print("Testing assumption: infoBelowTitle has 3 or 4 children")
                print("count: " + str(len(infoBelowTitle)))
                if len(infoBelowTitle) != 3 and len(infoBelowTitle) != 4:
                    print(
                        "EXCEPTION FOUND: unexpected number of children in infoBelowTitle"
                    )
                    exit()

                # all of infoBelowTitle children are div of class=infoTableRow
                # each child has two children, a div of class=rowLead, followed by a div of class=rowValue

                # child 0 rowLead text = "Task types:"
                # child 0 rowValue has one child - a div of class=taskTypes
                # taskTypes has at least one child, all children are div of class=taskType, each contains a span of class=taskTypeText, taskTypeText text len > 0
                print(
                    "Testing assumption: infoBelowTitle child 0 = Task types, contains list of task types"
                )

                e = 0
                for k, v in infoBelowTitle:
                    if (
                        k.name != "div"
                        or k["class"][0] != "rowLead"
                        or k.text != "Task types:"
                    ):
                        print("EXCEPTION: unexpected key in infoBelowTitle")
                        exit()
                    if v.name != "div" or v["class"][0] != "rowValue":
                        print("EXCEPTION: unexpected value in infoBelowTitle")
                        exit()

                    for infoTableRow in v:
                        print(infoTableRow.)

                        exit()
                        """if len(v1) == 0:
                            print("EXCEPTION: no task types found")
                            exit()
                        for tt in v1:
                            if tt.name != "div" or tt["class"][0] != "taskType":
                                print("EXCEPTION in taskTypes list")
                                exit()
                            tts = tt.find("span")
                            print(tts)"""

                    e += 1

                exit()

                taskTypes = infoBelowTitle
                if (
                    taskTypes["class"][0] != "infoTableRow"
                    or len(taskTypes != 2)
                    or taskTypes[0]["class"][0] != "rowLead"
                    or taskTypes[1]["class"][0] != "rowValue"
                    or taskTypes[0].text != "Task types:"
                    or len(taskTypes[1]) != 1
                    or taskTypes[1][0].name != "div"
                    or taskTypes[1][0]["class"][0] != "taskTypes"
                    or len(taskTypes[1][0]) == 0
                ):
                    print("EXCEPTION FOUND in infoBelowTitle")
                    exit()
                taskTypes = taskTypes[1][0]
                for tt in taskTypes:
                    if (
                        tt.name != "div"
                        or tt["class"][0] != "taskType"
                        or len(tt) != 1
                        or tt[0].name != "span"
                        or len(tt[0]) == 0
                    ):
                        print("EXCEPTION FOUND in a task type")
                        exit()

                # child 1 rowLead text = "Mastertasks:"
                # child 1 rowValue has at least one anchor child - both anchor text and href len are > 0

                # child 2 rowLead text = "Locations:"
                # child 2 rowValue has at least one anchor child - both anchor text and href len are > 0

                # child 3 rowLead text= "Spaces:" (optional)
                # child 3 rowValue has at least one anchor child - both anchor text and href len are > 0

                # description assumptions
                # exactly 3 children
                # child 0 = h1, text len > 0
                # child 1 = p, text len > 0
                # child 2 = blockquote of class=taskBrief, text len > 0

                # notes assumptions
                # if notes exists, has exactly 2 children
                # child 0 = h2, text len > 0
                # child 1 = ul
                # ul has at least one child, all children are li, li text len > 0

                print("All assumptions passed")
                exit()

                if len(children) != 5:
                    print(
                        "exception found: div aboutTask has an unexpected number of children"
                    )
                    exit()

                test = children[0]
                if test.name != "h1" or test.text == None or test.text == "":
                    print("exception found in child 0 (h1)")
                    exit()

                test = children[1]
                if test.name != "img" or test.get("id") != "coverImage":
                    print("exception found in child 1 (img)")
                    exit()

                test = children[2]
                if test.name != "div" or test.get("id") != "infoBelowTitle":
                    print("exception found in child 2 (div)")
                    exit()

                test = children[3]
                if (
                    test.name != "div"
                    or len(test.get("class")) != 1
                    or test.get("class")[0] != "description"
                ):
                    print("exception found in child 3 (div)")
                    exit()

                test = children[4]
                if test.name != "div" or test.get("id") != "navLinks":
                    print("exception found in child 4 (div)")
                    exit()

                # soup3 = soup2.find("div", {"class": "description"})

                test = children[2]
                infoBelowTitle = test.findChildren(recursive=False)

                if len(infoBelowTitle) != 3:
                    print(
                        "exception: infoBelowTitle has an unexpected number of children"
                    )
                    exit()

                for i in range(3):
                    test = infoBelowTitle[i]
                    if (
                        test.name != "div"
                        or len(test.get("class")) != 1
                        or test.get("class")[0] != "infoTableRow"
                    ):
                        print("exception found in infoBelowTitle children")
                        exit()

                # TASK TYPES
                test = infoBelowTitle[0].findChildren(recursive=False)
                if len(test) != 2:
                    print(
                        "exception: infoBelowTitle[0] has an unexpeted number of children"
                    )
                    exit()

                if (
                    test[0].name != "div"
                    or test[0].get("class")[0] != "rowLead"
                    or test[0].text != "Task types:"
                ):
                    print("exception in Task types rowLead")
                    exit()

                test = test[1]
                if test.name != "div" or test.get("class")[0] != "rowValue":
                    print("exception in Task types rowValue")
                    exit()

                test = test.findChildren(recursive=False)
                if len(test) != 1:
                    print(
                        "exception: unexpected number of children Task types rowValue"
                    )
                    exit()

                test = test[0]
                if test.name != "div" or test.get("class")[0] != "taskTypes":
                    print("exception in div taskTypes")
                    exit()

                taskTypes = test.findChildren(recursive=False)
                for taskType in taskTypes:
                    if taskType.name != "div" or taskType.get("class")[0] != "taskType":
                        print("exception found in one of the task types")
                        exit()
                    tt = taskType.findChildren(recursive=False)
                    tt = tt[1]
                    if tt.name != "span" or tt.get("class")[0] != "taskTypeText":
                        print("exception found in span of one of the taskTypes")
                        exit()
                    print(tt.text)

                # MASTERTASK SECTION
                test = infoBelowTitle[1]
                test = test.findChildren(recursive=False)

                if len(test) <= 1:
                    print("exception: Mastertasks section has too few children")
                    exit()

                if (
                    test[0].name != "div"
                    or test[0].get("class")[0] != "rowLead"
                    or test[0].text != "Mastertasks:"
                ):
                    print("exception found in Mastertasks")
                    exit()

                for i in range(1, len(test)):
                    if test[i].name != "div" or test[i].get("class")[0] != "rowValue":
                        print("exception found in one of the mastertasks")
                        exit()
                    mt = test[i].findChildren(recursive=False)
                    if len(mt) != 1:
                        print("exception: a mastertask has too many children")
                        exit()
                    mt = mt[0]
                    if (
                        mt.name != "a"
                        or mt["href"] is None
                        or mt["href"] == ""
                        or mt.text is None
                        or mt.text == ""
                    ):
                        print(
                            "exception: something is wrong with a link to a mastertask"
                        )
                        exit()
                    print(f"mastertask url: {mt['href']}")
                    print(f"mastertask text: {mt.text}")

                # TASK LOCATIONS
                test = infoBelowTitle[2]
                test = test.findChildren(recursive=False)
                if len(test) <= 1:
                    print("exception: locations section has too few children")
                    exit()

                if (
                    test[0].name != "div"
                    or test[0].get("class")[0] != "rowLead"
                    or test[0].text != "Locations:"
                ):
                    print(
                        "exception: something is wrong with locations section rowLead"
                    )
                    exit()

                for i in range(1, len(test)):
                    if test[i].name != "div" or test[1].get("class")[0] != "rowValue":
                        print(
                            "exception: something is wrong with a child in the locations section"
                        )
                        exit()
                    xy = test[i]
                    xy = xy.findChildren(recursive=False)
                    if len(xy) != 1:
                        print("exception: a location element has too many children")
                        exit()
                    xy = xy[0]
                    if (
                        xy.name != "a"
                        or xy["href"] == None
                        or xy["href"] == ""
                        or xy.text == None
                        or xy.text == ""
                    ):
                        print("exception: something is wrong with a location's link")
                        exit()
                    print(f"location url: {xy['href']}")
                    print(f"location name: {xy.text}")

                # TASK DESCRIPTION
                test = children[3]
                descriptionDiv = test.findChildren(recursive=False)
                if len(descriptionDiv) != 3:
                    print("exception: unexpected number of children in description div")
                    exit()

                test = descriptionDiv[0]
                if test.name != "h2" or test.text != "Task brief":
                    print("exception in description h2")
                    exit()

                test = descriptionDiv[1]
                if (
                    test.name != "p"
                    or test.text != "The brief for the task is as follows:"
                ):
                    print("exception in description p")
                    exit()

                test = descriptionDiv[2]
                if (
                    test.name != "blockquote"
                    or test.get("class")[0] != "taskBrief"
                    or test.text == None
                    or test.text == ""
                ):
                    print("exception: unexpected format in task brief")
                    exit()

                print("\n" + test.text)

                """
                EXPECTATIONS
                Children = {
                    h1
                    img id="coverImage"
                    div id="infoBelowTitle" {
                        div class="infoTableRow" { 
                            div class="rowLead" innerHTML="Task types:"
                            div class="rowValue" {
                                div class="taskTypes" {
                                    >=1 x div class="taskType" {
                                        img
                                        span class="taskTypeText" ! record innerHTML to dict !
                                    }
                                }
                            }
                        }
                        div class="infoTableRow" {
                            div class="rowLead" innerHTML="Mastertasks"
                            >=1 x div class="rowValue" {
                                a href=(is not blank) innerHTML = (is not blank)
                            }
                        }
                        div class="infoTableRow" {
                            div class="rowLead" innerHTML="Locations"
                            >=1 x div class="rowValue" {
                                a href=(is not blank) innerHTML = (is not blank)
                            }

                        }
                    }
                    div class="description" {
                        h2 innerHTML = "Task brief"
                        p innerHTML = "The brief for the task is as follows:"
                        blockquote class="taskBrief" innerHTML= "::before(NOTBLANK)::after"
                    }
                    div id="navLinks"
                }
                """

                """
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

exit()

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
