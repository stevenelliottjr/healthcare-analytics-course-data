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
            loaded_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"), rows=len(df), columns=df.shape[1]))
        return df

    def to_num(s: pd.Series) -> pd.Series:
        """Text -> number. Anything that is not a number ('Not Available', 'N/A', 'Too Few to Report', '')
        becomes missing, never zero."""
        return pd.to_numeric(s, errors="coerce")

    def provenance_table() -> pd.DataFrame:
        return pd.DataFrame(PROVENANCE)
    return load, mo, pd, provenance_table, to_num


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 6 — Validate the use; how an app is built

    A number can be correctly sourced (week 4) and correctly defended (week 5) and still be **the wrong number
    for the question**. This week you ask: *fit for what purpose, for whom?*

    **First half:** whose population does your measure cover, which hospitals are missing and why, and what
    happens when county data is attached to hospitals. You end with your **data card**.

    **Second half:** how a marimo notebook becomes an app, and a **one-screen sketch** of the app you'll build.
    """)
    return


@app.cell(hide_code=True)
def _(load):
    hospitals = load("hospitals")
    uv = load("unplanned_visits")
    hrrp = load("hrrp")
    crosswalk = load("crosswalk")
    places = load("places")
    return crosswalk, hospitals, hrrp, places, uv


@app.cell(hide_code=True)
def _(hrrp, mo, uv):
    _opts = {f"Unplanned Visits · {m}": ("uv", m) for m in sorted(uv["Measure ID"].unique())}
    _opts.update({f"HRRP · {m}": ("hrrp", m) for m in sorted(hrrp["Measure Name"].unique())})
    measure_pick = mo.ui.dropdown(_opts, value="Unplanned Visits · READM_30_HF", label="The measure at the heart of your layer",
                                  searchable=True, full_width=True)
    measure_pick
    return (measure_pick,)


@app.cell(hide_code=True)
def _(hospitals, hrrp, measure_pick, pd, to_num, uv):
    _src, _m = measure_pick.value
    if _src == "uv":
        _rows, _vcol, measure_name = uv[uv["Measure ID"] == _m], "Score", uv.loc[uv["Measure ID"] == _m, "Measure Name"].iloc[0]
    else:
        _rows, _vcol, measure_name = hrrp[hrrp["Measure Name"] == _m], "Excess Readmission Ratio", _m
    rows_m = _rows.assign(has_number=to_num(_rows[_vcol]).notna())
    # One row per hospital in the general-information file: is it in the measure file? does it have a number?
    cov = hospitals[["Facility ID", "Facility Name", "State", "Hospital Type"]].merge(
        rows_m[["Facility ID", "has_number", _vcol, "Footnote"]], on="Facility ID", how="left", indicator=True)
    cov["status"] = "not in the measure file"
    cov.loc[cov["_merge"] == "both", "status"] = "in file, no number"
    cov.loc[cov["has_number"].eq(True), "status"] = "has a number"
    funnel = pd.DataFrame({
        "step": ["Hospitals in CMS Hospital General Information", "…with a row for this measure", "…with a number for this measure"],
        "hospitals": [len(hospitals), int((cov["_merge"] == "both").sum()), int((cov["status"] == "has a number").sum())]})
    not_in_general = int((~rows_m["Facility ID"].isin(hospitals["Facility ID"])).sum())
    why_missing = (rows_m.loc[~rows_m["has_number"], _vcol].value_counts().rename_axis("text in the file")
                   .reset_index(name="hospitals"))
    foot_missing = (rows_m.loc[~rows_m["has_number"], "Footnote"].replace("", "(none)").value_counts()
                    .rename_axis("footnote code").reset_index(name="hospitals"))
    value_col = _vcol
    return cov, foot_missing, funnel, measure_name, not_in_general, rows_m, value_col, why_missing


@app.cell(hide_code=True)
def _(foot_missing, funnel, measure_name, mo, not_in_general, rows_m, why_missing):
    _n, _k = funnel["hospitals"].iloc[0], funnel["hospitals"].iloc[2]
    mo.vstack([
        mo.md(f"""
    ## 1. Whose population, and which hospitals are missing

    **Measure:** {measure_name} · period {rows_m['Start Date'].iloc[0]} to {rows_m['End Date'].iloc[0]}

    **Whose patients?** The file does not say which patients are counted (age, insurance, diagnosis rules).
    That lives in the measure definition on the CMS source page — **check the measure definition** and write
    what it says on your data card, with the link. Do not let an AI tool fill this in from memory.

    **Which hospitals?** Of {_n:,} hospitals in the general file, only **{_k:,} ({_k / _n:.0%})** have a number
    for this measure. {f"Also, {not_in_general:,} hospitals in the measure file are not in the general file." if not_in_general else ""}
    """),
        mo.ui.table(funnel, selection=None),
        mo.hstack([
            mo.vstack([mo.md("**What the file says instead of a number**"), mo.ui.table(why_missing, selection=None)]),
            mo.vstack([mo.md("**Footnote codes on those rows** (look each up in CMS's footnote list)"),
                       mo.ui.table(foot_missing, selection=None)]),
        ], widths=[1, 1], gap=2),
    ])
    return


@app.cell(hide_code=True)
def _(cov, mo, pd):
    import altair as alt
    _t = (cov.groupby("Hospital Type")["status"].value_counts().unstack(fill_value=0))
    _t["hospitals"] = _t.sum(axis=1)
    _t["share with a number"] = (_t.get("has a number", 0) / _t["hospitals"]).round(3)
    by_type = _t.reset_index().sort_values("hospitals", ascending=False)
    _s = cov.groupby("State")["status"].apply(lambda s: (s == "has a number").mean()).rename("share with a number")
    by_state = pd.concat([cov.groupby("State").size().rename("hospitals"), _s.round(3)], axis=1).reset_index()
    _chart = alt.Chart(by_type).mark_bar(color="#5b8db8").encode(
        x=alt.X("share with a number:Q", axis=alt.Axis(format="%"), title="share of hospitals with a number"),
        y=alt.Y("Hospital Type:N", sort="-x", title=None),
        tooltip=["Hospital Type", "hospitals", "share with a number"]).properties(width=480, height=200)
    mo.vstack([
        mo.md("## 2. Coverage by hospital type and state\nA layer that covers acute-care hospitals well may say "
              "nothing about critical-access, psychiatric or children's hospitals. Your data card must say which."),
        _chart,
        mo.ui.table(by_type, selection=None),
        mo.md("**By state** (sort by clicking a column header): which states would your app describe poorly?"),
        mo.ui.table(by_state, selection=None, page_size=8),
    ])
    return alt, by_state, by_type


@app.cell(hide_code=True)
def _(crosswalk, mo, places):
    _matched = crosswalk[crosswalk["county_fips"] != ""]
    _no_places = _matched[~_matched["county_fips"].isin(places["locationid"])]
    _gap_states = _no_places["State"].value_counts()
    _gap_txt = ", ".join(f"{k} {v:,}" for k, v in _gap_states.head(5).items())
    _per = _matched.groupby(["county_fips", "county_name_census", "State"]).size().sort_values(ascending=False)
    _top = _per.index[0]
    _multi = int((_per > 1).sum())
    mo.md(f"""
    ## 3. County data attached to hospitals: the ecological fallacy

    If your layer joins a **county** measure (CDC PLACES, ACS) to **hospitals**, every hospital in a county
    gets the *same* county value. In the course crosswalk, **{_per.iloc[0]} hospitals** sit in
    {_top[1]}, {_top[2]} (FIPS {_top[0]}), and {_multi:,} counties have more than one hospital.

    A county value describes **people who live in the county** — it is a fact about a place, not about any
    hospital's patients. So "hospitals in high-poverty counties have higher readmissions" is a statement
    about counties. It does **not** show that poorer *patients* are readmitted more, and it can't tell you
    anything about one patient. Saying otherwise is the ecological fallacy. Patients also cross county lines.

    **Coverage gap to put on your data card:** {len(_no_places):,} hospitals that have a county FIPS get **no**
    CDC PLACES 2025 value at all, because their county code is not in the PLACES file (by state: {_gap_txt}).
    Find out why before you explain it — don't guess.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    card_q = mo.ui.text_area(label="What question can this layer answer? (one sentence)", rows=2, full_width=True)
    card_who = mo.ui.text_area(label="For whom? Which patients (from the measure definition — cite it), which hospitals, which period",
                               rows=3, full_width=True)
    card_not = mo.ui.text_area(label="What can it NOT answer? (at least three things)", rows=3, full_width=True)
    card_use = mo.ui.text_area(label="Who should use it, and for what decision? Who should not?", rows=2, full_width=True)
    mo.vstack([mo.md("## 4. Your data card\nFill in the boxes; the computed facts are added for you. "
                     "The full template is [`../templates/data_card.md`](../templates/data_card.md)."),
               card_q, card_who, card_not, card_use])
    return card_not, card_q, card_use, card_who


@app.cell(hide_code=True)
def _(by_type, card_not, card_q, card_use, card_who, funnel, measure_name, mo, rows_m):
    def _or(box):
        return box.value.strip() or "*(write this yourself)*"
    _k, _n = funnel["hospitals"].iloc[2], funnel["hospitals"].iloc[0]
    _best = by_type.sort_values("share with a number", ascending=False).iloc[0]
    _worst = by_type.sort_values("share with a number").iloc[0]
    mo.md("\n\n".join([
        "### Data card — DRAFT",
        f"**Measure:** {measure_name} · **Period:** {rows_m['Start Date'].iloc[0]} to {rows_m['End Date'].iloc[0]}",
        f"**Question it can answer:** {_or(card_q)}",
        f"**For whom:** {_or(card_who)}",
        f"**Coverage (computed):** {_k:,} of {_n:,} hospitals have a number ({_k / _n:.0%}). Best covered type: "
        f"{_best['Hospital Type']} ({_best['share with a number']:.0%}); least: {_worst['Hospital Type']} "
        f"({_worst['share with a number']:.0%}).",
        f"**What it cannot answer:** {_or(card_not)}",
        f"**Intended use / not for:** {_or(card_use)}",
    ]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. How an app is built and published

    A marimo app is just a notebook with **controls** (`mo.ui.…`) and **outputs** that depend on them. When a
    control changes, marimo re-runs every cell that uses it — nothing else. That's the whole idea.

    Below is a complete tiny app in **two cells**. The code is shown because reading it is the lesson:

    - Cell 1 makes a control. `mo.ui.dropdown(...)` builds the menu; the last line (`state`) displays it.
    - Cell 2 uses `state.value` — whatever the user picked. Because it mentions `state`, marimo re-runs it on
      every change. It filters to that state, counts hospitals by type, and draws a bar chart with altair.
      The title says how many rows are behind the chart — always show that.
    """)
    return


@app.cell
def _(hospitals, mo):
    state = mo.ui.dropdown(sorted(hospitals["State"].unique()), value="CT", label="State")
    state
    return (state,)


@app.cell
def _(alt, hospitals, state):
    picked = hospitals[hospitals["State"] == state.value]
    counts = picked["Hospital Type"].value_counts().rename_axis("type").reset_index(name="hospitals")
    alt.Chart(counts).mark_bar().encode(
        x="hospitals:Q", y=alt.Y("type:N", sort="-x", title=None)
    ).properties(title=f"Hospitals in {state.value} by type ({len(picked)} rows)", width=420)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Publishing.** The same file runs as an app with the code hidden: locally, `marimo run your_notebook.py`
    opens it in the browser in app view. To share it as a link, follow the publishing steps in this week's
    brief. Before you share: does every chart say how many rows are behind it, and does the app show where its
    data came from?

    /// admonition | Ask your AI — start your app
    > *"In a marimo notebook, my data layer is a DataFrame called `layer` with columns ______. Build a
    > one-screen app: one `mo.ui.dropdown` for ______ and one chart (altair) that shows ______. Put the number
    > of rows behind the chart in the chart title. Do not convert 'Not Available' to zero. Explain each line."*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    sk_user = mo.ui.text(label="Who is the user?", full_width=True)
    sk_q = mo.ui.text(label="The one question they come with", full_width=True)
    sk_controls = mo.ui.text(label="Controls (what they can pick)", full_width=True)
    sk_out = mo.ui.text(label="Main output (chart or table)", full_width=True)
    sk_num = mo.ui.text(label="The one number you'll defend on screen", full_width=True)
    sk_warn = mo.ui.text(label="The warning the app must show (from your data card)", full_width=True)
    mo.vstack([mo.md("## 6. Your one-screen app sketch"), sk_user, sk_q, sk_controls, sk_out, sk_num, sk_warn])
    return sk_controls, sk_num, sk_out, sk_q, sk_user, sk_warn


@app.cell(hide_code=True)
def _(mo, sk_controls, sk_num, sk_out, sk_q, sk_user, sk_warn):
    def _or(box):
        return box.value.strip() or "…"
    mo.callout(mo.md("\n\n".join([
        f"**App for:** {_or(sk_user)} · **Question:** {_or(sk_q)}",
        f"**[ Controls ]** {_or(sk_controls)}",
        f"**[ Main output ]** {_or(sk_out)}",
        f"**[ Headline number ]** {_or(sk_num)}",
        f"**[ Warning line ]** {_or(sk_warn)}",
        "**[ Footer ]** Where these numbers came from (provenance table) · link to data card",
    ])), kind="neutral")
    return


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([mo.md("## Where these numbers came from"), mo.ui.table(provenance_table(), selection=None)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** (1) your data card (what it can answer, for whom, what it cannot), and (2) a one-screen
    sketch of the app you will build — this page's box, a photo of a paper sketch, or a slide. Submit your AI
    transcript with it.

    **The one check to run:** open the measure definition and confirm the patient population you wrote under
    "For whom". If you can't confirm it, write "not confirmed".

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
