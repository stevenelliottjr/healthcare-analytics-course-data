import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 12: recency in practice

    **Deliverable:** refresh one source, rerun your checks, report what changed.

    Public data is not a fixed thing. CMS refreshes Care Compare on a schedule (the course data mirror's
    README says quarterly), and every refresh can add or drop hospitals, change numbers, move the
    reporting period forward, or suppress a value that used to be published. An app built in week 8 can
    be out of date by week 14 without anyone touching it.

    This notebook compares two versions of the layer:

    - **Earlier:** your week-3 export (upload it), or a **SIMULATED** earlier snapshot the notebook makes
      for you, so you can practise before any real refresh.
    - **Current:** the layer rebuilt now from the sources the course loads today.

    The real exercise is to run this again **after the next refresh** with your saved export, and
    report what actually changed.
    """)
    return


@app.cell(hide_code=True)
def _():
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

    return load, to_num, provenance_table, SOURCES, pd


@app.cell(hide_code=True)
def _(load):
    hospitals_raw = load("hospitals")
    unplanned_raw = load("unplanned_visits")
    crosswalk_raw = load("crosswalk")
    places_raw = load("places")
    return crosswalk_raw, hospitals_raw, places_raw, unplanned_raw


@app.cell(hide_code=True)
def _(crosswalk_raw, hospitals_raw, pd, places_raw, to_num, unplanned_raw):
    def build_layer(cms_measure="READM_30_HF", places_measure="DIABETES", places_type="Age-adjusted prevalence"):
        """The course default layer: one row per hospital.
        CMS hospital info + one CMS Unplanned Hospital Visits measure + one CDC PLACES county measure
        (joined through the course crosswalk). Left joins: no hospital is dropped while building."""
        steps = []
        h = hospitals_raw[["Facility ID", "Facility Name", "State", "County/Parish", "Hospital Type",
                           "Hospital overall rating"]].rename(columns={
            "Facility ID": "facility_id", "Facility Name": "facility_name", "State": "state",
            "County/Parish": "county_cms", "Hospital Type": "hospital_type",
            "Hospital overall rating": "overall_rating"})
        steps.append(("Start: CMS Hospital General Information (one row per hospital)", len(h), len(h)))
        m = unplanned_raw.loc[unplanned_raw["Measure ID"] == cms_measure,
                              ["Facility ID", "Measure ID", "Measure Name", "Score", "Denominator", "Footnote",
                               "Start Date", "End Date"]].rename(columns={
            "Facility ID": "facility_id", "Measure ID": "cms_measure_id", "Measure Name": "cms_measure_name",
            "Score": "cms_score_text", "Denominator": "cms_denominator", "Footnote": "cms_footnote",
            "Start Date": "cms_period_start", "End Date": "cms_period_end"})
        layer = h.merge(m, on="facility_id", how="left", validate="one_to_one")
        steps.append((f"+ CMS Unplanned Hospital Visits, {cms_measure} (left join on Facility ID)",
                      len(layer), int(layer["cms_measure_id"].notna().sum())))
        x = crosswalk_raw[["Facility ID", "county_fips", "match_note"]].rename(columns={
            "Facility ID": "facility_id", "match_note": "county_match_note"})
        layer = layer.merge(x, on="facility_id", how="left", validate="one_to_one")
        steps.append(("+ Course crosswalk, hospital to county FIPS (left join on Facility ID)",
                      len(layer), int((layer["county_fips"].fillna("") != "").sum())))
        p = places_raw.loc[(places_raw["measureid"] == places_measure) & (places_raw["data_value_type"] == places_type),
                           ["locationid", "locationname", "measureid", "measure", "data_value_type", "year",
                            "data_value"]].rename(columns={
            "locationid": "county_fips", "locationname": "places_county_name", "measureid": "places_measure_id",
            "measure": "places_measure", "data_value_type": "places_value_type", "year": "places_data_year",
            "data_value": "places_value_text"})
        layer = layer.merge(p, on="county_fips", how="left", validate="many_to_one")
        steps.append((f"+ CDC PLACES county, {places_measure} {places_type.lower()} (left join on county FIPS)",
                      len(layer), int(layer["places_measure_id"].notna().sum())))
        layer = layer.fillna("")  # blank = the join found no row (not the same as 'Not Available')
        layer["cms_score"] = to_num(layer["cms_score_text"])  # 'Not Available' -> missing, never zero
        layer["places_value"] = to_num(layer["places_value_text"])
        log = pd.DataFrame(steps, columns=["step", "rows after this step", "rows that found a match"])
        return layer, log

    current_built, build_log = build_layer()
    # Compare as text, the way a CSV export stores it.
    current = current_built.astype(str).fillna("").replace("nan", "")
    return build_log, current


@app.cell(hide_code=True)
def _(mo, provenance_table):
    mo.vstack([
        mo.md("""
        ## 1. Where the current numbers came from

        Check the `obtained_from` and `loaded_at` columns. If they say **local cache**, this notebook reused
        a copy saved earlier in the `data` folder next to it, not a fresh download. To force a fresh copy,
        delete that `data` folder and run again. Then ask your instructor when the course copy of the sources
        was last refreshed: a fresh download of an old copy is still old.
        """),
        provenance_table(),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    upload = mo.ui.file(filetypes=[".csv"], label="Upload your earlier export (week-3 CSV)")
    mo.md(f"""
    ## 2. The earlier version

    {upload}

    No file uploaded? The notebook uses a **SIMULATED** earlier snapshot (described below).
    """)
    return (upload,)


@app.cell(hide_code=True)
def _(current, pd, to_num):
    # SIMULATED earlier snapshot: the current layer, changed in fixed, documented ways.
    # Deterministic: the same rows are picked every run (by sorted facility_id), no randomness.
    def simulate_earlier(cur):
        old = cur.sort_values("facility_id").reset_index(drop=True).copy()
        changes = []

        def back_one_year(s):
            return s.str.replace(r"(\d{4})$", lambda m: str(int(m.group(1)) - 1), regex=True)

        for c in ["cms_period_start", "cms_period_end", "places_data_year"]:
            old.loc[old[c] != "", c] = back_one_year(old.loc[old[c] != "", c])
        changes.append("every CMS period and the PLACES data year moved back one year")

        num = to_num(old["cms_score_text"]).notna()
        changed = old[num].index[::400][:8]
        old.loc[changed, "cms_score_text"] = (to_num(old.loc[changed, "cms_score_text"]) + 0.5).round(1).astype(str)
        old.loc[changed, "cms_score"] = old.loc[changed, "cms_score_text"]
        changes.append(f"{len(changed)} hospitals had a score 0.5 higher")

        na = old[(old["cms_measure_id"] != "") & ~num].index[::300][:5]
        old.loc[na, "cms_score_text"] = "20.0"
        old.loc[na, "cms_score"] = "20.0"
        changes.append(f"{len(na)} hospitals that are 'Not Available' now had a published score (20.0)")

        dropped = old.index.difference(changed.union(na))[::1000][:6]
        old = old.drop(index=dropped)
        changes.append(f"{len(dropped)} current hospitals were not in the earlier file")

        fake = old.head(3).copy()
        fake["facility_id"] = ["SIM-0001", "SIM-0002", "SIM-0003"]
        fake["facility_name"] = ["SIMULATED HOSPITAL " + str(i) for i in (1, 2, 3)]
        old = pd.concat([old, fake], ignore_index=True)
        changes.append("3 made-up hospitals (SIM-0001 to SIM-0003) were in the earlier file and are gone now")
        return old, changes

    simulated, sim_changes = simulate_earlier(current)
    return sim_changes, simulated


@app.cell(hide_code=True)
def _(io, mo, pd, sim_changes, simulated, upload):
    if upload.value:
        earlier = pd.read_csv(io.BytesIO(upload.contents()), dtype=str, keep_default_na=False, encoding="utf-8-sig")
        earlier_name = f"your upload: {upload.name()}"
        _msg = mo.md(f"Earlier version: **{earlier_name}**, {len(earlier):,} rows, {earlier.shape[1]} columns.")
    else:
        earlier = simulated
        earlier_name = "SIMULATED earlier snapshot"
        _msg = mo.callout(mo.md("**SIMULATED.** No file uploaded, so the earlier version is the current layer "
                                "with these made-up changes:\n\n" + "\n".join(f"- {c}" for c in sim_changes)
                                + "\n\nThe diff below should find exactly these. That is how you know it works."),
                          kind="warn")
    _msg
    return earlier, earlier_name


@app.cell(hide_code=True)
def _(crosswalk_raw, current, earlier, hospitals_raw, load, mo, pd, places_raw, to_num, unplanned_raw):
    # If the earlier file is a week-3 export, rebuild the current version THE SAME WAY (same measure,
    # same column names), so like is compared with like. Otherwise compare with the default layer.
    def rebuild_like_week3(old):
        measure = old.loc[old["uv_measure"] != "", "uv_measure"].iloc[0]
        cur = hospitals_raw[["Facility ID", "Facility Name", "State", "County/Parish", "Hospital Type"]]
        u = unplanned_raw[unplanned_raw["Measure ID"] == measure]
        cur = cur.merge(pd.DataFrame({
            "Facility ID": u["Facility ID"], "uv_measure": measure, "uv_score": u["Score"],
            "uv_score_num": to_num(u["Score"]), "uv_denominator": u["Denominator"],
            "uv_period": u["Start Date"] + " to " + u["End Date"]}), on="Facility ID", how="left")
        if "uv_score_num" in old.columns and (old["uv_score_num"] != "").all():
            cur = cur[cur["uv_score_num"].notna()]  # the week-3 export kept numeric scores only
        if "hrrp_measure" in old.columns:
            hr = load("hrrp")
            h = hr[hr["Measure Name"] == old.loc[old["hrrp_measure"] != "", "hrrp_measure"].iloc[0]]
            cur = cur.merge(pd.DataFrame({
                "Facility ID": h["Facility ID"], "hrrp_measure": h["Measure Name"],
                "hrrp_excess_ratio": h["Excess Readmission Ratio"], "hrrp_excess_ratio_num": to_num(h["Excess Readmission Ratio"]),
                "hrrp_readmissions": h["Number of Readmissions"], "hrrp_readmissions_num": to_num(h["Number of Readmissions"]),
                "hrrp_discharges": h["Number of Discharges"],
                "hrrp_period": h["Start Date"] + " to " + h["End Date"]}), on="Facility ID", how="left")
        if "county_fips" in old.columns:
            cur = cur.merge(crosswalk_raw[["Facility ID", "county_fips", "county_name_census", "match_note"]],
                            on="Facility ID", how="left")

        def wide(df, ids, prefix):
            d = df[df["measureid"].isin(ids)]
            w = d.pivot(index="locationid", columns="measureid", values="data_value").apply(to_num).add_prefix(prefix + "_")
            meta = d.groupby("locationid").agg(**{f"{prefix}_county": ("locationname", "first"),
                                                  f"{prefix}_data_year": ("year", "first")})
            return meta.join(w).reset_index().rename(columns={"locationid": "county_fips"})

        p_ids = [c[7:] for c in old.columns if c.startswith("places_") and c[7:] in set(places_raw["measureid"])]
        if p_ids and "county_fips" in cur.columns:
            # Which value type did week 3 use? Pick the one that matches the earlier file best.
            best = None
            for t in sorted(places_raw["data_value_type"].unique()):
                cand = cur.merge(wide(places_raw[places_raw["data_value_type"] == t], p_ids, "places"),
                                 on="county_fips", how="left")
                m = cand.set_index("Facility ID")[f"places_{p_ids[0]}"].astype(str)
                o = old.set_index("Facility ID")[f"places_{p_ids[0]}"].astype(str)
                hits = int((m.reindex(o.index) == o).sum())
                if best is None or hits > best[0]:
                    best = (hits, cand)
            cur = best[1]
        a_cols = [c for c in old.columns if c.startswith("acs_") and c not in ("acs_county", "acs_data_year")]
        if a_cols and "county_fips" in cur.columns:
            acs = load("acs_measures")
            cur = cur.merge(wide(acs, [c[4:] for c in a_cols], "acs"), on="county_fips", how="left")
        return cur

    if "uv_measure" in earlier.columns and "Facility ID" in earlier.columns:
        compare_current = rebuild_like_week3(earlier).astype(str).fillna("").replace("nan", "")
        _how = "rebuilt the current layer **the way week 3 builds it** (same measure, same columns)"
    else:
        compare_current = current
        _how = "compared with the course default layer"
    mo.md(f"For the comparison, the notebook {_how}: {len(compare_current):,} rows.")
    return (compare_current,)


@app.cell(hide_code=True)
def _(compare_current, earlier, mo):
    KEY = next((c for c in ["facility_id", "Facility ID"] if c in earlier.columns and c in compare_current.columns), None)
    both_cols = [c for c in compare_current.columns if c in earlier.columns]
    _only_old = [c for c in earlier.columns if c not in compare_current.columns]
    _only_new = [c for c in compare_current.columns if c not in earlier.columns]
    _out = [mo.md(f"**Columns in both versions:** {len(both_cols)}. Only in the earlier file: "
                  f"{', '.join(_only_old) or 'none'}. Only in the current layer: {', '.join(_only_new) or 'none'}.")]
    if KEY is None:
        _out.append(mo.callout(mo.md("Your file has no `facility_id` (or `Facility ID`) column, so rows can't be "
                                     "matched. Add it to your export and upload again."), kind="danger"))
    elif _only_old:
        _out.append(mo.md("Your file has columns the current build doesn't make, so they can't be compared. "
                          "To compare those too, use the Ask your AI box at the end."))
    mo.vstack(_out)
    return KEY, both_cols


@app.cell(hide_code=True)
def _(KEY, compare_current, earlier, mo, pd, to_num):
    # The week-3 checks, run on both versions.
    def checks(df):
        out = {"rows": len(df)}
        if KEY:
            out["distinct hospitals (key)"] = df[KEY].nunique()
            out["duplicate keys"] = int(df[KEY].duplicated().sum())
        for c in ["cms_score_text", "uv_score", "Score"]:
            if c in df.columns:
                out[f"numeric {c}"] = int(to_num(df[c]).notna().sum())
                out[f"'Not Available' in {c}"] = int((df[c] == "Not Available").sum())
                out[f"blank {c} (no row in the join)"] = int((df[c] == "").sum())
        if "county_fips" in df.columns:
            out["rows with a county FIPS"] = int((df["county_fips"] != "").sum())
        for c in [c for c in df.columns if c == "places_value_text" or (c.startswith("places_") and c.isupper() is False
                  and c[7:].isupper())]:
            out[f"rows with a value in {c}"] = int((df[c] != "").sum())
        return out

    _e, _c = checks(earlier), checks(compare_current)
    check_table = pd.DataFrame({"check": list(_c), "earlier": [_e.get(k, "") for k in _c],
                                "current": [_c[k] for k in _c]})
    check_table["changed?"] = ["yes" if str(a) != str(b) else "" for a, b in
                               zip(check_table["earlier"], check_table["current"])]
    mo.vstack([mo.md("## 3. The week-3 checks, before and after"), check_table])
    return (check_table,)


@app.cell(hide_code=True)
def _(KEY, both_cols, compare_current, earlier, pd, to_num):
    # The diff. Rows are matched on the key; values are compared as text, numbers with to_num.
    if KEY:
        _e = earlier.drop_duplicates(KEY).set_index(KEY)
        _c = compare_current.drop_duplicates(KEY).set_index(KEY)
        added = _c.loc[_c.index.difference(_e.index)].reset_index()
        removed = _e.loc[_e.index.difference(_c.index)].reset_index()
        _common = _e.index.intersection(_c.index)
        _cols = [c for c in both_cols if c != KEY]
        _e, _c = _e.loc[_common, _cols].fillna(""), _c.loc[_common, _cols].fillna("")
        _diff = (_e != _c)
        changes_by_column = _diff.sum().rename_axis("column").rename("hospitals with a different value").reset_index()
        changes_by_column = changes_by_column[changes_by_column.iloc[:, 1] > 0]

        _period_cols = [c for c in _cols if any(k in c.lower() for k in ["period", "year", "date"])]
        period_changes = pd.concat(
            [pd.DataFrame({"column": c, "earlier": _e[c], "current": _c[c]}) for c in _period_cols]
        ) if _period_cols else pd.DataFrame(columns=["column", "earlier", "current"])
        period_changes = (period_changes[period_changes["earlier"] != period_changes["current"]]
                          .value_counts().rename("hospitals").reset_index())

        period_hospitals = int(_diff[_period_cols].any(axis=1).sum()) if _period_cols else 0
        _score = next((c for c in ["cms_score_text", "uv_score", "Score"] if c in _cols), None)
        if _score:
            _old_n, _new_n = to_num(_e[_score]), to_num(_c[_score])
            _name = next((c for c in ["facility_name", "Facility Name"] if c in _cols), _score)
            _both = _old_n.notna() & _new_n.notna() & ((_old_n - _new_n).abs() > 1e-9)
            number_changes = pd.DataFrame({"hospital": _c.loc[_both, _name], "earlier": _old_n[_both],
                                           "current": _new_n[_both], "change": (_new_n - _old_n)[_both]}).reset_index()
            _sup = _old_n.notna() & _new_n.isna()
            new_suppression = pd.DataFrame({"hospital": _c.loc[_sup, _name], "earlier": _e.loc[_sup, _score],
                                            "current": _c.loc[_sup, _score]}).reset_index()
            _pub = _old_n.isna() & _new_n.notna()
            newly_published = pd.DataFrame({"hospital": _c.loc[_pub, _name], "earlier": _e.loc[_pub, _score],
                                            "current": _c.loc[_pub, _score]}).reset_index()
        else:
            number_changes = new_suppression = newly_published = pd.DataFrame()
    else:
        added = removed = changes_by_column = period_changes = pd.DataFrame()
        number_changes = new_suppression = newly_published = pd.DataFrame()
        period_hospitals = 0
    return (added, changes_by_column, new_suppression, newly_published, number_changes, period_changes,
            period_hospitals, removed)


@app.cell(hide_code=True)
def _(added, changes_by_column, earlier_name, mo, new_suppression, newly_published, number_changes,
      period_changes, period_hospitals, removed):
    def _t(df):
        return mo.ui.table(df, page_size=8, selection=None) if len(df) else mo.md("_None._")

    summary = (f"Comparing **{earlier_name}** with the current layer: {len(added)} hospitals added, "
               f"{len(removed)} removed, {len(number_changes)} with a different score, "
               f"{period_hospitals} with a different reporting period, "
               f"{len(new_suppression)} newly suppressed, {len(newly_published)} newly published.")
    mo.vstack([
        mo.md("## 4. What changed"),
        mo.md(summary),
        mo.accordion({
            f"Rows added ({len(added)})": _t(added),
            f"Rows removed ({len(removed)})": _t(removed),
            f"Columns that changed, and in how many hospitals ({len(changes_by_column)})": _t(changes_by_column),
            f"Period changes ({len(period_changes)} kinds)": _t(period_changes),
            f"Hospitals whose score changed ({len(number_changes)})": _t(number_changes),
            f"New suppression: had a number, now doesn't ({len(new_suppression)})": _t(new_suppression),
            f"Newly published: had no number, now does ({len(newly_published)})": _t(newly_published),
        }, multiple=True),
    ])
    return (summary,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. What it means for your app

    A diff is a list; your report says what it **means**. For each kind of change, decide:

    - **Period moved forward:** your app's labels and your week-5 defense name a period. Are they now wrong?
    - **Score changed:** is the change bigger than you'd expect from one more quarter of data? Check one
      hospital against the source page before you believe it.
    - **New suppression:** a hospital that disappears from your chart has not improved or closed; it lost
      its number. Does your app say so?
    - **Rows added or removed:** did your row counts in the app's panel change? They should.

    > **Ask your AI:** *"Here is the summary of changes between two versions of my data layer: [paste the
    > summary line and the tables]. Draft a half-page 'what changed' note for a hospital manager. List
    > every number you use and which table it came from, so I can check each one."*

    > **Ask your AI:** *"My week-3 layer has these extra columns: [paste]. Add them to the `checks`
    > function in this marimo cell [paste the cell's code], one check per column, and keep the earlier and
    > current columns side by side."*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** a short "what changed" report: which source you refreshed (with its provenance row),
    the before-and-after checks table, and what the changes mean for your app. If you used the simulated
    snapshot, say so, and say when you will rerun it on a real refresh.

    **The one check:** pick one hospital from "Hospitals whose score changed" (or "New suppression") and
    confirm the current value on the source page yourself.

    **Human sign-off** (three lines in the cell below). AI can help you draft this; make sure every claim is one you can explain live, without the AI open.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - What I checked myself:
    - What I'm trusting the AI on:
    - What I won't sign:
    """)
    return


if __name__ == "__main__":
    app.run()
