# Week 2: Where data comes from: relevance and recency

**Notebook:** [week02_sources.py](../notebooks/week02_sources.py) · [Course home](../README.md)

## Why this week matters

Two CMS readmission files can look current and still describe different years. The HRRP file covers discharges from 07/2021–06/2024, while the 30-day readmission measures in Unplanned Hospital Visits cover 07/2023–06/2025. Put them side by side without saying so, and you're comparing different patients in different years. The same trap shows up in CDC data: the PLACES "2025 release" holds estimates for data year 2023, and the ACS county measures are a five-year average from 2017–2021.

## The idea

Before you use a source, write down its **provenance**: who published it, what one row is (the grain), the key that identifies a row, the **data period**, the date you downloaded it, and its known gaps. Release date is not data period. A file can also be the wrong one for your question even when it's recent.

**Local example:** Fairfield is in Connecticut. PLACES 2025 reports Connecticut as 9 *planning regions* (for example "Greater Bridgeport", 09120), but the ACS measures and the course crosswalk use the *old* 8 counties (for example Fairfield County, 09001). Join them by county code and Connecticut silently disappears.

## In class

- Show and explain: week 1 charts and questions.
- Concept: provenance, grain, data period vs. release date, relevance to your question.
- Breakouts: fill in a provenance record together for one source.

## Your one required deliverable

Choose **2–3 sources** that could answer your week 1 question, and complete one [provenance record](../templates/provenance_record.md) for each.

## Steps

1. Run the [week 2 notebook](../notebooks/week02_sources.py). It lists each course source with its publisher, grain and key.
2. Choose your sources. Ask your AI tool to help you think, but you make the decision:
   > I want to answer: "[your question]". My options are CMS Hospital General Information, CMS Unplanned Hospital Visits, CMS HRRP, CDC PLACES county data, and CDC ACS county measures. For each, tell me what one row represents and what it could and could not tell me about my question. Don't recommend one yet.
3. Find each source's data period in the file or on its official page, not from the AI. Then ask:
   > Write a marimo cell that shows the distinct values of the period or date columns in this dataframe, with a count of rows for each.
4. Fill in a provenance record for each source.

## The check to run before you submit

For each source, are the **data period** and the **download date** two different fields, and did you get the period from the file or the publisher's page yourself?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Look up one source outside the course list (a state health department dataset, for example) and write a provenance record for it. Confirm it's public and aggregate before you load it anywhere.
- List every period that appears inside the Unplanned Hospital Visits file. The measures in it do not all share one period.

## Reading

About 30 minutes: Greenlund et al., *PLACES: Local Data for Better Health* (2022). Focus on what a model-based estimate is and the cautions about change over time. See [READINGS.md](../READINGS.md).
