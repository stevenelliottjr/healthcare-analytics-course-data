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
    return (
        CACHE,
        LOCAL_MIRROR,
        MIRROR,
        PROVENANCE,
        Path,
        UA,
        dt,
        load,
        mo,
        pd,
        provenance_table,
        to_num,
        urllib,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 4 — Verify the sourcing

    Last week you built a joined layer. This week you prove where its numbers came from.

    **Part A — trace three numbers.** Pick a hospital and a measure. The notebook shows the number as it
    would sit in your layer *next to* the exact source row it came from: which file, which line, which column,
    which reporting period. Then it shows a state average and every row that went into it. Do this three times.

    **Part B — find the planted errors.** We give you a copy of the hospital file that someone "cleaned"
    badly. Several kinds of error are hidden in it. The notebook gives you tools, not answers: you find them,
    count them, and say what each one would break.

    *Why this matters:* an AI tool can produce a confident average in seconds. Only you can say "I opened the
    source row and it matches."
    """)
    return


@app.cell(hide_code=True)
def _(load):
    hospitals = load("hospitals")
    uv = load("unplanned_visits")
    hrrp = load("hrrp")
    return hospitals, hrrp, uv


@app.cell(hide_code=True)
def _(CACHE, LOCAL_MIRROR, MIRROR, PROVENANCE, Path, UA, dt, pd, urllib):
    # Extra loader for the practice file with planted errors (Part B). It sits at the ROOT of the course
    # mirror, not under cms/. Same caching rule as the setup cell: download once, read everything as text.
    _name = "lab03_hospitals.csv"
    _path = CACHE / _name
    _how = "local cache"
    if not _path.exists():
        if LOCAL_MIRROR:
            _path.write_bytes((Path(LOCAL_MIRROR) / _name).read_bytes())
            _how = "local test mirror"
        else:
            _req = urllib.request.Request(f"{MIRROR}/{_name}", headers=UA)
            with urllib.request.urlopen(_req, timeout=300) as _r:
                _path.write_bytes(_r.read())
            _how = "course mirror (GitHub)"
    planted = pd.read_csv(_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    PROVENANCE.append(dict(
        source="Practice file with planted errors (copy of CMS Hospital General Information)",
        publisher="DATA 6900 (altered on purpose)", dataset_id="course", grain="should be one row per hospital",
        join_key="Facility ID", source_page=f"{MIRROR}/{_name}", obtained_from=_how,
        loaded_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"), rows=len(planted), columns=planted.shape[1]))
    return (planted,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Part A — Trace a number back to its source row

    Choose a file, a state and a hospital, then a measure and a column. Everything below updates.
    """)
    return


@app.cell(hide_code=True)
def _(hospitals, mo):
    source_pick = mo.ui.radio(
        options=["Unplanned Hospital Visits", "Hospital Readmissions Reduction Program (HRRP)"],
        value="Unplanned Hospital Visits", label="Source file")
    _states = sorted(hospitals["State"].unique())
    state_pick = mo.ui.dropdown(_states, value="CT" if "CT" in _states else _states[0], label="State", searchable=True)
    mo.hstack([source_pick, state_pick], justify="start", gap=2)
    return source_pick, state_pick


@app.cell(hide_code=True)
def _(hrrp, mo, source_pick, state_pick, uv):
    if source_pick.value.startswith("Unplanned"):
        src_df, src_file, measure_col = uv, "cms_unplanned_visits.csv", "Measure ID"
        value_cols = ["Score", "Denominator", "Number of Patients"]
    else:
        src_df, src_file, measure_col = hrrp, "cms_hrrp.csv", "Measure Name"
        value_cols = ["Excess Readmission Ratio", "Predicted Readmission Rate", "Expected Readmission Rate",
                      "Number of Discharges", "Number of Readmissions"]
    _here = src_df[src_df["State"] == state_pick.value]
    _opts = dict(sorted({f"{n} ({i})": i for i, n in zip(_here["Facility ID"], _here["Facility Name"])}.items()))
    hospital_pick = mo.ui.dropdown(_opts, value=next(iter(_opts)) if _opts else None,
                                   label=f"Hospital ({len(_opts)} in this file for {state_pick.value})", searchable=True)
    _measures = sorted(src_df[measure_col].unique())
    _default = next((m for m in ("READM_30_HF", "READM-30-HF-HRRP") if m in _measures), _measures[0])
    measure_pick = mo.ui.dropdown(_measures, value=_default,
                                  label="Measure", searchable=True)
    column_pick = mo.ui.dropdown(value_cols, value=value_cols[0], label="Column")
    mo.vstack([hospital_pick, mo.hstack([measure_pick, column_pick], justify="start", gap=2)])
    return column_pick, hospital_pick, measure_col, measure_pick, src_df, src_file


@app.cell(hide_code=True)
def _(column_pick, hospital_pick, measure_col, measure_pick, mo, pd, src_df, src_file, state_pick, to_num):
    _col = column_pick.value
    _rows = src_df[(src_df["Facility ID"] == hospital_pick.value) & (src_df[measure_col] == measure_pick.value)]
    if hospital_pick.value is None or _rows.empty:
        trace_md = "*This hospital has no row for this measure in this file. Pick another — that absence is itself worth noting.*"
        _out = mo.md(trace_md)
    else:
        _r = _rows.iloc[0]
        _line = int(_rows.index[0]) + 2  # +1 for the header line, +1 because spreadsheet lines start at 1
        _raw = _r[_col]
        _num = to_num(pd.Series([_raw])).iloc[0]
        _layer = f"**{_num:g}**" if pd.notna(_num) else f"**missing** (the file says `{_raw or '(blank)'}`; it stays missing, never 0)"
        _foot = _r.get("Footnote", "") or "(none)"
        # The aggregate: state average of the same measure and column, from numeric rows only
        _st = src_df[(src_df["State"] == state_pick.value) & (src_df[measure_col] == measure_pick.value)].copy()
        _st["value as number"] = to_num(_st[_col])
        _used = _st["value as number"].notna()
        _avg = _st.loc[_used, "value as number"].mean()
        _avg_txt = f"{_avg:.3g}" if _used.any() else "cannot be computed (no numeric rows)"
        trace_md = (
            f"- **Number in my layer:** {_num:g}\n" if pd.notna(_num) else f"- **Number in my layer:** missing (`{_raw}`)\n"
        ) + (
            f"- **Source:** {src_file}, line {_line}, column \"{_col}\", raw text `{_raw}`\n"
            f"- **Hospital / measure:** {_r['Facility Name']} ({_r['Facility ID']}), {measure_pick.value}\n"
            f"- **Reporting period:** {_r['Start Date']} to {_r['End Date']} · footnote: {_foot}\n"
            f"- **State average ({state_pick.value}):** {_avg_txt}, from {int(_used.sum())} of {len(_st)} rows "
            f"({int((~_used).sum())} rows were not numbers and were left out)\n"
        )
        _st.insert(0, "line in file", _st.index + 2)
        _out = mo.vstack([
            mo.hstack([
                mo.md(f"### The number in your layer\n{_layer}\n\n"
                      f"### State average ({state_pick.value})\n**{_avg_txt}**  \n"
                      f"from {int(_used.sum())} numeric rows out of {len(_st)}; "
                      f"{int((~_used).sum())} rows were text such as 'Not Available' and were left out."),
                mo.md(f"### The source row\n| | |\n|---|---|\n| File | `{src_file}` |\n| Line in file | {_line} |\n"
                      f"| Column | {_col} |\n| Raw text in the file | `{_raw or '(blank)'}` |\n"
                      f"| Measure | {measure_pick.value} |\n| Period | {_r['Start Date']} to {_r['End Date']} |\n"
                      f"| Footnote | {_foot} |"),
            ], widths=[1, 1], gap=2),
            mo.md("**Every row behind the state average** (open the CSV at these line numbers to check any one):"),
            mo.ui.table(_st[["line in file", "Facility ID", "Facility Name", _col, "value as number",
                             "Start Date", "End Date"]], selection=None, page_size=8),
            mo.md("**Copy this into your deliverable** (one per number you trace):"),
            mo.md(f"```\n{trace_md}```"),
        ])
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Ask your AI — trace a number from *your* layer
    Paste this, then check the answer by opening the file yourself:

    > *"In my marimo notebook I have a joined table called `layer`. For the row where Facility ID is ______,
    > add a cell that shows, for the column ______, the original row in the source file it came from: the
    > file name, the line number in the CSV (index + 2), the raw text before any conversion to a number, and
    > the Start Date and End Date. Do not change any values. Print the row count of the source file too."*

    Then open the CSV (Excel, a text editor, or the source page) at that line. Does it say the same thing?
    ///
    """)
    return


@app.cell(hide_code=True)
def _(hospitals, mo, planted):
    mo.md(f"""
    ## Part B — Find the planted errors

    `lab03_hospitals.csv` is a copy of CMS *Hospital General Information* that someone altered. The clean
    file (`hospitals`) is the trusted source. The practice file has **{len(planted):,}** rows; the clean file
    has **{len(hospitals):,}**. That gap is the first clue, but not the only problem.

    Use the five tools below. For each problem you find, write down: **what is wrong, how many rows, how you
    found it, and what it would break** in an analysis (a count, a join, a filter, an average).
    """)
    return


@app.cell(hide_code=True)
def _(hospitals, mo, pd, planted):
    _t = pd.DataFrame({
        "file": ["practice file (planted)", "clean CMS file"],
        "rows": [len(planted), len(hospitals)],
        "distinct Facility IDs": [planted["Facility ID"].nunique(), hospitals["Facility ID"].nunique()],
        "rows that are exact copies of another row": [int(planted.duplicated().sum()), int(hospitals.duplicated().sum())],
    })
    mo.vstack([mo.md("### Tool 1 — Row counts"), mo.ui.table(_t, selection=None)])
    return


@app.cell(hide_code=True)
def _(mo, planted):
    _d = planted[planted["Facility ID"].duplicated(keep=False)].sort_values("Facility ID")
    mo.vstack([
        mo.md(f"### Tool 2 — Facility IDs that appear more than once\n"
              f"{len(_d):,} rows share their Facility ID with another row. "
              "Are they true copies, or two different hospitals? Look at the other columns."),
        mo.ui.table(_d, selection=None, page_size=6),
    ])
    return


@app.cell(hide_code=True)
def _(hospitals, mo):
    pattern_col = mo.ui.dropdown(list(hospitals.columns), value="Facility ID", label="Column to profile", searchable=True)
    mo.vstack([
        mo.md("""### Tool 3 — Format check
    Each value is turned into its *shape*: every digit becomes `9`, every capital letter `A`, every lowercase
    letter `a` (other characters stay). So `06103` → `99999` and `CT` → `AA`. A column that should have one
    shape but shows several is suspicious. Compare the two files."""),
        pattern_col,
    ])
    return (pattern_col,)


@app.cell(hide_code=True)
def _(hospitals, mo, pattern_col, pd, planted):
    def _shape(s):
        return s.str.replace(r"[0-9]", "9", regex=True).str.replace(r"[A-Z]", "A", regex=True).str.replace(r"[a-z]", "a", regex=True)
    _c = pattern_col.value
    _p = pd.concat([_shape(planted[_c]).value_counts().rename("practice file"),
                    _shape(hospitals[_c]).value_counts().rename("clean file")], axis=1).fillna(0).astype(int)
    _p = _p.reset_index(names="shape").sort_values("practice file", ascending=False)
    mo.vstack([mo.md(f"{len(_p)} different shapes in **{_c}** (top 25 shown)."),
               mo.ui.table(_p.head(25), selection=None, page_size=10)])
    return


@app.cell(hide_code=True)
def _(hospitals, mo):
    dist_col = mo.ui.dropdown(list(hospitals.columns), value="Hospital overall rating", label="Column", searchable=True)
    only_diff = mo.ui.checkbox(value=True, label="Show only values whose counts differ")
    mo.vstack([mo.md("### Tool 4 — Value distribution, side by side\nHow often each value appears in each file."),
               mo.hstack([dist_col, only_diff], justify="start", gap=2)])
    return dist_col, only_diff


@app.cell(hide_code=True)
def _(dist_col, hospitals, mo, only_diff, pd, planted):
    _c = dist_col.value
    _v = pd.concat([planted[_c].value_counts().rename("practice file"),
                    hospitals[_c].value_counts().rename("clean file")], axis=1).fillna(0).astype(int)
    _v["difference"] = _v["practice file"] - _v["clean file"]
    _v = _v.reset_index(names="value")
    if only_diff.value:
        _v = _v[_v["difference"] != 0]
    _v = _v.sort_values("difference", key=abs, ascending=False)
    mo.vstack([mo.md(f"{len(_v):,} values shown for **{_c}**. Remember the duplicate rows also change counts — "
                     "which differences are *not* explained by duplicates?"),
               mo.ui.table(_v, selection=None, page_size=10)])
    return


@app.cell(hide_code=True)
def _(mo):
    id_box = mo.ui.text(value="", label="Facility ID exactly as it appears in the practice file", placeholder="e.g. 070017")
    mo.vstack([mo.md("### Tool 5 — Compare one hospital to the source\n"
                     "Type a Facility ID. You see every practice-file row with that ID, the clean row with that ID, "
                     "and which columns disagree. Use it to confirm a suspicion from Tools 2–4."),
               id_box])
    return (id_box,)


@app.cell(hide_code=True)
def _(hospitals, id_box, mo, pd, planted):
    _id = id_box.value.strip()
    if not _id:
        _out = mo.md("*Type an ID above.*")
    else:
        _p = planted[planted["Facility ID"] == _id]
        _c = hospitals[hospitals["Facility ID"] == _id]
        _parts = [mo.md(f"Practice file: **{len(_p)}** row(s) with this ID · clean file: **{len(_c)}** row(s).")]
        if len(_p) and len(_c):
            _both = pd.concat([_p.assign(file="practice"), _c.assign(file="clean")])
            _diff = [c for c in hospitals.columns if _both[c].nunique() > 1]
            _parts.append(mo.md("Columns that disagree: " + (", ".join(f"**{c}**" for c in _diff) if _diff else "none")))
            _side = _both[["file"] + list(hospitals.columns)].T
            _side.columns = [f"{f} row {i + 1}" for i, f in enumerate(_both["file"])]
            _parts.append(mo.ui.table(_side.reset_index(names="column"), selection=None, page_size=12))
        elif len(_p):
            _parts.append(mo.md("This ID is **not in the clean file**. Why might that be? Look at the name and address, "
                                "then search the clean file for that hospital another way."))
            _parts.append(mo.ui.table(_p, selection=None))
        _out = mo.vstack(_parts)
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Ask your AI — a check that would fire next month
    Finding the errors once is not enough; the next file might have them too. Paste:

    > *"Write a marimo cell with a function `check(df)` that returns a table of checks on a CMS Hospital
    > General Information file: one row per check, with the number of failing rows and one example. Include
    > checks for ______ (list what you found). Run it on `planted` and on `hospitals` and show both."*

    Then confirm: every check should fail on `planted` and pass on `hospitals`. If a check passes on both,
    it is not checking what you think.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    findings = mo.ui.text_area(
        placeholder="1. What is wrong · how many rows · how I found it · what it would break\n2. ...",
        rows=8, full_width=True, label="My findings (AI can help you word them; each one must be something you can explain live)")
    findings
    return (findings,)


@app.cell(hide_code=True)
def _(findings, mo):
    mo.md(f"**My findings:**\n\n{findings.value}" if findings.value.strip() else "*(Your findings will appear here.)*")
    return


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([mo.md("## Where these numbers came from"), mo.ui.table(provenance_table(), selection=None)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** (1) three traces from Part A — ideally numbers from *your* layer — each with file, line,
    column, raw text and period; (2) your list of planted errors: what, how many rows, how you found it, what
    it would break. Submit your AI transcript with it.

    **The one check to run:** for one of your three traces, open the source CSV yourself at the line number
    shown and read the raw text with your own eyes. Does it match?

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
