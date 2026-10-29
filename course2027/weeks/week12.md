# Week 12: Recency in practice

**Notebook:** [week12_refresh.py](../notebooks/week12_refresh.py) · [Course home](../README.md)

## Why this week matters

Public health data is republished on a schedule, and each release can change the periods, add or retire measures, or redraw geography. CMS's Unplanned Hospital Visits file already includes a newer hybrid hospital-wide readmission measure (Hybrid_HWR, 07/2024–06/2025), but in the course copy all 4,790 hospital rows say "Not Available". "Newest" doesn't always mean "usable". Your app is only as current as your last check.

## The idea

**Refreshing** a source means: get the newer version, record its provenance, rerun every check you've built (row counts, traces, compliance, your ten test questions), and report what changed and whether your conclusions still hold. A refresh that changes nothing is still worth reporting, because now you know.

## In class

- Show and explain: four or five of you show one agent failure, and why it happened.
- Concept: release schedules, what changes between releases, and rerunning checks.
- Breakouts: run the comparison together and read the before-and-after checks.

## Your one required deliverable

**Refresh one source**, rerun your checks, and write a short **change report**: which source you refreshed (with its provenance row), the before-and-after checks table, what changed (periods, row counts, values, suppression), and what the changes mean for your app. If you used the simulated snapshot, say so, and say when you'll rerun it on a real refresh.

## Steps

1. Run the [week 12 notebook](../notebooks/week12_refresh.py). The **current** version is your layer rebuilt now from the sources the course loads today.
2. **Section 1.** Check `obtained_from` and `loaded_at` in the provenance table. "local cache" means a copy saved earlier in the `data` folder; delete that folder and rerun to force a fresh copy, and ask your instructor when the course copy was last refreshed.
3. **Section 2, the earlier version.** Upload your week 3 export (`aggregator_<measure>.csv`); the notebook then rebuilds the current layer the same way, so like is compared with like. With no upload, it uses a **SIMULATED** earlier snapshot with documented, made-up changes, and the diff should find exactly those.
4. Read **section 3** (the week 3 checks, before and after) and **section 4** (what changed: rows added and removed, columns, period changes, score changes, new suppression, newly published).
5. **Section 5.** Decide what each change means for your app, your week 5 defense and your data card. The **Ask your AI** box can draft a "what changed" note; check every number in it against the tables.
6. Update your [provenance record](../templates/provenance_record.md) with the new download date and data period. Rerun your three traces, compliance checklist and ten test questions where anything changed.

## The check to run before you submit

Pick one hospital from **"Hospitals whose score changed"** (or **"New suppression"**) and confirm its current value on the source page yourself.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **A gen-AI video about a health outcome, made from your own numbers.** Use any video or slide-to-video tool to make a short explainer (about a minute) on one finding from your layer. Every number on screen must come from your layer, with its source and data period shown on screen while it appears. Submit the script with each number traced. (Idea from Phil Maymin.)
- Add a "data as of" line to your app that updates from your provenance records automatically.

## Reading

None this week.
