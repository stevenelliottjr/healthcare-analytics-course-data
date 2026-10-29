# Week 12: Recency in practice

**Notebook:** [week12_refresh.py](../notebooks/week12_refresh.py) · [Course home](../README.md)

## Why this week matters

Public health data is republished on a schedule, and each release can change the periods, add or retire measures, or redraw geography. CMS's Unplanned Hospital Visits file already includes a newer hybrid hospital-wide readmission measure (Hybrid_HWR, 07/2024–06/2025), but in the course copy all 4,790 hospital rows say "Not Available". "Newest" doesn't always mean "usable". Your app is only as current as your last check.

## The idea

**Refreshing** a source means: get the newer version, record its provenance, rerun every check you've built (row counts, traces, compliance, your ten test questions), and report what changed and whether your conclusions still hold. A refresh that changes nothing is still worth reporting, because now you know.

## In class

- Show and explain: one agent failure each, and why it happened.
- Concept: release schedules, what changes between releases, and rerunning checks.
- Breakouts: refresh one source together and compare the before and after row counts.

## Your one required deliverable

**Refresh one source**, rerun your checks, and write a short **change report**: what changed (periods, row counts, measures, values), which checks still pass, and whether any number in your app changed.

## Steps

1. Run the [week 12 notebook](../notebooks/week12_refresh.py) and choose the source to refresh.
2. Update its [provenance record](../templates/provenance_record.md) with the new download date and data period.
3. Ask your AI tool to compare versions:
   > I have two versions of the same public file loaded in marimo as old and new. Compare them: row counts, columns added or removed, distinct values in the period columns, and for rows with the same key, how many values changed. Show counts, not just a summary.
4. Rerun your join log, your three traces, the compliance checklist and your ten test questions.
5. Write the change report, with AI help if you want, and check every number in it against your rerun checks.

## The check to run before you submit

Did your join's **row counts** change after the refresh? If they did, can you explain every difference?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **A gen-AI video about a health outcome, made from your own numbers.** Use any video or slide-to-video tool to make a short explainer (about a minute) on one finding from your layer. Every number on screen must come from your layer, with its source and data period shown on screen while it appears. Submit the script with each number traced. (Idea from Phil Maymin.)
- Add a "data as of" line to your app that updates from your provenance records automatically.

## Reading

None this week.
