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

    return SOURCES, load, mo, pd, provenance_table, to_num


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 2 — Where data comes from: relevance and recency

    Before you join anything, you need to know what each source **is**: who published it, what one row
    means (its *grain*), which column links it to other files (its *join key*), and **what time period
    its numbers describe**. That last one is the trap: a file downloaded today can describe 2021.

    This notebook reads every source the course offers and builds a **source card** for each, with the
    periods computed from the data itself — not from the file name or the web page.

    **Your deliverable:** choose 2–3 sources for your aggregator and fill in a **provenance record**
    for each (form at the bottom).
    """)
    return


@app.cell(hide_code=True)
def _(load):
    data = {name: load(name) for name in ["hospitals", "unplanned_visits", "hrrp", "places", "acs_measures", "crosswalk"]}
    return (data,)


@app.cell(hide_code=True)
def _(SOURCES, data, pd):
    def cms_period(df):
        """Earliest Start Date to latest End Date, read from the file."""
        start = pd.to_datetime(df["Start Date"], format="%m/%d/%Y", errors="coerce")
        end = pd.to_datetime(df["End Date"], format="%m/%d/%Y", errors="coerce")
        return f"{start.min():%m/%Y} – {end.max():%m/%Y}"

    def years(df):
        return ", ".join(sorted(df["year"].unique()))

    period = {
        "hospitals": "no period column (a current snapshot: who the hospitals are now)",
        "unplanned_visits": f"{cms_period(data['unplanned_visits'])} overall — but DIFFERENT per measure (see below)",
        "hrrp": cms_period(data["hrrp"]),
        "places": f"data year {years(data['places'])} (2025 release)",
        "acs_measures": f"{years(data['acs_measures'])} (5-year average)",
        "crosswalk": "no period (built by the course from hospital county names)",
    }
    cards = pd.DataFrame([
        dict(source=SOURCES[n]["title"], publisher=SOURCES[n]["publisher"], grain=SOURCES[n]["grain"],
             join_key=SOURCES[n]["key"], reporting_period=period[n], rows=len(data[n]),
             source_page=SOURCES[n]["page"], name=n)
        for n in data
    ])
    return cards, cms_period


@app.cell(hide_code=True)
def _(cards, mo):
    def _card(r):
        return mo.callout(mo.md(f"""
    **{r.source}**

    | | |
    |---|---|
    | Publisher | {r.publisher} |
    | Grain (one row is…) | {r.grain} |
    | Join key | {r.join_key} |
    | Reporting period (from the data) | {r.reporting_period} |
    | Rows | {r.rows:,} |
    | Source page | [{r.source_page}]({r.source_page}) |
    """), kind="neutral")

    mo.vstack([
        mo.md("## Source cards"),
        mo.ui.tabs({r.name: _card(r) for r in cards.itertuples()}),
    ])
    return


@app.cell(hide_code=True)
def _(cms_period, data, mo, pd, to_num):
    _u = data["unplanned_visits"].assign(numeric=lambda d: to_num(d["Score"]).notna())
    by_measure = (
        _u.groupby("Measure ID")
        .apply(lambda g: pd.Series({
            "period": cms_period(g),
            "hospitals": g["Facility ID"].nunique(),
            "numeric scores": int(g["numeric"].sum()),
            "not numeric": int((~g["numeric"]).sum()),
        }), include_groups=False)
        .reset_index()
        .sort_values(["period", "Measure ID"])
    )
    _hwr = by_measure[by_measure["Measure ID"] == "Hybrid_HWR"].iloc[0]
    _nper = by_measure["period"].nunique()
    mo.vstack([
        mo.md(f"""
    ## Lesson 1 — one file, {_nper} different periods

    *Unplanned Hospital Visits* holds {by_measure.shape[0]} measures. They do **not** share a time window.
    If you put two of them side by side, you are comparing different years.
    """),
        mo.ui.table(by_measure, selection=None, page_size=20),
        mo.callout(mo.md(
            f"**Hybrid_HWR** ({_hwr['period']}) has **{_hwr['numeric scores']} numeric scores** out of "
            f"{_hwr['hospitals']:,} hospitals. The measure is in the file, but there is nothing to analyse. "
            "A source can be present and still be empty."), kind="warn"),
    ])
    return (by_measure,)


@app.cell(hide_code=True)
def _(by_measure, cms_period, data, mo):
    _hrrp = cms_period(data["hrrp"])
    _readm = by_measure.loc[by_measure["Measure ID"] == "READM_30_HF", "period"].iloc[0]
    mo.md(f"""
    ## Lesson 2 — "readmissions" from two CMS files are not the same years

    - **HRRP** (the readmissions *penalty* program): **{_hrrp}**
    - **Unplanned visits, READM_30_HF**: **{_readm}**

    Both are CMS, both say "30-day heart-failure readmission". The HRRP window is **older**. If your
    question is about *now*, the newer file is more relevant; if it is about *penalties*, HRRP is the one
    that matters even though it is older. Relevance depends on your question.
    """)
    return


@app.cell(hide_code=True)
def _(data, mo):
    _p_years = ", ".join(sorted(data["places"]["year"].unique()))
    _a_years = ", ".join(sorted(data["acs_measures"]["year"].unique()))
    _p_states = set(data["places"]["stateabbr"])
    _a_states = set(data["acs_measures"]["stateabbr"])
    _only_acs = ", ".join(sorted(_a_states - _p_states)) or "none"
    mo.md(f"""
    ## Lesson 3 — release year is not data year

    - **CDC PLACES** is the *2025 release*, but its `year` column says **{_p_years}**. These are
      model-based **estimates** of the share of adults with a condition, not counts of patients.
    - **ACS measures** say **{_a_years}**: a five-year average that ended years before your hospital data.
    - PLACES covers **{len(_p_states)}** state codes; the ACS file covers **{len(_a_states)}**.
      In the ACS file but **not** in this PLACES county file: **{_only_acs}**. Check the PLACES
      source page before you assume why — and before you assume your state is there.
    """)
    return


@app.cell(hide_code=True)
def _(data, mo, pd):
    _p = data["places"]
    _a = data["acs_measures"]
    _x = data["crosswalk"]
    _ct = pd.concat([
        _p[_p["stateabbr"] == "CT"][["locationid", "locationname"]].drop_duplicates().assign(file="PLACES 2025"),
        _a[_a["stateabbr"] == "CT"][["locationid", "locationname"]].drop_duplicates().assign(file="ACS 2017–2021"),
    ])
    _fair = _x[(_x["State"] == "CT") & (_x["County/Parish"] == "FAIRFIELD")]
    _fips = ", ".join(sorted(_fair["county_fips"].unique()))
    _in_places = _fair["county_fips"].isin(_p["locationid"]).sum()
    _ct_h = _x[_x["State"] == "CT"]
    _ct_join = _ct_h["county_fips"].isin(_p["locationid"]).sum()
    mo.vstack([
        mo.md(f"""
    ## Lesson 4 — Fairfield is in Connecticut, and Connecticut changed its map

    PLACES 2025 reports Connecticut as **{(_ct['file'] == 'PLACES 2025').sum()} planning regions**; the ACS file
    still uses the **{(_ct['file'] == 'ACS 2017–2021').sum()} old counties**. The course crosswalk puts the
    {len(_fair)} hospitals in Fairfield County at FIPS **{_fips}** — and **{_in_places} of them** find a match
    in PLACES. Of all {len(_ct_h)} Connecticut hospitals, **{_ct_join}** match PLACES.

    A county join for a Fairfield student would quietly drop every Connecticut hospital. Nothing errors.
    The rows are just gone. That is why week 3 counts rows after every join.
    """),
        mo.ui.table(_ct, selection=None, page_size=20),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(mo.md(r"""
    **Ask your AI** — when you look at a source this notebook doesn't cover:

    ```text
    I have a pandas DataFrame `df` loaded from a public health CSV (all columns are text).
    Write a cell that tells me: the number of rows; which columns look like IDs or join keys;
    any date or year columns and the earliest and latest value in each; and, for every column,
    how many values are blank or say things like "Not Available" or "Suppressed".
    Do not convert missing values to zero.
    ```

    Then check one of its answers by hand: open the source page and find the same period there.
    """), kind="info")
    return


@app.cell(hide_code=True)
def _(cards, mo):
    pick = mo.ui.multiselect(
        options={r.source: r.name for r in cards.itertuples()},
        value=["CMS Hospital General Information", "CMS Unplanned Hospital Visits"],
        label="Sources for my aggregator (choose 2–3)",
        max_selections=3,
    )
    mo.vstack([
        mo.md(r"""
    ## Your deliverable: a provenance record per source

    Choose your sources. The facts the data can tell us are filled in for you — **check them**. The
    judgement fields are yours. (Changing the selection clears the form, so choose first.)
    The full template, with guidance for each field, is
    [`../templates/provenance_record.md`](../templates/provenance_record.md).
    """),
        pick,
    ])
    return (pick,)


@app.cell(hide_code=True)
def _(cards, mo, pick):
    import datetime as _dt

    _today = _dt.date.today().isoformat()

    def _form(r):
        return mo.ui.dictionary({
            "Publisher": mo.ui.text(value=r.publisher, full_width=True),
            "Source page": mo.ui.text(value=r.source_page, full_width=True),
            "Grain": mo.ui.text(value=r.grain, full_width=True),
            "Join key": mo.ui.text(value=r.join_key, full_width=True),
            "Reporting period": mo.ui.text(value=r.reporting_period, full_width=True),
            "Rows": mo.ui.text(value=f"{r.rows:,}", full_width=True),
            "Retrieved": mo.ui.text(value=f"{_today} via the course mirror", full_width=True),
            "Why it is relevant to my question": mo.ui.text_area(full_width=True),
            "Is it recent enough? Why": mo.ui.text_area(full_width=True),
            "Known gaps (suppression, missing places, changed definitions)": mo.ui.text_area(full_width=True),
            "What I checked myself": mo.ui.text_area(full_width=True),
        })

    _rows = cards.set_index("name")
    forms = mo.ui.dictionary({_rows.loc[n, "source"]: _form(_rows.loc[n].rename(n)) for n in pick.value})
    forms
    return (forms,)


@app.cell(hide_code=True)
def _(forms, mo):
    def _record(title, fields):
        lines = [f"## Provenance record: {title}", ""]
        lines += [f"- **{k}:** {v.strip() or '(to fill in)'}" for k, v in fields.items()]
        return "\n".join(lines)

    record_md = "\n\n".join(_record(t, f) for t, f in forms.value.items())
    mo.vstack([
        mo.md("### Your records (copy this into your submission)"),
        mo.ui.code_editor(value=record_md, language="markdown", disabled=True),
        mo.download(data=record_md.encode("utf-8"), filename="provenance_records.md", label="Download as .md"),
    ]) if record_md else mo.md("*Choose at least one source above.*")
    return


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([mo.md("## Where these numbers came from"), mo.ui.table(provenance_table(), selection=None)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** a provenance record for each of your 2–3 chosen sources, every field filled in.
    Submit your AI transcript with it.

    **The one check to run:** for one source, open its source page and confirm the reporting period
    yourself. Does it match what the data says? If not, write down which one you believe and why.

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
