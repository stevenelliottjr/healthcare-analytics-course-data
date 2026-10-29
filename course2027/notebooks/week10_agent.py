import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import re

    import duckdb
    import marimo as mo

    return duckdb, mo, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 10: let an agent query your aggregator

    **Deliverable:** an agent that answers questions from your layer and says which source it used.

    Here an "agent" is an AI that is allowed to do one thing: **write a query against your layer**.
    The notebook, not the AI, runs the query and attaches the source and reporting period to the answer.
    That split is the point: the AI proposes, the data answers, and you check.

    **The free path (no API key, any AI chat):**

    1. The notebook writes an **agent brief**: what is in your layer, what each column means, where it
       came from, and the rules the agent must follow.
    2. You paste the brief and a question into any free AI chat. It replies with a SQL query.
    3. You paste the reply into the query box below. The notebook runs it (read-only) and shows the
       answer with its source and period.

    An optional section at the end connects a chat directly, if you have an API key. You don't need it.
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

    default_layer, build_log = build_layer()
    return build_log, default_layer


@app.cell(hide_code=True)
def _(mo):
    upload = mo.ui.file(filetypes=[".csv"], label="Upload your own layer (CSV)")
    own_card = mo.ui.text_area(label="Paste your data card from week 6 (used only if you upload a layer)",
                               full_width=True, rows=6)
    mo.md(f"""
    ## 1. Which layer the agent may query

    By default this is the **course default layer**: one row per hospital, CMS hospital information +
    the CMS heart failure readmission measure (READM_30_HF) + the CDC PLACES county diabetes estimate.
    To use your own aggregator instead, upload its CSV and paste your data card.

    {upload}

    {own_card}
    """)
    return own_card, upload


@app.cell(hide_code=True)
def _(default_layer, io, mo, pd, upload):
    if upload.value:
        layer = pd.read_csv(io.BytesIO(upload.contents()), dtype=str, keep_default_na=False, encoding="utf-8-sig")
        layer_name = f"your upload: {upload.name()}"
    else:
        layer = default_layer
        layer_name = "the course default layer"
    mo.md(f"The agent will query **{layer_name}**: {len(layer):,} rows, {layer.shape[1]} columns, "
          "as a table named `layer`.")
    return layer, layer_name


@app.cell(hide_code=True)
def _(layer, pd, upload):
    # What each column means, where it came from, and which period it covers.
    # For the default layer this is known; for an upload, the student's data card says it.
    def _period(cols):
        vals = layer[list(cols)].astype(str).drop_duplicates()
        vals = vals[(vals != "").all(axis=1)]
        return "; ".join(" to ".join(r) for r in vals.itertuples(index=False, name=None)) or "(none)"

    if not upload.value:
        _cms = "CMS Unplanned Hospital Visits (632h-zaca)"
        _hosp = "CMS Hospital General Information (xubh-q36u)"
        _xw = "Course crosswalk: hospital to county FIPS"
        _pl = "CDC PLACES: County Data, 2025 release (swc5-untb)"
        _cms_p = _period(["cms_period_start", "cms_period_end"])
        _pl_p = "data year " + _period(["places_data_year"])
        _rows = [
            ("facility_id", "CMS Certification Number of the hospital (text; keep leading zeros)", _hosp, "current CMS release"),
            ("facility_name", "Hospital name", _hosp, "current CMS release"),
            ("state", "Two-letter state or territory code", _hosp, "current CMS release"),
            ("county_cms", "County name as CMS spells it (not a FIPS code)", _hosp, "current CMS release"),
            ("hospital_type", "CMS hospital type, e.g. Acute Care Hospitals", _hosp, "current CMS release"),
            ("overall_rating", "CMS overall star rating, as text: 1-5 or 'Not Available'", _hosp, "current CMS release"),
            ("cms_measure_id", "CMS measure ID (blank = hospital not in the measure file)", _cms, _cms_p),
            ("cms_measure_name", "What the CMS measure is", _cms, _cms_p),
            ("cms_score_text", "The measure score exactly as CMS publishes it, including 'Not Available'", _cms, _cms_p),
            ("cms_score", "Same score as a number; NULL when CMS did not publish a number. NULL is not zero", _cms, _cms_p),
            ("cms_denominator", "CMS denominator as published (text)", _cms, _cms_p),
            ("cms_footnote", "CMS footnote code (look up its meaning on the CMS source page)", _cms, _cms_p),
            ("cms_period_start", "Start of the CMS measurement period (MM/DD/YYYY text)", _cms, _cms_p),
            ("cms_period_end", "End of the CMS measurement period (MM/DD/YYYY text)", _cms, _cms_p),
            ("county_fips", "5-digit county FIPS from the course crosswalk (blank = no match)", _xw, "course build"),
            ("county_match_note", "How the crosswalk matched the county", _xw, "course build"),
            ("places_county_name", "County name in CDC PLACES", _pl, _pl_p),
            ("places_measure_id", "PLACES measure ID", _pl, _pl_p),
            ("places_measure", "What the PLACES measure is", _pl, _pl_p),
            ("places_value_type", "Crude or age-adjusted prevalence", _pl, _pl_p),
            ("places_data_year", "Year the PLACES estimate describes (not the release year)", _pl, _pl_p),
            ("places_value_text", "PLACES estimate as published (text; blank = county not in PLACES)", _pl, _pl_p),
            ("places_value", "Same estimate as a number (a model-based percent, not a count); NULL when missing", _pl, _pl_p),
        ]
        column_info = pd.DataFrame(_rows, columns=["column", "meaning", "source", "period"])
    else:
        column_info = pd.DataFrame([(c, "(see your data card)", "your upload (see your data card)",
                                     "(see your data card)") for c in layer.columns],
                                   columns=["column", "meaning", "source", "period"])
    _filled = (layer.notna() & layer.astype(str).apply(lambda s: s.str.strip() != "")).sum()
    column_info["non-blank rows"] = column_info["column"].map(_filled).fillna(0).astype(int)
    column_info["example"] = column_info["column"].map(
        lambda c: next((v for v in layer[c].dropna().astype(str) if v.strip()), "") if c in layer else "")
    return (column_info,)


@app.cell(hide_code=True)
def _(layer, own_card, upload):
    # The data card the agent sees. Every number here is computed from the layer.
    if upload.value:
        data_card = own_card.value.strip() or "(No data card pasted. Paste yours above before you use the brief.)"
    else:
        _has_row = layer["cms_measure_id"] != ""
        _no_pl = (layer["county_fips"] != "") & (layer["places_value_text"] == "")
        data_card = "\n".join([
            f"- Grain: one row per hospital. {len(layer):,} rows. Key: facility_id.",
            f"- {int(_has_row.sum()):,} hospitals have a row for {layer.loc[_has_row, 'cms_measure_id'].iloc[0]} "
            f"({layer.loc[_has_row, 'cms_measure_name'].iloc[0]}); {int((~_has_row).sum()):,} have no row (blank).",
            f"- Of those with a row, {int(layer['cms_score'].notna().sum()):,} have a numeric score and "
            f"{int((_has_row & layer['cms_score'].isna()).sum()):,} do not (CMS shows "
            + ", ".join(f"'{v}'" for v in sorted(layer.loc[_has_row & layer['cms_score'].isna(), 'cms_score_text'].unique()))
            + "). Those are missing, not zero.",
            f"- {int((layer['places_value_text'] != '').sum()):,} hospitals have a county PLACES value; "
            f"{int((layer['county_fips'] == '').sum()):,} have no county FIPS (territories and names to check by hand), "
            f"and {int(_no_pl.sum()):,} have a FIPS code that is not in PLACES 2025 (most in: "
            + ", ".join(layer.loc[_no_pl, "state"].value_counts().index[:5])
            + "). States with no value at all in PLACES 2025 for this measure: "
            + (", ".join(sorted(set(layer.loc[_no_pl, "state"]) - set(layer.loc[layer["places_value_text"] != "", "state"])))
               or "none")
            + ". Connecticut: PLACES 2025 uses Connecticut's planning regions, the crosswalk uses the old counties.",
            "- The CMS measure and the PLACES estimate cover different periods (see the column list).",
            "- PLACES values are model-based estimates for the whole county, not counts and not about the hospital's patients.",
        ])
    return (data_card,)


@app.cell(hide_code=True)
def _(column_info, data_card, layer, layer_name, provenance_table, upload):
    _cols = "\n".join(f"- {r.column}: {r.meaning}. Source: {r.source}. Period: {r.period}. Example: {r.example}"
                      for r in column_info.itertuples())
    _prov = provenance_table()[["source", "dataset_id", "source_page", "obtained_from", "loaded_at"]]
    _prov_txt = ("\n".join(f"- {r.source} ({r.dataset_id}), {r.source_page}, loaded {r.loaded_at} from {r.obtained_from}"
                           for r in _prov.itertuples()) if not upload.value
                 else "- See the data card above; this layer was built by the student.")
    _sample = layer.head(3).to_csv(index=False)
    agent_brief = f"""You are a data agent for a single table called `layer` ({layer_name}, {len(layer):,} rows).
You answer questions ONLY by writing one DuckDB SQL query over `layer`. You never see the data yourself;
the user runs your query and reads the result.

RULES
1. Answer only from `layer`. Do not use outside knowledge, other tables, or files.
2. Reply with exactly one read-only query (SELECT or WITH ... SELECT) in a ```sql code block.
3. After the query, one sentence naming the source and reporting period of every column you used
   (from the column list below).
4. If the question cannot be answered from these columns, do NOT write a query. Reply exactly:
   "I can't answer that from this data." and say which information is missing.
5. Missing values (NULL, blank, 'Not Available', 'Too Few to Report') are missing, never zero.
   Do not average, sum or count them as zero. Say how many rows were left out.
6. If the question asks about a period the data does not cover, say so instead of answering
   with a different period.
7. Text columns are text: compare IDs and codes as strings, e.g. facility_id = '070010'.

DATA CARD
{data_card}

COLUMNS (name: meaning. source. period. example)
{_cols}

PROVENANCE
{_prov_txt}

FIRST 3 ROWS (CSV)
{_sample}
Data rule: this is public, aggregate data. No patient-level data exists in this table.
"""
    return (agent_brief,)


@app.cell(hide_code=True)
def _(agent_brief, column_info, mo):
    mo.vstack([
        mo.md("## 2. The agent brief\n\nThe columns the agent will be told about:"),
        mo.ui.table(column_info, page_size=8, selection=None),
        mo.md("Copy the whole brief below (or download it), paste it into any AI chat, then ask your "
              "question underneath it. Read the brief first: anything wrong in it, the agent will repeat."),
        mo.download(data=agent_brief.encode("utf-8"), filename="agent_brief.txt", label="Download the brief"),
        mo.md(f"````text\n{agent_brief}\n````"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    question = mo.ui.text(label="The question you asked the AI", full_width=True)
    reply = mo.ui.code_editor(
        language="sql", min_height=140,
        placeholder="Paste the AI's reply here: just the SQL, or the whole reply (the notebook finds the ```sql block).")
    mo.md(f"""
    ## 3. Run the agent's query

    Try questions you already know something about, e.g. *"How many hospitals in Connecticut have a
    numeric heart failure readmission score?"* or *"Which five hospitals have the highest score?"*

    {question}

    {reply}

    The notebook only runs **one read-only SELECT** against `layer`. Anything else (changing data,
    reading files, more than one statement) is refused.
    """)
    return question, reply


@app.cell(hide_code=True)
def _(duckdb, layer, re):
    _BLOCKED = re.compile(
        r"\b(insert|update|delete|drop|create|alter|attach|detach|copy|export|import|pragma|install|load|"
        r"call|set|reset|vacuum|checkpoint|grant|revoke|truncate|use|begin|commit|rollback)\b"
        r"|\bread_\w+|\bglob\s*\(|\bhttp", re.I)

    def extract_sql(text):
        """Take the AI's reply and pull out the SQL (the ```sql block if there is one)."""
        m = re.search(r"```(?:sql|duckdb)?\s*\n(.*?)```", text or "", re.S | re.I)
        return (m.group(1) if m else (text or "")).strip()

    def safe_query(sql):
        """Run one read-only SELECT over `layer`. Returns (DataFrame or None, message)."""
        q = re.sub(r"--[^\n]*|/\*.*?\*/", " ", sql, flags=re.S).strip().rstrip(";").strip()
        no_strings = re.sub(r"'(?:[^']|'')*'", "''", q)
        if not q:
            return None, "No query yet."
        if not re.match(r"(select|with)\b", q, re.I):
            return None, "Refused: only a query that starts with SELECT or WITH is allowed."
        if ";" in no_strings:
            return None, "Refused: one statement only."
        bad = _BLOCKED.search(no_strings)
        if bad:
            return None, f"Refused: '{bad.group(0)}' is not allowed here (read-only, no files, no settings)."
        con = duckdb.connect(":memory:", config={"enable_external_access": False})
        try:
            con.register("layer", layer)
            con.execute("SET lock_configuration = true")
            return con.execute(q).df(), "ok"
        except Exception as e:
            return None, f"The query did not run: {type(e).__name__}: {str(e).splitlines()[0]}"
        finally:
            con.close()

    return extract_sql, safe_query


@app.cell(hide_code=True)
def _(column_info, re):
    def sources_used(sql):
        """Which columns the query mentions, and their sources and periods."""
        used = [c for c in column_info["column"] if re.search(rf"\b{re.escape(c)}\b", sql)]
        if not used:
            return column_info.iloc[0:0][["column", "source", "period"]]
        return column_info[column_info["column"].isin(used)][["column", "source", "period"]]

    return (sources_used,)


@app.cell(hide_code=True)
def _(extract_sql, mo, question, reply, safe_query, sources_used):
    _sql = extract_sql(reply.value)
    _df, _msg = safe_query(_sql)
    if _df is None:
        _out = mo.callout(mo.md(_msg), kind="neutral" if _msg == "No query yet." else "danger")
    else:
        _src = sources_used(_sql)
        _out = mo.vstack([
            mo.md(f"**Question:** {question.value or '(not recorded: type it above)'}"),
            mo.md(f"**Query that ran:**\n```sql\n{_sql}\n```"),
            mo.md(f"**Answer** ({len(_df):,} rows; showing up to 50):"),
            mo.ui.table(_df.head(50), selection=None),
            mo.callout(mo.vstack([mo.md("**Source and period of the columns this query used:**"),
                                  _src if len(_src) else mo.md("_The query used no known column._")]),
                       kind="info"),
        ])
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Check the agent, every time

    - **Did it follow the rules?** One query, named the source and period, refused what the layer can't answer.
    - **Read the query in plain words.** Ask your AI: *"Explain this SQL line by line for someone who
      doesn't code. Which rows does it leave out, and why?"*
    - **Missing is not zero.** If the query uses `cms_score`, does it say how many hospitals had no number?
    - **Try a question the layer can't answer** (e.g. what a hospital charges). A good agent says
      "I can't answer that from this data." Next week you test this systematically.

    > **Ask your AI:** *"Here is my agent brief: [paste]. Write five questions that this table cannot
    > answer but that a manager might ask anyway, and say why each can't be answered."*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    provider = mo.ui.dropdown(["anthropic", "openai", "google", "groq"], value="anthropic", label="Provider")
    model_name = mo.ui.text(label="Model name (copy it from your provider's current model list)", full_width=True)
    api_key = mo.ui.text(kind="password", label="API key (never type it into a cell or a shared file)", full_width=True)
    mo.accordion({"Optional: connect a chat directly (needs an API key; skip this if you don't have one)": mo.vstack([
        mo.md("""
        marimo has a chat element (`mo.ui.chat`) with built-in connectors for several AI providers
        (documented at https://docs.marimo.io/api/inputs/chat/). Here the chat gets the agent brief as its
        instructions; when its reply contains a ```sql block, the notebook runs that query with the same
        read-only checks as above and appends the result, so the numbers come from your layer, not the AI.

        Using an API key may cost money on your provider account, and the key is a credential: it stays
        in this box, never in the notebook file. The provider's Python package must be installed
        (marimo offers to install it the first time).
        """),
        provider, model_name, api_key,
        mo.md("If you use **Claude Code**, you can also give it the layer through an MCP connector instead of "
              "pasting the brief (optional; nothing in this notebook depends on it)."),
    ])})
    return api_key, model_name, provider


@app.cell(hide_code=True)
def _(agent_brief, api_key, extract_sql, mo, model_name, provider, safe_query):
    if api_key.value and model_name.value:
        _llm = getattr(mo.ai.llm, provider.value)(model_name.value, system_message=agent_brief,
                                                   api_key=api_key.value)

        def agent(messages, config):
            out = _llm(messages, config)
            text = out if isinstance(out, str) else "".join(str(chunk) for chunk in out)
            df, msg = safe_query(extract_sql(text)) if "```" in text else (None, "")
            if df is not None:
                text += ("\n\n**Result, run by the notebook on your layer** "
                         f"({len(df):,} rows, first 20):\n```text\n{df.head(20).to_string(index=False)}\n```")
            elif msg:
                text += f"\n\n_{msg}_"
            return text

        _chat = mo.ui.chat(agent, config={"max_tokens": 1500},
                           prompts=["How many hospitals have a numeric score, and how many don't?"])
    else:
        _chat = mo.md("_The direct chat appears here once a provider, model name and API key are filled in above._")
    _chat
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Before you submit

    **Deliverable:** your agent (the brief you used, plus the AI chat transcript) and three questions it
    answered from your layer, each with the query, the answer, and the source and period the notebook showed.
    Include one question it correctly refused.

    **The one check:** for one of the three answers, find the same number yourself in the layer table
    (week 8's app works) and say whether it matches.

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
