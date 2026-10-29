import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    # --- Course setup (canonical copy: course/notebooks/_setup_cell.py). Do not edit. ---
    import datetime as dt
    import io
    import json
    import os
    import urllib.request
    from pathlib import Path

    import pandas as pd

    CACHE = Path("data")
    CACHE.mkdir(exist_ok=True)
    # Course mirror on GitHub: a dated snapshot of every file the course uses.
    MIRROR = "https://raw.githubusercontent.com/stevenelliottjr/healthcare-analytics-course-data/main/data"
    # Date each mirror folder was last refreshed from its publisher. Update these when you refresh the mirror.
    MIRROR_SNAPSHOT = {"cms": "2026-10-26", "cdc": "2026-10-29", "course": "2026-10-29"}
    # For testing before files are pushed: point this at a local folder laid out like the mirror.
    LOCAL_MIRROR = os.environ.get("COURSE_DATA_LOCAL")
    UA = {"User-Agent": "healthcare-analytics-course/1.0"}

    # Every source the course offers. 'mirror' is the path under MIRROR; 'live' is tried first when set.
    SOURCES = {
        "hospitals": dict(
            title="CMS Hospital General Information", publisher="Centers for Medicare & Medicaid Services",
            dataset_id="xubh-q36u", grain="one row per hospital", key="Facility ID (CMS Certification Number)",
            page="https://data.cms.gov/provider-data/dataset/xubh-q36u", mirror="cms/cms_hospital_general_info.csv"),
        "unplanned_visits": dict(
            title="CMS Unplanned Hospital Visits", publisher="Centers for Medicare & Medicaid Services",
            dataset_id="632h-zaca", grain="one row per hospital x measure", key="Facility ID + Measure ID",
            page="https://data.cms.gov/provider-data/dataset/632h-zaca", mirror="cms/cms_unplanned_visits.csv"),
        "hrrp": dict(
            title="CMS Hospital Readmissions Reduction Program", publisher="Centers for Medicare & Medicaid Services",
            dataset_id="9n3s-kdb3", grain="one row per hospital x condition", key="Facility ID + Measure Name",
            page="https://data.cms.gov/provider-data/dataset/9n3s-kdb3", mirror="cms/cms_hrrp.csv"),
        "places": dict(
            title="CDC PLACES: County Data, 2025 release", publisher="Centers for Disease Control and Prevention",
            dataset_id="swc5-untb", grain="one row per county x measure x value type", key="locationid (5-digit county FIPS)",
            page="https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb",
            mirror="cdc/cdc_places_county.csv"),
        "acs_measures": dict(
            title="CDC Non-Medical Factor Measures for County, ACS 2017-2021", publisher="Centers for Disease Control and Prevention (from Census ACS 5-year)",
            dataset_id="i6u4-y3g4", grain="one row per county x measure", key="locationid (5-digit county FIPS)",
            page="https://data.cdc.gov/d/i6u4-y3g4", mirror="cdc/cdc_acs_county_measures.csv"),
        "crosswalk": dict(
            title="Course crosswalk: hospital to county FIPS", publisher="DATA 6900 (built from CMS county names + CDC county list)",
            dataset_id="course", grain="one row per hospital", key="Facility ID -> county_fips",
            page="https://github.com/stevenelliottjr/healthcare-analytics-course-data", mirror="course/hospital_county_crosswalk.csv"),
    }

    PROVENANCE = []  # one record per load; shown in every notebook

    def _fetch(url, timeout=300):
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()

    def load(name: str) -> pd.DataFrame:
        """Load a course source by name. Everything is read as TEXT: IDs keep leading zeros and
        'Not Available' stays visible instead of silently becoming a blank. Records provenance."""
        src = SOURCES[name]
        path = CACHE / Path(src["mirror"]).name
        how = "local cache"
        if not path.exists():
            if LOCAL_MIRROR:
                path.write_bytes((Path(LOCAL_MIRROR) / src["mirror"]).read_bytes())
                how = "local test mirror"
            else:
                path.write_bytes(_fetch(f"{MIRROR}/{src['mirror']}"))
                how = "course mirror (GitHub)"
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        PROVENANCE.append(dict(
            source=src["title"], publisher=src["publisher"], dataset_id=src["dataset_id"], grain=src["grain"],
            join_key=src["key"], source_page=src["page"], obtained_from=how,
            mirror_snapshot=MIRROR_SNAPSHOT.get(src["mirror"].split("/")[0], "see the course mirror README"),
            loaded_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"), rows=len(df), columns=df.shape[1]))
        return df

    def to_num(s: pd.Series) -> pd.Series:
        """Text -> number. Anything that is not a number ('Not Available', 'N/A', 'Too Few to Report', '')
        becomes missing, never zero."""
        return pd.to_numeric(s, errors="coerce")

    def provenance_table() -> pd.DataFrame:
        return pd.DataFrame(PROVENANCE)

    return load, mo, pd, provenance_table


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 1 — Your first chart, and what the human is for

    Tonight you make **one chart from one CMS file**, publish it as a link a classmate can open,
    and write down **the question you want your aggregator to answer** this term.

    You do not need to write code. Pick options with the controls below. When you want something
    the notebook doesn't do yet, use an **Ask your AI** box: copy the prompt into the AI tool of your
    choice, paste its code into a new cell, and then check its answer against the numbers on screen.

    *Data rule from day one: only public, aggregate data goes into any AI tool. No patient data,
    no passwords.*
    """)
    return


@app.cell(hide_code=True)
def _(load):
    hospitals = load("hospitals")
    return (hospitals,)


@app.cell(hide_code=True)
def _(hospitals, mo):
    _n = len(hospitals)
    _na = int((hospitals["Hospital overall rating"] == "Not Available").sum())
    _states = hospitals["State"].nunique()
    mo.md(f"""
    ## The file: CMS *Hospital General Information*

    One row per hospital: **{_n:,} hospitals** across **{_states}** states and territories.
    Each has a type (acute care, critical access, psychiatric, …), an ownership, and a CMS
    **overall star rating** from 1 to 5.

    One thing to notice before you chart anything: **{_na:,} of {_n:,} hospitals
    ({_na / _n:.0%}) have no star rating** — the file says "Not Available". A chart that quietly
    drops those hospitals tells a different story from one that shows them. In this course they are
    always shown as their own category.
    """)
    return


@app.cell(hide_code=True)
def _(hospitals, mo):
    state_pick = mo.ui.dropdown(
        options=["All states"] + sorted(hospitals["State"].unique()),
        value="CT",
        label="State",
    )
    group_pick = mo.ui.dropdown(
        options={
            "Overall star rating": "Hospital overall rating",
            "Hospital type": "Hospital Type",
            "Ownership": "Hospital Ownership",
        },
        value="Overall star rating",
        label="Count hospitals by",
    )
    mo.hstack([state_pick, group_pick], justify="start", gap=2)
    return group_pick, state_pick


@app.cell(hide_code=True)
def _(group_pick, hospitals, mo, pd, state_pick):
    import altair as alt

    _col = group_pick.value
    _sub = hospitals if state_pick.value == "All states" else hospitals[hospitals["State"] == state_pick.value]
    counts = _sub[_col].replace("", "(blank)").value_counts().rename_axis("category").reset_index(name="hospitals")
    counts["share"] = counts["hospitals"] / counts["hospitals"].sum()
    counts["missing"] = counts["category"].isin(["Not Available", "(blank)"])

    if _col == "Hospital overall rating":
        _order = [c for c in ["1", "2", "3", "4", "5", "Not Available", "(blank)"] if c in set(counts["category"])]
    else:
        _order = list(counts.sort_values("hospitals", ascending=False)["category"])

    _where = "all states" if state_pick.value == "All states" else state_pick.value
    chart = (
        alt.Chart(counts)
        .mark_bar(cornerRadiusEnd=4, size=18)
        .encode(
            y=alt.Y("category:N", sort=_order, title=None),
            x=alt.X("hospitals:Q", title="Number of hospitals"),
            color=alt.Color(
                "missing:N",
                scale=alt.Scale(domain=[False, True], range=["#2a78d6", "#8f8d87"]),
                legend=alt.Legend(title="Value reported?", labelExpr="datum.value == 'true' ? 'No (Not Available)' : 'Yes'"),
            ),
            tooltip=[
                alt.Tooltip("category:N", title=group_pick.selected_key),
                alt.Tooltip("hospitals:Q", title="Hospitals"),
                alt.Tooltip("share:Q", title="Share", format=".0%"),
            ],
        )
        .properties(title=f"Hospitals in {_where} by {group_pick.selected_key.lower()} (n = {len(_sub):,})", width="container", height=alt.Step(26))
    )
    mo.vstack([
        chart,
        mo.md(f"**Rows behind this chart:** {len(_sub):,} hospitals (after filtering to {_where}). "
              f"The bars add up to {int(counts['hospitals'].sum()):,} — nothing was dropped."),
        mo.accordion({"Show the numbers as a table": mo.ui.table(counts[["category", "hospitals", "share"]], selection=None)}),
    ])
    return (counts,)


@app.cell(hide_code=True)
def _(counts, group_pick, mo, state_pick):
    _miss = counts.loc[counts["missing"], "hospitals"].sum()
    _tot = counts["hospitals"].sum()
    _msg = (
        f"In your current view, **{_miss:,} of {_tot:,} hospitals ({_miss / _tot:.0%})** have no value for "
        f"*{group_pick.selected_key.lower()}*. If you removed them, every other bar's share would go up — "
        "and nobody reading your chart would know."
        if _miss
        else f"In your current view every hospital has a value for *{group_pick.selected_key.lower()}*. "
        "Try **Overall star rating** to see the missing ones."
    )
    mo.callout(mo.md(f"**Read your chart before you publish it.** {_msg}  \n"
                     f"Write one sentence you could defend about {state_pick.value}: what does the chart show, and what can't it tell you?"),
               kind="warn")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(mo.md(r"""
    **Ask your AI** — copy this prompt, paste the code it gives you into a new cell below.

    ```text
    I have a marimo notebook with a pandas DataFrame called `hospitals` (CMS Hospital General
    Information; every column is text). Add a cell that makes an Altair bar chart of
    "Hospital overall rating" for hospitals where "Emergency Services" is "Yes", shown next to
    the same chart for "No". Keep "Not Available" as its own bar - do not drop it or turn it
    into zero. Print the number of rows in each group before charting.
    ```

    Then check it: do the two groups' row counts add up to the total in the file?
    """), kind="info")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Publish it as a link

    Your deliverable is a link a classmate can open and see your chart — without installing anything.

    1. Open this notebook in **molab** (marimo's free hosted notebooks) if you aren't already there.
    2. Set the dropdowns to the view you want to show.
    3. Use molab's **share / publish** option to get a link. If you are unsure which setting makes it
       viewable by others, ask in the class channel or check molab's own help page.
    4. **Test the link** in a private/incognito browser window, or send it to a classmate and ask what they see.
       If they can't open it, it isn't published yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    question = mo.ui.text_area(
        label="The one question I want my aggregator to answer this term:",
        placeholder="e.g. Do hospitals in counties with higher diabetes rates have higher heart-failure readmissions?",
        full_width=True,
        rows=3,
    )
    mo.vstack([
        mo.md(r"""
    ## Your question for the term

    Over the next weeks you will join several public sources into one **aggregator** — a data layer
    you can defend. Start with the question it should answer. Keep it to one sentence, about places
    or hospitals (not individual patients).
    """),
        question,
    ])
    return (question,)


@app.cell(hide_code=True)
def _(mo, question):
    _q = question.value.strip()
    mo.md(f"> **My question:** {_q}" if _q else "> *(Your question will appear here once you type it.)*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is the human for?

    An AI tool can write the code for this chart in seconds. It cannot decide whether "Not Available"
    belongs on the chart, whether your question is worth asking, or whether you are willing to put your
    name on the result. **Your job in this course is those decisions:** choosing what to count, checking
    the numbers, and saying out loud what you would and would not sign.
    """)
    return


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([mo.md("## Where these numbers came from"), mo.ui.table(provenance_table(), selection=None)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** (1) a link to your published chart that a classmate has opened, and (2) your one-sentence
    question for the term. Submit your AI transcript with it.

    **The one check to run:** do your bars add up to the "rows behind this chart" number? If not, something
    was dropped — find out what.

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
