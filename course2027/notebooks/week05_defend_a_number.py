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
    # Week 5 — Defend one number

    Pick **one hospital and one measure**. By the end you will have a one-page defense of that single number:
    what kind of number it is, what it was counted from, when, what was hidden, how it compares, and what it
    does *not* tell you.

    The notebook gathers the facts from the file. **AI can help you draft the page; the ideas and decisions
    must be yours.** Make sure every claim is one you can explain live, in class, without the AI open — that
    explanation is what verifies the work.
    """)
    return


@app.cell(hide_code=True)
def _(load):
    uv = load("unplanned_visits")
    hrrp = load("hrrp")
    return hrrp, uv


@app.cell(hide_code=True)
def _(mo, uv):
    source_pick = mo.ui.radio(
        options=["Unplanned Hospital Visits", "Hospital Readmissions Reduction Program (HRRP)"],
        value="Unplanned Hospital Visits", label="Source file")
    _states = sorted(uv["State"].unique())
    state_pick = mo.ui.dropdown(_states, value="CT" if "CT" in _states else _states[0], label="State", searchable=True)
    mo.hstack([source_pick, state_pick], justify="start", gap=2)
    return source_pick, state_pick


@app.cell(hide_code=True)
def _(hrrp, mo, source_pick, state_pick, uv):
    is_uv = source_pick.value.startswith("Unplanned")
    src_df = uv if is_uv else hrrp
    measure_col = "Measure ID" if is_uv else "Measure Name"
    value_col = "Score" if is_uv else "Excess Readmission Ratio"
    _here = src_df[src_df["State"] == state_pick.value]
    _opts = dict(sorted({f"{n} ({i})": i for i, n in zip(_here["Facility ID"], _here["Facility Name"])}.items()))
    hospital_pick = mo.ui.dropdown(_opts, value=next(iter(_opts)) if _opts else None,
                                   label=f"Hospital ({len(_opts)} in this file for {state_pick.value})", searchable=True)
    _measures = sorted(src_df[measure_col].unique())
    _default = next((m for m in ("READM_30_HF", "READM-30-HF-HRRP") if m in _measures), _measures[0])
    measure_pick = mo.ui.dropdown(_measures, value=_default, label="Measure", searchable=True)
    mo.hstack([hospital_pick, measure_pick], justify="start", gap=2)
    return hospital_pick, is_uv, measure_col, measure_pick, src_df, value_col


@app.cell(hide_code=True)
def _(hospital_pick, measure_col, measure_pick, mo, pd, src_df, to_num):
    # The selected row, and every row of the same measure (for context)
    m_rows = src_df[src_df[measure_col] == measure_pick.value].copy()
    _sel = m_rows[m_rows["Facility ID"] == hospital_pick.value]
    row = _sel.iloc[0] if len(_sel) else None
    # Which columns actually hold numbers for THIS measure? (Check before claiming anything.)
    _skip = {"Facility ID", "Facility Name", "Address", "City/Town", "State", "ZIP Code", "County/Parish",
             "Telephone Number", "Measure ID", "Measure Name", "Compared to National", "Footnote", "Start Date", "End Date"}
    populated = pd.DataFrame([
        {"column": c, "rows with a number": int(to_num(m_rows[c]).notna().sum()), "rows for this measure": len(m_rows),
         "most common non-number text": (m_rows[c][to_num(m_rows[c]).isna()].value_counts().index[:1].tolist() or [""])[0]}
        for c in m_rows.columns if c not in _skip])
    mo.vstack([mo.md(f"**Which columns hold numbers for {measure_pick.value}?** Check this before you claim a "
                     "numerator or denominator — a column that exists is not a column that is filled in."),
               mo.ui.table(populated, selection=None)])
    return m_rows, populated, row


@app.cell(hide_code=True)
def _(hrrp, is_uv, m_rows, measure_col, pd, populated, row, src_df, to_num, value_col):
    # Gather the facts for the defense. Every sentence below is computed from the file.
    facts = {}
    if row is not None:
        _name = row["Measure Name"]
        _val = to_num(pd.Series([row[value_col]])).iloc[0]
        _all = to_num(m_rows[value_col])
        facts["value"] = f"{_val:g}" if pd.notna(_val) else f"not reported (`{row[value_col]}`)"
        facts["value_num"] = _val
        facts["pct"] = (f"higher than {(_all.dropna() < _val).mean() * 100:.0f}% of the {int(_all.notna().sum()):,} hospitals "
                        f"with a number for this measure" if pd.notna(_val) else "cannot be ranked (no number)")
        facts["median"] = f"{_all.median():.3g}" if _all.notna().any() else "n/a"
        # 1. What kind of number
        if is_uv:
            _low = _name.lower()
            if "ratio" in _low:
                facts["kind"] = f"a **ratio** (\"{_name}\"). Check the measure definition for what 1.0 means."
            elif "return days" in _low:
                _neg = int((_all < 0).sum())
                facts["kind"] = (f"a measure of **hospital return days** (\"{_name}\"). The file does not say what it "
                                 f"is counted per — check the definition for the unit. {_neg:,} hospitals have a "
                                 "negative value, so it cannot be a plain count of days; the definition will say what "
                                 "it is compared against.")
            elif "per 1,000" in _low:
                facts["kind"] = f"a **rate per 1,000** (\"{_name}\")."
            else:
                facts["kind"] = (f"a **rate** (\"{_name}\"). The file does not state the unit; the median across "
                                 f"hospitals is {facts['median']}. Confirm the unit in the measure definition.")
        else:
            _p, _e, _r = (to_num(hrrp[c]) for c in ["Predicted Readmission Rate", "Expected Readmission Rate",
                                                     "Excess Readmission Ratio"])
            _gap = ((_p / _e) - _r).abs().max()
            facts["kind"] = ("the **Excess Readmission Ratio** = predicted rate ÷ expected rate. Checked in this file: "
                             f"predicted ÷ expected matches the published ratio to within {_gap:.5f} on every row "
                             f"with numbers. Above 1 means predicted is higher than expected. This hospital: "
                             f"predicted {row['Predicted Readmission Rate']}, expected {row['Expected Readmission Rate']}.")
        # 2. Numerator / denominator
        _pop = populated.set_index("column")["rows with a number"]
        if is_uv:
            _bits = [f"Denominator (as labeled in the file): **{row['Denominator']}**"]
            if _pop.get("Number of Patients", 0) > 0:
                _bits.append(f"Number of Patients: **{row['Number of Patients']}**")
            _bits.append(f"Number of Patients Returned: `{row['Number of Patients Returned']}` — for this measure "
                         f"{int(_pop.get('Number of Patients Returned', 0)):,} of {len(m_rows):,} rows hold a number, "
                         "so the file does **not** give you a numerator. Say so.")
            facts["numden"] = "; ".join(_bits)
        else:
            _d, _n = to_num(pd.Series([row["Number of Discharges"]])).iloc[0], to_num(pd.Series([row["Number of Readmissions"]])).iloc[0]
            _txt = (f"Number of Readmissions: **{row['Number of Readmissions']}**; Number of Discharges: "
                    f"**{row['Number of Discharges']}**.")
            if pd.notna(_d) and pd.notna(_n) and _d > 0:
                _txt += (f" Raw share = {_n:g} ÷ {_d:g} = {_n / _d * 100:.1f}% — this is *not* the published rate, "
                         "which comes from a model (predicted vs. expected).")
            _too = hrrp["Number of Readmissions"].eq("Too Few to Report")
            _txt += (f" Across the file, {int(_too.sum()):,} rows say \"Too Few to Report\"; in "
                     f"{int((_too & hrrp['Number of Discharges'].eq('N/A')).sum()):,} of them the discharges are "
                     "also \"N/A\" — yet a ratio is still published.")
            facts["numden"] = _txt
        # 3. Period
        _n_periods = len(src_df[["Start Date", "End Date"]].drop_duplicates())
        facts["period"] = (f"**{row['Start Date']} to {row['End Date']}**. This file mixes {_n_periods} different "
                           "reporting period(s) across its measures — check that anything you compare it with covers "
                           "the same months.")
        # 4. Suppression / footnotes
        _codes = m_rows["Footnote"].replace("", "(none)").value_counts()
        facts["foot"] = (f"Footnote on this row: **{row['Footnote'] or '(none)'}**. For this measure, "
                         f"{int(_all.isna().sum()):,} of {len(m_rows):,} hospitals have no number. Footnote codes seen: "
                         + ", ".join(f"{k} ({v:,})" for k, v in _codes.head(6).items())
                         + ". Footnote numbers are codes: look up what each means in CMS's footnote list for this "
                         "dataset (linked from the source page). Do not guess.")
        # 5. Compared to national
        if is_uv:
            _cmp = m_rows["Compared to National"].value_counts()
            _ci = ""
            if to_num(pd.Series([row["Lower Estimate"]])).notna().iloc[0]:
                _ci = f" Interval reported: {row['Lower Estimate']} to {row['Higher Estimate']}."
            if list(_cmp.index) == ["Not Available"]:
                facts["natl"] = ("\"Compared to National\" is **Not Available for every hospital** on this measure in "
                                 f"this release ({len(m_rows):,} rows). You cannot cite a CMS comparison; you can only "
                                 f"say where it sits: {facts['pct']} (median {facts['median']}).")
            else:
                facts["natl"] = (f"This hospital: **{row['Compared to National']}**.{_ci} Across hospitals: "
                                 + ", ".join(f"{k} ({v:,})" for k, v in _cmp.items()) + ".")
        else:
            facts["natl"] = ("HRRP has no \"Compared to National\" column. The ratio compares the hospital to its own "
                             f"expected rate, not to a national rate. It is {facts['pct']} (median {facts['median']}).")
    return (facts,)


@app.cell(hide_code=True)
def _(alt_chart, facts, hospital_pick, measure_pick, mo, row):
    if row is None:
        _out = mo.md(f"*{hospital_pick.selected_key} has no row for {measure_pick.value}. That absence is a fact too — "
                     "pick another measure or hospital.*")
    else:
        _out = mo.vstack([
            mo.md("\n\n".join([
                f"## The facts behind {row['Facility Name']} — {measure_pick.value}",
                f"**The number:** {facts['value']}",
                f"1. **What it is.** {facts['kind']}\n"
                f"2. **Numerator and denominator.** {facts['numden']}\n"
                f"3. **Reporting period.** {facts['period']}\n"
                f"4. **Suppression and footnotes.** {facts['foot']}\n"
                f"5. **How it compares.** {facts['natl']}\n"
                "6. **What it does not tell you.** It is one hospital's result over a fixed window, not this year's. "
                "Whether and how it is risk-adjusted, and *which patients* are counted (for example, which insurance), "
                "is set by the measure definition — read it before you say. It says nothing about *why* the number is "
                "what it is.",
            ])),
            alt_chart,
        ])
    _out
    return


@app.cell(hide_code=True)
def _(facts, m_rows, measure_pick, pd, row, to_num, value_col):
    import altair as alt
    _v = pd.DataFrame({"value": to_num(m_rows[value_col])}).dropna()
    _bars = alt.Chart(_v).mark_bar(color="#8aa6c1").encode(
        x=alt.X("value:Q", bin=alt.Bin(maxbins=40), title=f"{value_col} — {measure_pick.value}"),
        y=alt.Y("count():Q", title="hospitals"))
    alt_chart = _bars
    if row is not None and pd.notna(facts.get("value_num")):
        alt_chart = _bars + alt.Chart(pd.DataFrame({"value": [facts["value_num"]]})).mark_rule(
            color="#c0392b", strokeWidth=2).encode(x="value:Q")
    alt_chart = alt_chart.properties(width=560, height=180,
                                     title=f"All {len(_v):,} hospitals with a number (red line = your hospital)")
    return (alt_chart,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Write your defense

    Fill in the three boxes. The page below combines your answers with the facts from the file. AI can help
    you draft and tighten it; before you submit, read every sentence and ask "could I explain this live,
    without the AI open?" A defense you can't say out loud isn't a defense.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    own_meaning = mo.ui.text_area(label="1. In one or two sentences, what does this number mean for a reader?", rows=3, full_width=True)
    own_trust = mo.ui.text_area(label="2. Why do I believe it? (what I checked, and where)", rows=3, full_width=True)
    own_limits = mo.ui.text_area(label="3. What would I refuse to claim from it?", rows=3, full_width=True)
    mo.vstack([own_meaning, own_trust, own_limits])
    return own_limits, own_meaning, own_trust


@app.cell(hide_code=True)
def _(facts, measure_pick, mo, own_limits, own_meaning, own_trust, row):
    def _or(box):
        return box.value.strip() or "*(write this yourself)*"
    if row is None:
        _page = "*Pick a hospital with a row for this measure first.*"
    else:
        _page = "\n\n".join([
            "# Defense of one number — DRAFT",
            f"**{row['Facility Name']} ({row['Facility ID']}, {row['State']}) · {measure_pick.value} · value {facts['value']}**",
            f"**What it means.** {_or(own_meaning)}",
            f"**What kind of number.** {facts['kind']}",
            f"**Counted from.** {facts['numden']}",
            f"**When.** {facts['period']}",
            f"**What is hidden.** {facts['foot']}",
            f"**Compared with.** {facts['natl']}",
            f"**Why I believe it.** {_or(own_trust)}",
            f"**What I won't claim.** {_or(own_limits)}",
            "*Draft assembled by the notebook from the source file. Every claim is one I can explain without the AI open.*",
        ])
    mo.md(_page)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Ask your AI — draft, then stress-test
    AI can help you draft this; make sure every claim is one you can explain live, without the AI open. Once
    you have a draft, paste it and:

    > *"Here is my one-page defense of a CMS hospital measure. List every claim in it, and for
    > each one tell me whether it is supported by the facts I gave, needs a source I haven't cited (for example
    > the measure definition or the CMS footnote list), or is wrong. Ask me two questions a skeptical hospital
    > executive would ask."*

    Then make sure you can answer the two questions yourself, out loud — that is what show and explain is for.
    ///
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

    **Deliverable:** a one-page defense of one number — what it is, numerator and denominator (or why the file
    doesn't give them), suppression and footnotes, reporting period, how it compares, and what it does not tell
    you. AI may help draft it; every claim must be one you can explain live without the AI open. Submit your AI
    transcript with it.

    **The one check to run:** open the measure definition on the CMS source page and confirm the unit and the
    patient population you describe. If you can't find it, write "not confirmed" rather than guess.

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
