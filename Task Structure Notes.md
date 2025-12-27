Task link text on episode page

---

DIV ID=aboutTask (ASSUMED EXISTS AND UNIQUE)

    h1 (ASSUMED UNIQUE)
    ASSUMPTION: Task page heading will match Task link heading

    img (ASSUMED UNIQUE)

    DIV ID=infoBelowTitle (ASSUMED EXISTS AND UNIQUE)

        Task types (list of categories) (ASSUMED EXISTS AND UNIQUE)
        Mastertasks: one or more names/links (ASSUMED EXISTS, >= 1 ITEM)
        Locations: one or more names/links (ASSUMED EXISTS, >= 1 ITEM)
        Spaces: one or more names/,links (ASSUMED EXISTS, >= 1 ITEM)

        ASSUMPTION: no other elements inside infoBelowTitle

    DIV class=description (ASSUMED EXISTS AND UNIQUE)

        Task brief (ASSUMED EXISTS AND UNIQUE)
        Blockquote taskBrief (ASSUMED EXISTS AND UNIQUE)

    DIV id=notes (ASSUMED EXISTS AND UNIQUE)

        ul of task notes (ASSUMED EXISTS AND UNIQUE)

    ASSUMPTION: no other elements inside aboutTask

---

briefIntro (first p)

Array - 1 or more briefs
briefNote (optional, p class)
taskBrief (blockquote, class)

TaskNotes

if ul - task notes
if p class: callToAction - no notes
one exception to check: https://taskmaster.info/task.php?id=4177

https://taskmaster.info/task.php?id=4177
