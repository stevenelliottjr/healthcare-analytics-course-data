# Week 3: Build the aggregator (guided, in class)

**Notebook:** [week03_build_aggregator.py](../notebooks/week03_build_aggregator.py) · [Course home](../README.md)

## Why this week matters

A hospital file lists counties by *name*, while CDC county data uses five-digit *FIPS codes*. To ask "do hospitals in high-diabetes counties do worse?", you have to connect the two, and every connection loses something. The course crosswalk matches 5,338 of 5,419 hospitals to a county. Sixty-five are in territories such as Puerto Rico and Guam that aren't in the CDC county files, and 16 need a check by hand because of typos in the CMS file ("JEFFRSON DAVIS", "YELLOW MEDCINE"). If you don't count rows at each step, you never see that loss.

## The idea

Your **aggregator** is one table at one **grain**, built by joining your sources on a shared key. In the course notebook the grain is **one row per hospital**: county measures are attached to each hospital through the crosswalk. A join is where numbers quietly vanish or multiply, so after every join you record **row counts before and after** and explain any difference. This is the one week where reading the code is the lesson. The notebook shows the join and explains each line.

## In class

- Show and explain: four or five of you show a provenance record, focusing on the data period.
- Concept: grain, keys, the four outcomes of a join (matched, unmatched left, unmatched right, duplicated).
- Breakouts: build the layer together, step by step, in the notebook.

## Your one required deliverable

A joined table at **one grain** (one row per hospital), built from your 2–3 sources, with a clear **key for every join** (the Facility ID, or the crosswalk from hospital to county), plus the **join ledger**: for each join, the row count, the rows matched, and one sentence explaining any gap. Submit the layer CSV and the join ledger CSV from the notebook's Export section.

## Steps

1. Run the [week 3 notebook](../notebooks/week03_build_aggregator.py). Keep it: every later week starts from the layer it builds.
2. Make your choices under **Your choices**: the **Unplanned-visits measure**; whether to keep only hospitals with a numeric score (the one step that removes rows); **Join HRRP for the same condition**; the **CDC PLACES county measures** and **PLACES value type** (crude or age-adjusted); and the **ACS county measures**. Clear both county lists for a hospital-only layer.
3. Read the build code and open **"What each line does"**. This is the one week where reading code is the lesson.
4. Read the **Join ledger**: rows should stay the same at every join; *rows matched* shows what each source actually supplied.
5. Open the **"What didn't match, and why"** tabs: hospitals with no row for the measure, rows with text instead of a number, HRRP gaps, hospitals with no county FIPS, and counties not in PLACES (Connecticut is one). Check the source pages before you explain them.
6. Set **"Lowest key match rate I will accept"** and read every FAIL in the checks table. Fix the layer, or keep your bar and say why in your submission.
7. Under **Export**, download the layer (`aggregator_<measure>.csv`, for example `aggregator_READM_30_HF.csv`) and `join_ledger.csv`. Save the layer file: you'll upload it again in weeks 7, 8, 10 and 12.
8. To add a source the notebook doesn't offer, use the **Ask your AI** box at the bottom of the notebook.

## The check to run before you submit

Pick one row of the ledger where *rows matched* is lower than *rows*, and say in one sentence who didn't match and why. Then confirm the checks table still says **one row per hospital (unique key)**.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **The full agent workflow** (Claude Code or another coding agent): write a short project-instructions file that states the data rule, your grain and "always print row counts after joins". Use plan mode so the agent shows its plan before it changes anything, then have a second agent session audit the first one's join and report what it would question.
- Fix the 16 "check by hand" hospitals yourself and document each decision.

## Reading

None this week.
