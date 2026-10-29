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
    return io, load, mo, pd, provenance_table, to_num


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 7 — Compliance: public aggregate data vs. PHI

    Your layer is built from **public, facility-level** files: one row per hospital (or hospital x measure),
    published by CMS and CDC for anyone to download. That is very different from **patient-level** data.

    **The words, at the level this course uses them.** Under HIPAA, *protected health information* (PHI) is
    individually identifiable health information. HHS describes two ways to de-identify health information:
    **Safe Harbor** and **Expert Determination**. Look them up on the HHS de-identification guidance page
    before you rely on either; this notebook is a course check, not a legal review.

    **The lesson:** a hospital's name, address and phone number are *public facts about a facility*, not PHI.
    A patient's name, a date of birth, or a count small enough to point at a few people is a different matter.

    Run the checklist below against your layer: pick one of the course examples, or upload the CSV you
    exported from your own notebook.
    """)
    return


@app.cell(hide_code=True)
def _(load):
    hospitals = load("hospitals")
    hrrp = load("hrrp")
    uv = load("unplanned_visits")
    return hospitals, hrrp, uv


@app.cell(hide_code=True)
def _(mo):
    layer_pick = mo.ui.radio(
        options=["Example layer: HRRP joined to hospital info", "CMS Unplanned Hospital Visits", "CMS Hospital General Information",
                 "My exported CSV (upload below)"],
        value="Example layer: HRRP joined to hospital info", label="Run the checklist on")
    upload = mo.ui.file(filetypes=[".csv"], label="Upload my layer (CSV)")
    threshold = mo.ui.slider(start=1, stop=30, step=1, value=11, show_value=True, include_input=True,
                             label="Small-cell threshold (flag counts below this)")
    mo.vstack([layer_pick, upload, threshold])
    return layer_pick, threshold, upload


@app.cell(hide_code=True)
def _(hospitals, hrrp, io, layer_pick, mo, pd, upload, uv):
    _note = ""
    if layer_pick.value.startswith("My exported"):
        if upload.value:
            layer = pd.read_csv(io.BytesIO(upload.contents()), dtype=str, keep_default_na=False, encoding="utf-8-sig")
            layer_name = upload.name()
        else:
            layer = hrrp.merge(hospitals[["Facility ID", "Address", "City/Town", "ZIP Code", "County/Parish",
                                          "Telephone Number", "Hospital Type"]], on="Facility ID", how="left")
            layer_name = "example layer (no file uploaded yet)"
            _note = "**No file uploaded yet** — showing the example layer. Upload your CSV above."
    elif layer_pick.value.startswith("Example"):
        layer = hrrp.merge(hospitals[["Facility ID", "Address", "City/Town", "ZIP Code", "County/Parish",
                                      "Telephone Number", "Hospital Type"]], on="Facility ID", how="left")
        layer_name = "example layer: HRRP + hospital info"
    elif "Unplanned" in layer_pick.value:
        layer, layer_name = uv, "CMS Unplanned Hospital Visits"
    else:
        layer, layer_name = hospitals, "CMS Hospital General Information"
    mo.md(f"{_note}\n\nChecking **{layer_name}**: {len(layer):,} rows x {layer.shape[1]} columns.")
    return layer, layer_name


@app.cell(hide_code=True)
def _(layer, mo, pd):
    # Check 1 — identifier-like columns. Column NAMES and cell VALUES are both scanned.
    _patient = r"patient|member|beneficiar|mrn|medical record|ssn|social security|birth|\bdob\b|first name|last name|email|e-mail"
    _facility = r"facility|hospital|provider|address|city|zip|telephone|phone|county|state"
    _ssn = r"^\d{3}-\d{2}-\d{4}$"
    _email = r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$"
    _phone = r"^\(?\d{3}\)?[ -.]?\d{3}-?\d{4}$"
    _rows = []
    for _c in layer.columns:
        _s = layer[_c].astype(str).head(20000)
        _lc = _c.lower()
        _finds = []
        if _s.str.fullmatch(_ssn).any():
            _finds.append("SSN-like values")
        if _s.str.fullmatch(_email, case=False).any():
            _finds.append("e-mail addresses")
        if _s.str.fullmatch(_phone).any():
            _finds.append("phone numbers")
        # "Number of Patients" is an aggregate count, not an identifier, so count-style names are excluded here
        _is_count = bool(pd.Series([_lc]).str.contains(r"number of|\bcounts?\b|rate|ratio|score").iloc[0])
        _patient_name = bool(pd.Series([_lc]).str.contains(_patient).iloc[0]) and not _is_count
        _facility_name = bool(pd.Series([_lc]).str.contains(_facility).iloc[0])
        if _patient_name or "SSN-like values" in _finds or "e-mail addresses" in _finds:
            _verdict = "FAIL — looks like a person-level identifier"
        elif _facility_name and (_finds or any(k in _lc for k in ("name", "address", "phone", "telephone", "zip", "city"))):
            _verdict = "OK — public facility information (about a hospital, not a person)"
        elif _finds:
            _verdict = "CHECK — identifier-like values; whose are they?"
        else:
            continue
        _rows.append({"column": _c, "found": ", ".join(_finds) or "name looks identifying", "verdict": _verdict})
    ident = pd.DataFrame(_rows, columns=["column", "found", "verdict"])
    ident_fail = int(ident["verdict"].str.startswith("FAIL").sum())
    ident_check = int(ident["verdict"].str.startswith("CHECK").sum())
    mo.vstack([
        mo.md("## Check 1 — Identifiers\nColumns whose name or values look like identifiers, and whose they are. "
              "Hospital names, addresses and phone numbers are published by CMS for every hospital: they identify "
              "a *facility*. Anything that identifies a *patient* fails."),
        mo.ui.table(ident, selection=None) if len(ident) else mo.md("*No identifier-like columns found.*"),
    ])
    return ident, ident_check, ident_fail


@app.cell(hide_code=True)
def _(hrrp, layer, mo, pd, threshold, to_num):
    # Check 2 — small cells in COUNT columns (people or events). Counts of *measures* are not about people.
    _count = r"number of|\bcounts?\b|discharges|readmissions|patients|denominator|cases|population"
    _cols = [c for c in layer.columns if pd.Series([c.lower()]).str.contains(_count).iloc[0] and "measure" not in c.lower()]
    _t = threshold.value
    _rows = []
    for _c in _cols:
        _n = to_num(layer[_c])
        _rows.append({"count column": _c, "cells with a number": int(_n.notna().sum()),
                      f"cells from 1 to {_t - 1}": int(((_n >= 1) & (_n < _t)).sum()), "cells equal to 0": int((_n == 0).sum()),
                      "smallest non-zero": (_n[_n > 0].min() if (_n > 0).any() else None)})
    small = pd.DataFrame(_rows)
    small_fail = int(small[f"cells from 1 to {_t - 1}"].sum()) if len(small) else 0
    _r = to_num(hrrp["Number of Readmissions"])
    mo.vstack([
        mo.md("## Check 2 — Small cells\n\n"
              "A count small enough can point at a handful of people. CMS's public files suppress small counts — "
              "this is **CMS's cell-size suppression convention; confirm the current policy** before you cite a number. "
              f"You can see it in the data: in the HRRP file the smallest *Number of Readmissions* shown is **{_r.min():g}**, "
              f"and **{int(hrrp['Number of Readmissions'].eq('Too Few to Report').sum()):,}** rows say \"Too Few to Report\" "
              "instead. The default threshold here is 11 to match what the data shows; set your own if your policy "
              "differs. Zeros are listed separately: decide whether a zero in your layer could identify anyone."),
        mo.ui.table(small, selection=None) if len(small) else mo.md("*No count columns found by name. Check by hand.*"),
    ])
    return small, small_fail


@app.cell(hide_code=True)
def _(layer, mo, pd):
    # Check 3 — suppression markers preserved (not turned into blanks or zeros)
    _markers = ["Not Available", "Too Few to Report", "N/A", "Number of Cases Too Small", "Number of cases too small",
                "Not Applicable"]
    _rows = []
    for _c in layer.columns:
        _m = int(layer[_c].isin(_markers).sum())
        _b = int((layer[_c].astype(str).str.strip().isin(["", "nan", "NaN", "None"])).sum())
        if _m or _b:
            _rows.append({"column": _c, "suppression-marker cells": _m, "blank cells": _b})
    supp = pd.DataFrame(_rows, columns=["column", "suppression-marker cells", "blank cells"])
    markers_found = int(supp["suppression-marker cells"].sum()) if len(supp) else 0
    _mixed = supp[(supp["suppression-marker cells"] > 0) & (supp["blank cells"] > 0)] if len(supp) else supp
    supp_warn = len(supp) > 0 and markers_found == 0
    mo.vstack([
        mo.md("## Check 3 — Suppression markers preserved\nCMS writes *why* a value is missing (\"Too Few to Report\", "
              "\"Not Available\"). If your export shows blanks or zeros where the source had a marker, a reader can't "
              "tell \"suppressed\" from \"zero\". Blanks are not always wrong (CMS leaves Footnote blank when there is none) "
              f"— look at which columns have them. Columns with both markers and blanks: **{len(_mixed)}**."),
        mo.ui.table(supp, selection=None, page_size=10) if len(supp) else mo.md("*No markers and no blanks found.*"),
    ])
    return markers_found, supp, supp_warn


@app.cell(hide_code=True)
def _(layer, mo, pd):
    # Check 4 — what you may paste into an AI tool
    _cred = r"api[_ -]?key|password|passwd|secret|token|bearer|sk-[a-z0-9]{10,}"
    _hits = [c for c in layer.columns if pd.Series([c.lower()]).str.contains(_cred).iloc[0]]
    _hits += [c for c in layer.columns if c not in _hits and layer[c].astype(str).head(20000).str.contains(_cred, case=False).any()]
    cred_fail = len(_hits)
    attest_public = mo.ui.checkbox(label="Everything I paste into an AI tool is public, aggregate data (facility or county level)")
    attest_rows = mo.ui.checkbox(label="I never paste patient-level rows, or anything I was given under a data agreement")
    attest_cred = mo.ui.checkbox(label="I never paste passwords, API keys or tokens")
    mo.vstack([
        mo.md("## Check 4 — What you may give an AI tool\n**Course rule:** only public, aggregate data goes into any "
              "AI tool. No PHI, no row-level patient data, no credentials. Scan for credential-like text: "
              + (f"**found in {', '.join(_hits)}**" if _hits else "none found.")),
        attest_public, attest_rows, attest_cred,
    ])
    return attest_cred, attest_public, attest_rows, cred_fail


@app.cell(hide_code=True)
def _(attest_cred, attest_public, attest_rows, cred_fail, ident_check, ident_fail, layer_name, markers_found, mo,
      small_fail, supp_warn, threshold):
    def _r(ok, warn=False):
        return "PASS" if ok else ("CHECK" if warn else "FAIL")
    _rows = [
        ("No patient-level identifiers", _r(ident_fail == 0 and ident_check == 0, ident_fail == 0),
         f"{ident_fail} failing, {ident_check} to check by hand (Check 1)"),
        (f"No small cells (counts 1 to {threshold.value - 1})", _r(small_fail == 0), f"{small_fail:,} small cells (Check 2)"),
        ("Suppression markers preserved", _r(not supp_warn, True),
         f"{markers_found:,} marker cells kept as text (Check 3)"),
        ("No credentials in the data", _r(cred_fail == 0), f"{cred_fail} columns flagged (Check 4)"),
        ("AI-tool rule acknowledged", _r(attest_public.value and attest_rows.value and attest_cred.value, True),
         "all three boxes ticked" if (attest_public.value and attest_rows.value and attest_cred.value) else "tick the three boxes"),
    ]
    _md = "\n".join(f"| {name} | **{res}** | {why} |" for name, res, why in _rows)
    _all = all(r[1] == "PASS" for r in _rows)
    mo.md("\n".join([
        f"## Your compliance checklist — {layer_name}", "",
        "| Check | Result | Detail |", "|---|---|---|", _md, "",
        f"**Overall: {'PASS' if _all else 'NOT YET — fix or explain each FAIL/CHECK'}.** A PASS here is a course "
        "check, not a legal opinion. Copy this table into the full checklist: "
        "[`../templates/compliance_checklist.md`](../templates/compliance_checklist.md).",
    ]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Ask your AI — fix a failing check
    > *"My data layer `layer` (public CMS hospital data) fails this check: ______. Add a marimo cell that
    > ______ (for example: replaces counts below 11 in column ______ with the text 'Suppressed (<11)', or drops
    > column ______). Keep all other values as text exactly as they are, never turn suppressed values into 0,
    > and print the row count and the number of changed cells."*

    Paste only column names and the check result into the AI tool — not patient data, not credentials.
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

    **Deliverable:** the compliance checklist for **your** layer (upload your exported CSV above), with every
    FAIL or CHECK fixed or explained, copied into `compliance_checklist.md`. Submit your AI transcript with it.

    **The one check to run:** open your exported CSV and find one suppressed value from the source. Is it still
    there as text, or did it become a blank or a zero?

    **Sign-off (write three lines in your submission):**
    - *What I checked myself:* …
    - *What I'm trusting the AI on:* …
    - *What I won't sign:* …
    """)
    return


if __name__ == "__main__":
    app.run()
