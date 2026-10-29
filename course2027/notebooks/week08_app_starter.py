import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import altair as alt
    import marimo as mo

    return alt, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 8: your app, version 1

    **Midterm deliverable:** a working app on top of your aggregator, shown to the class, with a
    5-minute explanation of how you know its numbers are right.

    This notebook is a starter app. It has the four parts every app in this course needs:

    1. **Filters** so a reader can narrow the data down.
    2. **A chart** of the numbers.
    3. **A table** with the actual rows behind the chart.
    4. **A "Where these numbers came from" panel** that is always on screen: the sources, the reporting
       periods, and how many hospitals were left out of the chart and why.

    Use it as it is with the course's default layer, or upload your own week-3 export. Then change it,
    with your AI tool's help, until it answers *your* question.
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
        text_cols = [c for c in layer.columns]
        layer[text_cols] = layer[text_cols].fillna("")  # blank = the join found no row (not the same as 'Not Available')
        layer["cms_score"] = to_num(layer["cms_score_text"])  # 'Not Available' -> missing, never zero
        layer["places_value"] = to_num(layer["places_value_text"])
        log = pd.DataFrame(steps, columns=["step", "rows after this step", "rows that found a match"])
        return layer, log

    return (build_layer,)


@app.cell(hide_code=True)
def _(mo, places_raw, unplanned_raw):
    upload = mo.ui.file(filetypes=[".csv"], label="Upload your week-3 export (CSV)")
    cms_pick = mo.ui.dropdown(sorted(unplanned_raw["Measure ID"].unique()), value="READM_30_HF",
                              label="CMS measure")
    places_pick = mo.ui.dropdown(sorted(places_raw["measureid"].unique()), value="DIABETES",
                                 label="CDC PLACES county measure")
    mo.md(f"""
    ## 1. Choose your layer

    **Option A, the course default layer** (nothing to do): one row per hospital, with one CMS measure
    and one county health measure. You can swap the two measures here:

    {cms_pick} {places_pick}

    **Option B, your own layer:** upload the CSV you exported in week 3. It should have one row per
    hospital. If you upload a file, the app uses it instead of the default.

    {upload}
    """)
    return cms_pick, places_pick, upload


@app.cell(hide_code=True)
def _(build_layer, cms_pick, io, mo, pd, places_pick, upload):
    default_layer, build_log = build_layer(cms_pick.value, places_pick.value)
    if upload.value:
        layer = pd.read_csv(io.BytesIO(upload.contents()), dtype=str, keep_default_na=False, encoding="utf-8-sig")
        layer_name = f"your upload: {upload.name()}"
    else:
        layer = default_layer
        layer_name = "the course default layer"
    _note = (mo.md(f"Using **{layer_name}**: {len(layer):,} rows, {layer.shape[1]} columns. "
                   "How the default layer was built (row counts after each join):")
             if not upload.value else
             mo.md(f"Using **{layer_name}**: {len(layer):,} rows, {layer.shape[1]} columns."))
    mo.vstack([_note, build_log] if not upload.value else [_note])
    return build_log, layer, layer_name


@app.cell(hide_code=True)
def _(layer, mo, to_num):
    # Columns that hold numbers worth charting (not IDs, codes, periods or the raw-text copies).
    _skip = ("fips", "zip", "year", "period", "date", "footnote", "phone", "telephone")
    _numeric = [c for c in layer.columns if to_num(layer[c]).notna().sum() > 0 and not c.endswith("_text")
                and not any(k in c.lower() for k in _skip) and not c.lower().replace(" ", "_").endswith("_id")
                and c.lower() not in ("id", "facility id")]
    _y0 = next((c for c in ["cms_score", "uv_score_num"] if c in _numeric), _numeric[0] if _numeric else None)
    _x0 = next((c for c in _numeric if c.startswith("places_") and c != "places_data_year"), "(none: show a histogram)")
    y_pick = mo.ui.dropdown(_numeric, value=_y0, label="Number to chart")
    x_pick = mo.ui.dropdown(["(none: show a histogram)"] + _numeric, value=_x0, label="Compare against")
    _state_col = next((c for c in ["state", "State"] if c in layer.columns), None)
    state_pick = mo.ui.multiselect(sorted(layer[_state_col].unique()) if _state_col else [],
                                   label="States (leave empty for all)")
    _type_col = next((c for c in ["hospital_type", "Hospital Type"] if c in layer.columns), None)
    type_pick = mo.ui.multiselect(sorted(layer[_type_col].unique()) if _type_col else [],
                                  label="Hospital types (leave empty for all)")
    return state_pick, type_pick, x_pick, y_pick


@app.cell(hide_code=True)
def _(layer, pd, state_pick, to_num, type_pick, x_pick, y_pick):
    # Filters first, then the rows the chart can use. Row counts are kept at every step.
    _state_col = next((c for c in ["state", "State"] if c in layer.columns), None)
    _type_col = next((c for c in ["hospital_type", "Hospital Type"] if c in layer.columns), None)
    filtered = layer
    if _state_col and state_pick.value:
        filtered = filtered[filtered[_state_col].isin(state_pick.value)]
    if _type_col and type_pick.value:
        filtered = filtered[filtered[_type_col].isin(type_pick.value)]

    chart_cols = [c for c in [y_pick.value, x_pick.value] if c and not c.startswith("(none")]

    def why_excluded(df, cols):
        """For each row, the first reason it can't be charted (blank = it can be)."""
        reason = pd.Series("", index=df.index, dtype=object)
        note = next((n for n in ["county_match_note", "match_note"] if n in df.columns), None)
        for c in cols:
            # The published text behind a number column: x_text (default layer) or x for x_num (week-3 export).
            src = c + "_text" if c + "_text" in df.columns else (c[:-4] if c.endswith("_num") and c[:-4] in df.columns else c)
            raw = df[src].fillna("").astype(str).str.strip()
            bad = to_num(df[c]).isna() & (reason == "")
            if c.startswith("places_") and "county_fips" in df.columns:
                fips = df["county_fips"].fillna("").astype(str)
                no_fips = bad & (fips == "")
                reason[no_fips] = ("no county FIPS (crosswalk says: " + df.loc[no_fips, note] + ")") if note else "no county FIPS"
                no_county = bad & (fips != "") & (raw == "")
                reason[no_county] = "county FIPS not found in CDC PLACES 2025"
                bad = bad & (reason == "")
            reason[bad & (raw == "")] = f"{c}: blank (the join found no row)"
            reason[bad & (raw != "")] = f"{c}: '" + raw[bad & (raw != "")] + "'"
        return reason

    _reason = why_excluded(filtered, chart_cols)
    charted = filtered[_reason == ""].copy()
    for _c in chart_cols:
        charted[_c] = to_num(charted[_c])
    _ex = filtered[_reason != ""].assign(reason=_reason[_reason != ""])
    _by = _ex.groupby("reason").size().rename("rows left out")
    if _state_col:
        _top = _ex.groupby("reason")[_state_col].agg(lambda s: ", ".join(s.value_counts().index[:3]))
        exclusions = pd.concat([_by, _top.rename("most common states")], axis=1).reset_index()
    else:
        exclusions = _by.reset_index()
    exclusions = exclusions.sort_values("rows left out", ascending=False)
    return chart_cols, charted, exclusions, filtered


@app.cell(hide_code=True)
def _(alt, chart_cols, charted):
    alt.data_transformers.disable_max_rows()
    _name = next((c for c in ["facility_name", "Facility Name"] if c in charted.columns), charted.columns[0])
    _state = next((c for c in ["state", "State"] if c in charted.columns), _name)
    _d = charted[list(dict.fromkeys([_name, _state] + chart_cols))]
    if len(chart_cols) == 2:
        chart = alt.Chart(_d).mark_circle(size=30, opacity=0.5).encode(
            x=alt.X(chart_cols[1], scale=alt.Scale(zero=False)),
            y=alt.Y(chart_cols[0], scale=alt.Scale(zero=False)),
            tooltip=[_name, _state] + chart_cols,
        ).properties(width=420, height=320, title=f"{chart_cols[0]} vs {chart_cols[1]} ({len(_d):,} rows)")
    elif chart_cols:
        chart = alt.Chart(_d).mark_bar().encode(
            x=alt.X(chart_cols[0], bin=alt.Bin(maxbins=40)), y="count()",
        ).properties(width=420, height=320, title=f"{chart_cols[0]} ({len(_d):,} rows)")
    else:
        chart = None
    return (chart,)


@app.cell(hide_code=True)
def _(chart_cols, charted, exclusions, filtered, layer, layer_name, mo, pd, provenance_table, upload):
    # The always-visible panel: sources, reporting periods, what was left out.
    if upload.value:
        _sources = mo.md(f"**Your file:** {upload.name()}, {len(layer):,} rows. Its sources are the ones in your "
                         "week-2 provenance records; name them when you present.")
    else:
        _sources = provenance_table()[["source", "dataset_id", "obtained_from", "loaded_at", "rows"]]
    _period_cols = [c for c in layer.columns if any(k in c.lower() for k in ["period", "year", "date"])]
    _periods = pd.DataFrame([dict(column=c, values=", ".join(sorted(filtered[c].astype(str).unique())[:4]))
                             for c in _period_cols])
    panel = mo.callout(mo.vstack([
        mo.md("### Where these numbers came from"),
        _sources,
        mo.md("**Reporting periods** (columns that hold a period, year or date):"),
        _periods if len(_periods) else mo.md("_No period column found. Add one: a number without a period "
                                             "can't be defended._"),
        mo.md(f"**Rows:** {len(layer):,} in {layer_name} → {len(filtered):,} after filters → "
              f"**{len(charted):,} charted**. {len(filtered) - len(charted):,} left out, and why:"),
        exclusions if len(exclusions) else mo.md("_None left out._"),
        mo.md("Left-out values are **missing, never zero**."),
    ]), kind="info")
    return (panel,)


@app.cell(hide_code=True)
def _(chart, charted, mo, panel, state_pick, type_pick, x_pick, y_pick):
    mo.vstack([
        mo.md("## 2. The app"),
        mo.hstack([y_pick, x_pick], justify="start"),
        mo.hstack([state_pick, type_pick], justify="start"),
        mo.hstack([chart if chart is not None else mo.md("_No numeric column to chart._"), panel],
                  widths=[3, 2], align="start"),
        mo.md(f"**The rows behind the chart** ({len(charted):,}):"),
        mo.ui.table(charted, page_size=10, selection=None),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Run it as an app and share it

    **On your own computer.** Open a terminal in the folder that holds this file and run

        marimo run week08_app_starter.py

    marimo opens the notebook in your browser as an app: code hidden, controls working.
    `marimo edit week08_app_starter.py` reopens it for editing.

    **In molab** (marimo's free hosted service, https://molab.marimo.io/notebooks). marimo's molab guide
    says: to share a notebook, share its URL (viewers get a static preview and can make their own copy);
    to share it as a data app, choose **"Run as app"** from the share button on a running notebook.
    If the menus look different from that description, trust what you see, and check
    https://docs.marimo.io/guides/molab/.

    Before you share: open your link in a private browser window to check a classmate can open it,
    and check the app only uses public, aggregate data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Make it yours: Ask your AI

    Paste one of these into the AI tool you use, together with the code of the cell you want changed
    (in molab or `marimo edit`, show the code of a cell with its "show code" toggle).

    > *"This is a marimo notebook cell that draws an Altair chart from a pandas DataFrame called `charted`.
    > Change it to a bar chart of the median of `cms_score` by `state`, one bar per state, sorted high to
    > low. Keep the row count in the title. Don't turn missing values into zero."*

    > *"Add a marimo dropdown that filters `layer` by `overall_rating`. Put it next to the state filter.
    > Show the number of rows before and after the filter."*

    > *"My week-3 export has these columns: [paste the column names]. Which of them should the
    > 'Where these numbers came from' panel list as reporting periods, and why?"*

    After every change, check two things yourself: the row counts in the panel still add up, and one
    number in the table still matches the source file.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** a working app link a classmate can open, and a 5-minute explanation in class of how
    you know its numbers are right.

    **The one check:** pick one hospital in your table and find its number in the original source file
    (the source page is in the panel). Say in your explanation which hospital you checked.

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
