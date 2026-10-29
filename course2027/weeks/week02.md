# Week 2: Where data comes from: relevance and recency

**Notebook:** [week02_sources.py](../notebooks/week02_sources.py) · [Course home](../README.md)

## Why this week matters

Two CMS readmission files can look current and still describe different years. The HRRP file covers discharges from 07/2021–06/2024, while the 30-day readmission measures in Unplanned Hospital Visits cover 07/2023–06/2025. Put them side by side without saying so, and you're comparing different patients in different years. The same trap shows up in CDC data: the PLACES "2025 release" holds estimates for data year 2023, and the ACS county measures are a five-year average from 2017–2021.

## The idea

Before you use a source, write down its **provenance**: who published it, what one row is (the grain), the key that identifies a row, the **data period**, the date you downloaded it, and its known gaps. Release date is not data period. A file can also be the wrong one for your question even when it's recent.

**Local example:** Fairfield is in Connecticut. PLACES 2025 reports Connecticut as 9 *planning regions* (for example "Greater Bridgeport", 09120), but the ACS measures and the course crosswalk use the *old* 8 counties (for example Fairfield County, 09001). Join them by county code and Connecticut silently disappears.

## In class

- Show and explain: four or five of you show your week 1 chart and question.
- Concept: provenance, grain, data period vs. release date, relevance to your question.
- Breakouts: fill in a provenance record together for one source.

## Your one required deliverable

Choose **2–3 sources** that could answer your week 1 question, and complete one [provenance record](../templates/provenance_record.md) for each. The form at the bottom of the notebook produces one record per source.

## Steps

1. Run the [week 2 notebook](../notebooks/week02_sources.py). The **Source cards** tabs give each course source's publisher, grain, join key, row count, source page, and a reporting period computed from the data itself.
2. Read the four lessons: one file with five different periods (Unplanned Hospital Visits); HRRP vs. Unplanned Visits readmissions covering different years; release year vs. data year (PLACES and ACS); and Connecticut's planning regions.
3. Choose your sources. Ask your AI tool to help you think, but you make the decision:
   > I want to answer: "[your question]". My options are CMS Hospital General Information, CMS Unplanned Hospital Visits, CMS HRRP, CDC PLACES county data, and CDC ACS county measures. For each, tell me what one row represents and what it could and could not tell me about my question. Don't recommend one yet.
4. Pick them in **"Sources for my aggregator (choose 2–3)"**. Choose first: changing the selection clears the form.
5. In each form, check the pre-filled facts and write the judgment fields yourself: why it's relevant, whether it's recent enough, known gaps, and what you checked. Then copy the records or use **Download as .md** (`provenance_records.md`).

## The check to run before you submit

For one source, open its source page and confirm the **reporting period** yourself. Does it match what the notebook computed from the data? If not, write down which one you believe and why. Also check that the period and the date you downloaded the data are two different fields.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Look up one source outside the course list (a state health department dataset, for example) and write a provenance record for it. Confirm it's public and aggregate before you load it anywhere.
- Use the notebook's **Ask your AI** box to profile a source the notebook doesn't cover (rows, likely keys, date columns, missing-value text), then check one of its answers against the source page.

## Reading

About 30 minutes: Greenlund et al., *PLACES: Local Data for Better Health* (2022). Focus on what a model-based estimate is and the cautions about change over time. See [READINGS.md](../READINGS.md).
