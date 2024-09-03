Task link text on episode page

---

DIV ID=aboutTask (ASSUMED EXISTS AND UNIQUE)

    h1 (ASSUMED UNIQUE)
    ASSUMPTION: Task page heading will match Task link heading

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
