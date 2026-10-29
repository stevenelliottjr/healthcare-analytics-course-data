# Week 3: Build the aggregator (guided, in class)

**Notebook:** [week03_build_aggregator.py](../notebooks/week03_build_aggregator.py) · [Course home](../README.md)

## Why this week matters

A hospital file lists counties by *name*, while CDC county data uses five-digit *FIPS codes*. To ask "do hospitals in high-diabetes counties do worse?", you have to connect the two, and every connection loses something. The course crosswalk matches 5,338 of 5,419 hospitals to a county. Sixty-five are in territories such as Puerto Rico and Guam that aren't in the CDC county files, and 16 need a check by hand because of typos in the CMS file ("JEFFRSON DAVIS", "YELLOW MEDCINE"). If you don't count rows at each step, you never see that loss.

## The idea

Your **aggregator** is one table at one **grain** (one row per hospital, or one row per county), built by joining your sources on a shared key. A join is where numbers quietly vanish or multiply, so after every join you record **row counts before and after** and explain any difference. This is the one week where reading the code is the lesson. The notebook shows the join and explains each line.

## In class

- Show and explain: one provenance record each, focusing on the data period.
- Concept: grain, keys, the four outcomes of a join (matched, unmatched left, unmatched right, duplicated).
- Breakouts: build the layer together, step by step, in the notebook.

## Your one required deliverable

A joined table at **one grain**, built from your 2–3 sources, with a clear **key for every join** (the hospital ID, or the crosswalk from hospital to county), plus a short **join log**: for each join, the row count before, the row count after, and one sentence explaining any change.

## Steps

1. Run the [week 3 notebook](../notebooks/week03_build_aggregator.py) and follow the guided join. Decide your grain (one row per hospital, or per county) before you start.
2. Swap in your own sources. Ask your AI tool:
   > In this marimo notebook, join [source A] to [source B] on [key]. Use a left join so I keep every [hospital/county]. Before and after the join, print the row count. Then print how many rows did not find a match, and show five of them.
3. Ask it to check that the grain held:
   > Check whether [key] is still unique after the join. If any value appears more than once, show me those rows and explain why.
4. Look at the unmatched rows yourself. Are they territories, typos, or Connecticut? Write your join log.

## The check to run before you submit

Is your key **still unique** after the last join? If you started with one row per hospital, you should still have one row per hospital.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **The full agent workflow** (Claude Code or another coding agent): write a short project-instructions file that states the data rule, your grain and "always print row counts after joins". Use plan mode so the agent shows its plan before it changes anything, then have a second agent session audit the first one's join and report what it would question.
- Fix the 16 "check by hand" hospitals yourself and document each decision.

## Reading

None this week.
