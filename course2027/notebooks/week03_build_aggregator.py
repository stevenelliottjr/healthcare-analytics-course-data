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

    return load, mo, pd, provenance_table, to_num


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 3 — Build your aggregator

    An **aggregator** is one table, at one **grain**, that joins several public sources and records where
    every column came from. Yours is at **hospital grain: one row per hospital**. You will keep this
    notebook all term — every later week (verify, defend, app, agent, refresh) starts from the layer it builds.

    The build, in order:

    1. **Start** with every hospital in CMS *Hospital General Information*.
    2. **Join one measure** from CMS *Unplanned Hospital Visits* (you pick it).
    3. *(optional)* **Join HRRP**, the readmissions penalty program, for the same condition.
    4. *(optional)* **Join county measures** (CDC PLACES and/or ACS) through the course crosswalk.

    After every step the **join ledger** counts the rows. If a number changes and you can't say why,
    stop — that is the lesson for tonight.
    """)
    return


@app.cell(hide_code=True)
def _(load):
    hospitals = load("hospitals")
    visits = load("unplanned_visits")
    hrrp = load("hrrp")
    crosswalk = load("crosswalk")
    places = load("places")
    acs = load("acs_measures")
    return acs, crosswalk, hospitals, hrrp, places, visits


@app.cell(hide_code=True)
def _(acs, mo, places, visits):
    _names = visits[["Measure ID", "Measure Name"]].drop_duplicates().sort_values("Measure ID")
    _opts = {f"{r['Measure ID']} — {r['Measure Name']}": r["Measure ID"] for _, r in _names.iterrows()}
    measure_pick = mo.ui.dropdown(options=_opts, value=next(k for k, v in _opts.items() if v == "READM_30_HF"),
                                  label="Unplanned-visits measure", full_width=True)
    only_scored = mo.ui.checkbox(label="Filter: keep only hospitals with a numeric score for this measure", value=False)
    use_hrrp = mo.ui.checkbox(label="Join HRRP for the same condition (if one exists)", value=True)

    _p = places[["measureid", "measure"]].drop_duplicates().sort_values("measureid")
    places_pick = mo.ui.multiselect(options={f"{r['measureid']} — {r['measure']}": r["measureid"] for _, r in _p.iterrows()},
                                    value=[k for k in [f"{r['measureid']} — {r['measure']}" for _, r in _p.iterrows()] if k.startswith("DIABETES")],
                                    label="CDC PLACES county measures", full_width=True)
    places_type = mo.ui.dropdown(options=sorted(places["data_value_type"].unique()), value="Age-adjusted prevalence",
                                 label="PLACES value type")
    _a = acs[["measureid", "short_question_text"]].drop_duplicates().sort_values("measureid")
    acs_pick = mo.ui.multiselect(options={f"{r['measureid']} — {r['short_question_text']}": r["measureid"] for _, r in _a.iterrows()},
                                 value=[k for k in [f"{r['measureid']} — {r['short_question_text']}" for _, r in _a.iterrows()] if k.startswith("POV150")],
                                 label="ACS county measures", full_width=True)
    mo.vstack([
        mo.md("## Your choices"),
        measure_pick, only_scored, use_hrrp,
        mo.hstack([places_pick, places_type], widths=[3, 1]),
        acs_pick,
        mo.md("*Clear both county lists to build a hospital-only layer.*"),
    ])
    return acs_pick, measure_pick, only_scored, places_pick, places_type, use_hrrp


@app.cell(hide_code=True)
def _(acs, acs_pick, crosswalk, hrrp, measure_pick, pd, places, places_pick, places_type, to_num, use_hrrp, visits):
    # Prepare each source so it has ONE row per join key (hidden: you don't need to read this).
    measure = measure_pick.value
    _u = visits[visits["Measure ID"] == measure]
    uv_rows = pd.DataFrame({
        "Facility ID": _u["Facility ID"], "uv_measure": measure, "uv_score": _u["Score"],
        "uv_score_num": to_num(_u["Score"]), "uv_denominator": _u["Denominator"],
        "uv_period": _u["Start Date"] + " to " + _u["End Date"],
    })

    hrrp_name = measure.replace("_", "-") + "-HRRP"
    hrrp_rows = None
    if use_hrrp.value and hrrp_name in set(hrrp["Measure Name"]):
        _h = hrrp[hrrp["Measure Name"] == hrrp_name]
        hrrp_rows = pd.DataFrame({
            "Facility ID": _h["Facility ID"], "hrrp_measure": hrrp_name,
            "hrrp_excess_ratio": _h["Excess Readmission Ratio"], "hrrp_excess_ratio_num": to_num(_h["Excess Readmission Ratio"]),
            "hrrp_readmissions": _h["Number of Readmissions"], "hrrp_readmissions_num": to_num(_h["Number of Readmissions"]),
            "hrrp_discharges": _h["Number of Discharges"],
            "hrrp_period": _h["Start Date"] + " to " + _h["End Date"],
        })

    crosswalk_rows = crosswalk[["Facility ID", "county_fips", "county_name_census", "match_note"]].assign(
        county_fips=lambda d: d["county_fips"].replace("", pd.NA))

    def _wide(df, ids, prefix, name_col, year_col):
        _d = df[df["measureid"].isin(ids)]
        _w = _d.pivot(index="locationid", columns="measureid", values="data_value")
        _w = _w.apply(to_num).add_prefix(prefix + "_")
        _meta = _d.groupby("locationid").agg(**{f"{prefix}_county": (name_col, "first"), f"{prefix}_data_year": (year_col, "first")})
        return _meta.join(_w).reset_index().rename(columns={"locationid": "county_fips"})

    places_wide = None
    if places_pick.value:
        places_wide = _wide(places[places["data_value_type"] == places_type.value], places_pick.value, "places", "locationname", "year")
    acs_wide = _wide(acs, acs_pick.value, "acs", "locationname", "year") if acs_pick.value else None
    return acs_wide, crosswalk_rows, hrrp_name, hrrp_rows, measure, places_wide, uv_rows


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The build (read this code — it is the lesson)

    This is the only code you are asked to read this week. The explanation is under it.
    """)
    return


@app.cell
def _(acs_wide, crosswalk_rows, hospitals, hrrp_rows, measure, only_scored, places_wide, uv_rows):
    ledger = []

    def count(step, df, kind, matched=None):
        ledger.append({"step": step, "kind": kind, "rows": len(df),
                       "unique hospitals": df["Facility ID"].nunique(), "rows matched": matched})
        return df

    layer = hospitals[["Facility ID", "Facility Name", "State", "County/Parish", "Hospital Type"]]
    count("Start: every CMS hospital", layer, "start")

    layer = layer.merge(uv_rows, on="Facility ID", how="left", validate="one_to_one")
    count(f"Join unplanned visits ({measure})", layer, "join", matched=int(layer["uv_period"].notna().sum()))

    if only_scored.value:
        layer = layer[layer["uv_score_num"].notna()]
        count("Filter: keep hospitals with a numeric score", layer, "filter")

    if hrrp_rows is not None:
        layer = layer.merge(hrrp_rows, on="Facility ID", how="left", validate="one_to_one")
        count("Join HRRP (same condition)", layer, "join", matched=int(layer["hrrp_period"].notna().sum()))

    if places_wide is not None or acs_wide is not None:
        layer = layer.merge(crosswalk_rows, on="Facility ID", how="left", validate="one_to_one")
        count("Join crosswalk (hospital to county FIPS)", layer, "join", matched=int(layer["county_fips"].notna().sum()))
    if places_wide is not None:
        layer = layer.merge(places_wide, on="county_fips", how="left", validate="many_to_one")
        count("Join CDC PLACES by county FIPS", layer, "join", matched=int(layer["places_county"].notna().sum()))
    if acs_wide is not None:
        layer = layer.merge(acs_wide, on="county_fips", how="left", validate="many_to_one")
        count("Join ACS measures by county FIPS", layer, "join", matched=int(layer["acs_county"].notna().sum()))
    return layer, ledger


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({"What each line does (open this)": mo.md(r"""
    - `ledger = []` — an empty list. Every step below adds one line to it: that list *is* the join ledger.
    - `def count(step, df, kind, matched=None)` — a small helper that writes down the step's name, how many
      rows the table has now, how many different hospitals, and how many rows found a match. It hands the
      table back unchanged.
    - `layer = hospitals[[...]]` — start from every hospital, keeping five columns. This is the grain:
      one row per `Facility ID`.
    - `layer.merge(uv_rows, on="Facility ID", how="left", ...)` — a **left join**: keep *every* hospital
      on the left; attach the measure where the Facility ID matches; leave it **blank** where it doesn't.
      Nothing is thrown away, and nothing is filled in with zero.
    - `validate="one_to_one"` — a guard. If either side had a Facility ID twice, the join would multiply
      rows; this line makes pandas **stop with an error** instead of silently duplicating hospitals.
    - `if only_scored.value: layer = layer[...notna()]` — the only step that *removes* rows, and only
      if you ticked the box. The ledger shows how many.
    - The HRRP join works the same way, on the same key.
    - The **crosswalk** join adds a `county_fips` column to each hospital. Then PLACES and ACS join on
      `county_fips` with `validate="many_to_one"`: many hospitals can share one county, but each county
      must appear only once on the right.
    - `matched=...notna().sum()` — counts rows where the new source actually supplied something.
      **Rows** staying the same while **rows matched** drops is how a left join tells you what it couldn't find.
    """)})
    return


@app.cell(hide_code=True)
def _(ledger, mo, pd):
    ledger_df = pd.DataFrame(ledger)
    ledger_df["change in rows"] = ledger_df["rows"].diff().fillna(0).astype(int)
    ledger_df["match rate"] = (ledger_df["rows matched"] / ledger_df["rows"]).map(lambda v: "" if pd.isna(v) else f"{v:.1%}")
    ledger_df["rows matched"] = ledger_df["rows matched"].map(lambda v: "" if pd.isna(v) else f"{int(v):,}")
    mo.vstack([
        mo.md("## Join ledger"),
        mo.ui.table(ledger_df, selection=None),
        mo.md("A left join should never change **rows**. If it does, the right-hand table had a duplicate key. "
              "A filter should change rows, and the ledger says by how much."),
    ])
    return (ledger_df,)


@app.cell(hide_code=True)
def _(crosswalk_rows, hospitals, hrrp, hrrp_name, hrrp_rows, layer, measure, mo, pd, places, places_wide, uv_rows):
    _tabs = {}

    _no_row = hospitals[~hospitals["Facility ID"].isin(uv_rows["Facility ID"])]
    _tabs["No row for the measure"] = mo.vstack([
        mo.md(f"**{len(_no_row):,}** hospitals have no {measure} row at all (kept in the layer, left blank). By hospital type:"),
        mo.ui.table(_no_row["Hospital Type"].value_counts().rename_axis("Hospital Type").reset_index(name="hospitals"), selection=None),
    ])

    _non_num = uv_rows[uv_rows["uv_score_num"].isna()]
    _tabs["Row but no number"] = mo.vstack([
        mo.md(f"**{len(_non_num):,}** of {len(uv_rows):,} {measure} rows have a score that is not a number. "
              "They stay **missing** in `uv_score_num`; the original text stays in `uv_score`."),
        mo.ui.table(_non_num["uv_score"].replace("", "(blank)").value_counts().rename_axis("text in the file").reset_index(name="rows"), selection=None),
    ])

    if hrrp_rows is not None:
        _orph = hrrp_rows[~hrrp_rows["Facility ID"].isin(hospitals["Facility ID"])]
        _orph = _orph.merge(hrrp[["Facility ID", "Facility Name", "State"]].drop_duplicates(), on="Facility ID")
        _tabs["HRRP hospitals not in the hospital file"] = mo.vstack([
            mo.md(f"**{len(_orph):,}** HRRP rows for {hrrp_name} have a Facility ID that is not in Hospital General "
                  "Information. A left join from hospitals **drops them**. Who are they?"),
            mo.ui.table(_orph[["Facility ID", "Facility Name", "State"]], selection=None),
        ])
        _cov = (hospitals.assign(in_hrrp=hospitals["Facility ID"].isin(hrrp_rows["Facility ID"]))
                .groupby("Hospital Type")["in_hrrp"].agg(hospitals="size", with_hrrp_row="sum")
                .sort_values("hospitals", ascending=False).reset_index())
        _tabs["Hospitals HRRP doesn't cover"] = mo.vstack([
            mo.md(f"Only **{int(_cov['with_hrrp_row'].sum()):,}** of {len(hospitals):,} hospitals have an HRRP row. "
                  "HRRP does not cover every kind of hospital. Which types are in it? Check the HRRP source page "
                  "for the rule before you write it down."),
            mo.ui.table(_cov, selection=None),
        ])

    _cw = crosswalk_rows["match_note"].value_counts().rename_axis("crosswalk note").reset_index(name="hospitals")
    _tabs["No county FIPS"] = mo.vstack([
        mo.md("The crosswalk could not place these hospitals in a CDC county. Territories are not in the CDC county files; "
              "'check by hand' rows are CMS spellings that didn't match."),
        mo.ui.table(_cw, selection=None),
        mo.ui.table(crosswalk_rows[crosswalk_rows["match_note"].str.contains("by hand")]
                    .merge(hospitals[["Facility ID", "Facility Name", "State", "County/Parish"]], on="Facility ID"), selection=None),
    ])

    if places_wide is not None:
        _miss = layer[layer["county_fips"].notna() & layer["places_county"].isna()]
        _by = _miss["State"].value_counts().rename_axis("State").reset_index(name="hospitals with a county but no PLACES match")
        _ct = places[places["stateabbr"] == "CT"]["locationname"].drop_duplicates().tolist()
        _tabs["County not in PLACES"] = mo.vstack([
            mo.md(f"**{len(_miss):,}** hospitals have a county FIPS that PLACES 2025 doesn't have. "
                  f"Connecticut is one: the crosswalk uses the old counties (Fairfield County = 09001); PLACES "
                  f"reports CT as planning regions ({', '.join(_ct)}). Look at the other states too, then check "
                  "the PLACES source page before you explain them."),
            mo.ui.table(_by, selection=None),
        ])
    mo.vstack([mo.md("## What didn't match, and why"), mo.ui.tabs(_tabs)])
    return


@app.cell(hide_code=True)
def _(mo):
    min_rate = mo.ui.slider(start=0.5, stop=1.0, step=0.01, value=0.85, show_value=True,
                            label="Lowest key match rate I will accept")
    mo.vstack([
        mo.md(r"""
    ## Checks your layer reruns on every refresh

    These run every time the notebook runs — when you change a choice above, and in week 12 when a source
    is refreshed. They are the layer's **backpressure**: if a source changes under you, a check fails
    instead of a wrong number reaching your app. **You** set the match-rate bar; the AI can't decide
    what's good enough for your question.
    """),
        min_rate,
    ])
    return (min_rate,)


@app.cell(hide_code=True)
def _(layer, ledger, ledger_df, min_rate, mo, pd, to_num):
    _checks = []

    def _add(name, ok, detail):
        _checks.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    _add("Layer is not empty", len(layer) > 0, f"{len(layer):,} rows")
    _add("One row per hospital (unique key)", layer["Facility ID"].is_unique,
         f"{len(layer):,} rows, {layer['Facility ID'].nunique():,} unique Facility IDs")
    _joins = ledger_df[ledger_df["kind"] == "join"]
    _add("Joins never changed the row count", bool((_joins["change in rows"] == 0).all()),
         "; ".join(f"{s}: {c:+d}" for s, c in zip(_joins["step"], _joins["change in rows"])))
    for _e in [e for e in ledger if e["kind"] == "join"]:
        _v = _e["rows matched"] / _e["rows"] if _e["rows"] else 0.0
        _add(f"Key match rate: {_e['step']}", _v >= min_rate.value,
             f"{_e['rows matched']:,} of {_e['rows']:,} rows = {_v:.1%} (bar: {min_rate.value:.0%})")
    for _col in [c for c in ["uv_period", "hrrp_period", "places_data_year", "acs_data_year"] if c in layer]:
        _vals = sorted(layer[_col].dropna().unique())
        _add(f"One reporting period in {_col}", len(_vals) == 1, ", ".join(_vals) or "(no values)")
    for _txt, _num in [("uv_score", "uv_score_num"), ("hrrp_excess_ratio", "hrrp_excess_ratio_num"),
                       ("hrrp_readmissions", "hrrp_readmissions_num")]:
        if _txt in layer:
            _present = layer[_txt].notna()
            _supp = int((_present & layer[_num].isna()).sum())
            _bad = int((layer[_num].fillna(-1e9) != to_num(layer[_txt]).fillna(-1e9)).sum())
            _zeros = int((layer[_num] == 0).sum())
            _words = ", ".join(f"'{w}'" for w in layer.loc[_present & layer[_num].isna(), _txt].unique()[:3])
            _add(f"Suppressed kept as missing: {_num}", _bad == 0,
                 f"{_supp:,} rows say {_words or 'nothing non-numeric'} and are missing, not zero; "
                 f"{_zeros} values are a real 0 in the file")
    checks = pd.DataFrame(_checks)
    _n_fail = int((checks["result"] == "FAIL").sum())
    mo.vstack([
        mo.callout(mo.md(f"**{len(checks) - _n_fail} of {len(checks)} checks pass.**" +
                         ("" if not _n_fail else " Read each FAIL and decide: fix the layer, or change the bar and say why in your submission.")),
                   kind="success" if not _n_fail else "danger"),
        mo.ui.table(checks, selection=None),
    ])
    return (checks,)


@app.cell(hide_code=True)
def _(layer, mo):
    mo.vstack([
        mo.md(f"## Your layer\n\n**{len(layer):,} rows × {layer.shape[1]} columns.** Blank cells are missing values, not zeros. "
              "Column prefixes say where each column came from: `uv_` unplanned visits, `hrrp_` HRRP, "
              "`places_` CDC PLACES, `acs_` ACS, `county_`/`match_note` the course crosswalk."),
        mo.ui.table(layer, selection=None, page_size=10),
    ])
    return


@app.cell(hide_code=True)
def _(checks, layer, ledger_df, measure, mo, provenance_table):
    mo.vstack([
        mo.md("## Export"),
        mo.hstack([
            mo.download(data=layer.to_csv(index=False).encode("utf-8"), filename=f"aggregator_{measure}.csv", label="Layer (CSV)"),
            mo.download(data=ledger_df.to_csv(index=False).encode("utf-8"), filename="join_ledger.csv", label="Join ledger (CSV)"),
            mo.download(data=checks.to_csv(index=False).encode("utf-8"), filename="checks.csv", label="Checks (CSV)"),
            mo.download(data=provenance_table().to_csv(index=False).encode("utf-8"), filename="provenance.csv", label="Provenance (CSV)"),
        ], justify="start"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(mo.md(r"""
    **Ask your AI** — adding a fourth source:

    ```text
    My marimo notebook has a pandas DataFrame `layer` (one row per hospital, key "Facility ID",
    also a "county_fips" column; all IDs are text). I want to add one more source: <describe it,
    and paste its column names - not its data rows>. Write ONE new cell that:
    1. reduces the new source to one row per join key, and prints its row count;
    2. left-joins it onto a COPY called `layer4` with merge(..., how="left", validate=...)
       choosing one_to_one or many_to_one correctly;
    3. prints rows before and after, and how many rows matched;
    4. keeps non-numeric values like "Not Available" as missing, never zero.
    Do not reuse or redefine any variable name that already exists in the notebook.
    ```

    Then check: did rows stay the same? Is the match rate above your bar? If not, find out who didn't match.
    """), kind="info")
    return


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([mo.md("## Where these numbers came from"), mo.ui.table(provenance_table(), selection=None)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** your joined layer at hospital grain (CSV), with the join ledger showing row counts before
    and after each join and filter. Submit your AI transcript with it.

    **The one check to run:** pick one row of the ledger where *rows matched* is lower than *rows*, and say in
    one sentence who didn't match and why (use the "What didn't match" tabs).

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
