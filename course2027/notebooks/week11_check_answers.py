import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import re

    import marimo as mo

    return mo, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 11: check the AI's answers

    **Deliverable:** ten test questions with known answers; where your agent is wrong, and why.

    Last week your agent answered questions. This week you find out **how often it is right**. The method
    is old and simple: ask questions you already know the answer to.

    1. The notebook computes the true answer to ten questions **from the layer itself** (nothing typed in by hand).
    2. You ask your week-10 agent the same ten questions and record what it said.
    3. The notebook scores each answer and sorts the mistakes by kind: wrong number, wrong period,
       treated a suppressed value as zero, answered a question the data can't answer.
    4. You read every verdict and overrule the scorer where it is wrong. That is the human's job.

    The questions are about the **course default layer** (the same one week 10 uses by default).
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

    layer, build_log = build_layer()
    return build_log, layer


@app.cell(hide_code=True)
def _(SOURCES, layer, places_raw, re):
    # Ground truth, computed live from the layer. Each question also records how it is scored.
    L = layer
    _num = L["cms_score"].notna()
    _has_row = L["cms_measure_id"] != ""
    _names = dict(zip(places_raw["stateabbr"], places_raw["statedesc"]))
    _measure = L.loc[_has_row, "cms_measure_name"].iloc[0]
    _acute = L["hospital_type"] == "Acute Care Hospitals"
    _ct = L[(L["state"] == "CT") & _acute & _num].sort_values("facility_id").iloc[0]
    _ct_na = L[(L["state"] == "CT") & _acute & _has_row & ~_num].sort_values("facility_id").iloc[0]
    # The 50 states + DC (USPS codes); territories such as PR and GU are left out of "states".
    _STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ "
                  "NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
    _j = L[_num & L["places_value"].notna()].sort_values("facility_id").iloc[0]
    _by_state = L[_num].groupby("state")["cms_score"]
    _med = _by_state.median()[(_by_state.count() >= 10) & _by_state.median().index.isin(_STATES)]
    _top_state = _med.idxmax()
    _top_any = _by_state.median().idxmax()  # the answer you get if you include territories or tiny states
    _share = (L[_has_row].groupby("state")["cms_score"].apply(lambda s: s.isna().mean())
              [L[_has_row].groupby("state").size() >= 20])
    _sup_state = _share.idxmax()
    _s = L[_has_row & (L["state"] == _sup_state)]
    _mean_ok = _s["cms_score"].mean()
    _mean_zero = _s["cms_score"].fillna(0).mean()
    _ct_places = int(((L["state"] == "CT") & L["places_value"].notna()).sum())
    _y0, _y1 = _ct["cms_period_start"][-4:], _ct["cms_period_end"][-4:]
    _pl_year = L.loc[L["places_data_year"] != "", "places_data_year"].iloc[0]
    _release = re.search(r"(\d{4}) release", SOURCES["places"]["title"]).group(1)
    _place = L.loc[L["facility_id"] == _j["facility_id"], "places_county_name"].iloc[0]

    QUESTIONS = [
        dict(kind="easy lookup", rule="number", q=f"How many hospitals have a row for {_measure} but no numeric score?",
             truth=int((_has_row & ~_num).sum()), shown=f"{int((_has_row & ~_num).sum()):,}"),
        dict(kind="easy lookup", rule="number",
             q=f"What is the {_measure} score for {_ct['facility_name']} (facility_id {_ct['facility_id']})?",
             truth=float(_ct["cms_score"]), shown=_ct["cms_score_text"]),
        dict(kind="aggregation", rule="state",
             q=f"Among the 50 states and DC, counting only states with at least 10 hospitals that have a numeric "
               f"score, which state has the highest median {_measure} score?",
             truth=_top_state, name=_names.get(_top_state, ""),
             shown=f"{_top_state} {_names.get(_top_state, '')}, median {_med.max():.1f}".replace("  ", " "),
             wrong=_top_any),
        dict(kind="join", rule="number",
             q=f"What is the county diabetes estimate (CDC PLACES, age-adjusted) for the county where "
               f"{_j['facility_name']} (facility_id {_j['facility_id']}) is located?",
             truth=float(_j["places_value"]), shown=f"{_j['places_value_text']} ({_place})"),
        dict(kind="join (trap)", rule="number",
             q="How many Connecticut hospitals in the layer have a county diabetes estimate?",
             truth=_ct_places, shown=f"{_ct_places} (Connecticut hospitals don't join to PLACES 2025)"),
        dict(kind="suppressed (trap)", rule="suppressed",
             q=f"What is the {_measure} score for {_ct_na['facility_name']} (facility_id {_ct_na['facility_id']})?",
             truth=None, shown=f"No number: CMS shows '{_ct_na['cms_score_text']}'"),
        dict(kind="suppressed (trap)", rule="mean",
             q=f"What is the average {_measure} score across hospitals in {_names.get(_sup_state, _sup_state)} "
               f"({_sup_state})?",
             truth=round(float(_mean_ok), 2),
             shown=f"{_mean_ok:.2f} over {int(_s['cms_score'].notna().sum())} hospitals with a number "
                   f"({int(_s['cms_score'].isna().sum())} have none)",
             wrong=round(float(_mean_zero), 2)),
        dict(kind="period mismatch (trap)", rule="period",
             q=f"What was the {_measure} score for {_ct['facility_name']} in calendar year 2024 alone?",
             truth=float(_ct["cms_score"]),
             shown=f"Not in the layer: the only score covers {_ct['cms_period_start']} to {_ct['cms_period_end']}",
             years=(_y0, _y1)),
        dict(kind="period", rule="year", q="Which year do the county diabetes estimates describe?",
             truth=_pl_year, shown=f"{_pl_year} (data year; the release is {_release})", wrong=_release),
        dict(kind="unanswerable", rule="refuse",
             q=f"How much does a heart failure admission cost at {_ct['facility_name']}?",
             truth=None, shown="Can't be answered: the layer has no cost or payment column"),
    ]
    return (QUESTIONS,)


@app.cell(hide_code=True)
def _(QUESTIONS, mo):
    _all = "\n".join(f"{i}. {q['q']}" for i, q in enumerate(QUESTIONS, 1))
    mo.vstack([
        mo.md("## 1. Ask your agent\n\nUse the same brief and the same AI tool as week 10. Ask each question "
              "**in a fresh chat** (paste the brief first), so one answer doesn't steer the next. "
              "Run each SQL the AI writes in week 10's query box and record the final answer it gives you, "
              "plus whether it named the source and period."),
        mo.md(f"```text\n{_all}\n```"),
    ])
    return


@app.cell(hide_code=True)
def _(QUESTIONS, mo):
    answers = mo.ui.array([mo.ui.text_area(placeholder="The agent's answer, as it gave it", rows=2, full_width=True)
                           for _ in QUESTIONS])
    named = mo.ui.array([mo.ui.checkbox(label="named the source and period") for _ in QUESTIONS])
    demo = mo.ui.switch(label="Show me how scoring works with example (made-up) agent answers")
    mo.vstack([mo.md("## 2. Record the agent's answers"), demo]
              + [mo.vstack([mo.md(f"**{i}. {q['q']}**"), answers[i - 1], named[i - 1]])
                 for i, q in enumerate(QUESTIONS, 1)])
    return answers, demo, named


@app.cell(hide_code=True)
def _(re):
    REFUSE = re.compile(r"can.?t answer|can.?t be answered|cannot be answered|cannot answer|can not answer|unable to answer|not (?:in|available in|"
                        r"included in|part of) (?:the|this|my) (?:data|layer|table)|no (?:column|data|information)"
                        r" (?:on|for|about)|(?:does not|doesn't) (?:contain|include|have)|is(?: not|n't) in the", re.I)
    MISSING = re.compile(r"not available|suppress|no (?:numeric )?(?:score|number|value)|missing|null|"
                         r"not reported|(?:did not|didn't) publish|too few", re.I)

    def numbers(text):
        found = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*(?:\.\d+)?", text or "")]
        if re.search(r"\b(zero|none)\b", text or "", re.I):
            found.append(0.0)
        return found

    def close(found, target):
        tol = max(0.051, 0.005 * abs(target))
        return any(abs(f - target) <= tol for f in found)

    def score(q, text):
        """Return (verdict, explanation). A first pass for a human to check, not the final word."""
        t = (text or "").strip()
        if not t:
            return "no answer recorded", ""
        nums = numbers(t)
        refused = bool(REFUSE.search(t))
        if q["rule"] == "refuse":
            return (("correct", "refused, as it should") if refused
                    else ("answered the unanswerable", "the layer has no column for this"))
        if q["rule"] == "suppressed":
            if MISSING.search(t) or refused:
                return "correct", "said there is no number"
            if close(nums, 0):
                return "treated suppressed as zero", "a suppressed value is missing, not 0"
            return "wrong number", "there is no number to give"
        if q["rule"] == "period":
            y0, y1 = q["years"]
            if (y0 in t and y1 in t) or refused:
                return "correct", "said the score covers a different period"
            if close(nums, q["truth"]):
                return "wrong period", f"gave the {y0}-{y1} score as if it were 2024"
            return "wrong number", ""
        if q["rule"] == "year":
            if q["truth"] in t:
                return "correct", ""
            if q["wrong"] in t:
                return "wrong period", "gave the release year, not the data year"
            return "wrong number", ""
        if q["rule"] == "state":
            words = set(re.findall(r"[A-Za-z]+", t))
            if q["truth"] in words or (q["name"] and q["name"].lower() in t.lower()):
                return "correct", ""
            if refused:
                return "refused an answerable question", ""
            return "wrong number", ("ignored a condition in the question (states only, at least 10 hospitals)"
                                    if q["wrong"] in words else "")
        # numeric answers ("number" and "mean")
        if close(nums, q["truth"]):
            return "correct", ""
        if q["rule"] == "mean" and close(nums, q["wrong"]):
            return "treated suppressed as zero", "averaged missing scores in as 0"
        if refused:
            return "refused an answerable question", "the layer does have this"
        return "wrong number", ""

    return (score,)


@app.cell(hide_code=True)
def _(QUESTIONS):
    # Made-up agent answers, built from the truths, that make one of each kind of mistake.
    _q = QUESTIONS
    DEMO_ANSWERS = [
        f"{_q[0]['shown']} hospitals. Source: CMS Unplanned Hospital Visits.",
        f"The score is {_q[1]['shown']}.",
        f"{_q[2]['wrong']} has the highest median.",
        f"{_q[3]['truth']}",
        "I can't answer that from this data.",
        "0",
        f"The average is {_q[6]['wrong']}.",
        f"In 2024 it was {_q[7]['truth']}.",
        f"{_q[8]['wrong']}",
        "About $14,000 per admission.",
    ]
    return (DEMO_ANSWERS,)


@app.cell(hide_code=True)
def _(mo):
    reveal = mo.ui.switch(label="Show the known answers (record your agent's answers first)")
    reveal
    return (reveal,)


@app.cell(hide_code=True)
def _(DEMO_ANSWERS, QUESTIONS, answers, demo, mo, named, pd, reveal, score):
    _given = DEMO_ANSWERS if demo.value else answers.value
    _rows = []
    for _i, (_q, _a) in enumerate(zip(QUESTIONS, _given), 1):
        _v, _why = score(_q, _a)
        _rows.append({"#": _i, "kind": _q["kind"], "agent said": _a, "auto verdict": _v, "why": _why,
                      "named source + period": "demo" if demo.value else ("yes" if named.value[_i - 1] else "no"),
                      "known answer": _q["shown"] if reveal.value else "(hidden)"})
    scorecard = pd.DataFrame(_rows)
    _answered = scorecard[scorecard["auto verdict"] != "no answer recorded"]
    _tally = _answered["auto verdict"].value_counts().rename_axis("verdict").reset_index(name="questions")
    mo.vstack([
        mo.md("## 3. The scorecard" + ("  \n**DEMO: these are made-up answers, not your agent's.**" if demo.value else "")),
        mo.ui.table(scorecard, selection=None, page_size=10),
        mo.md(f"**{int((_answered['auto verdict'] == 'correct').sum())} of {len(_answered)} recorded answers "
              "scored correct.** Where the mistakes are:"),
        _tally,
    ])
    return (scorecard,)


@app.cell(hide_code=True)
def _(QUESTIONS, mo):
    _options = ["(agree with auto verdict)", "correct", "wrong number", "wrong period", "treated suppressed as zero",
                "answered the unanswerable", "refused an answerable question"]
    override = mo.ui.array([mo.ui.dropdown(_options, value=_options[0], label=f"Q{i}") for i in range(1, len(QUESTIONS) + 1)])
    mo.vstack([
        mo.md("""
        ## 4. Your verdict

        The scorer matches numbers and key words. It can be fooled: an answer that mentions the right number
        by accident scores "correct". **Read every answer yourself** and overrule the scorer where it is wrong.
        """),
        mo.hstack(list(override), wrap=True),
    ])
    return (override,)


@app.cell(hide_code=True)
def _(mo, override, scorecard):
    final = scorecard.copy()
    final["my verdict"] = [v if v != "(agree with auto verdict)" else a
                           for v, a in zip(override.value, final["auto verdict"])]
    _csv = final.drop(columns=["known answer"]).to_csv(index=False).encode("utf-8")
    mo.vstack([
        mo.md(f"**Final: {int((final['my verdict'] == 'correct').sum())} of {len(final)} correct.** "
              f"Overruled: {int((final['my verdict'] != final['auto verdict']).sum())}."),
        mo.download(data=_csv, filename="week11_scorecard.csv", label="Download the scorecard (CSV)"),
    ])
    return (final,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Why it was wrong

    For each wrong answer, the fix usually lives in one of three places:

    - **The brief.** Was the rule there? (e.g. "missing is never zero", "say when a period isn't covered".)
    - **The layer.** Did a column name or meaning mislead it? (e.g. a column called `score` with no period.)
    - **The question.** Was it ambiguous? Would a person have asked "which year?" first?

    > **Ask your AI:** *"My agent got this question wrong: [question]. Its SQL was [paste]. The known
    > answer is [answer]. In plain words, what did the query do differently, and what one line should I
    > add to the agent brief so it doesn't happen again?"* Then rerun the question and record whether the
    > fix worked.

    > **Ask your AI:** *"Write five more test questions about this table [paste the column list] whose answer
    > I can check myself, including one about a suppressed value and one about a reporting period."*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** the downloaded scorecard (ten questions, your agent's answers, your verdicts) and a
    short paragraph: where your agent is wrong, and why (AI can help you draft it; you should be able to explain every point live, without the AI open).

    **The one check:** pick one question the scorer marked correct and confirm it yourself in the layer.
    A scorer can be wrong too.

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
