# Week 4: Verify the sourcing

**Notebook:** [week04_verify_sourcing.py](../notebooks/week04_verify_sourcing.py) · [Course home](../README.md)

## Why this week matters

Suppose your layer says a Connecticut county has an adult diabetes estimate of some value. Which file did that come from, which row, which column, and was it the crude or the age-adjusted estimate? PLACES publishes both for every county. If you can't trace a number to one cell in a source file, you can't defend it, and you can't spot when an AI step changed it.

## The idea

**Verification** means checking that the numbers in your layer are exactly what the source says, with nothing added, dropped or shifted along the way. You do it two ways:

1. **Trace**: pick a number in your layer and find the same value in the original file, by key.
2. **Inspect**: look for the kinds of errors that creep into files, such as duplicates, impossible values, codes that lost their leading zeros, and text where numbers should be.

## In class

- Show and explain: one join log each. What disappeared, and why?
- Concept: tracing a number; common file defects; why "Not Available" is not zero.
- Breakouts: hunt for planted errors in a practice file together.

## Your one required deliverable

1. **Trace three numbers** from your layer back to the source file: file, key, column, and value in both places.
2. **Find the planted errors** in the provided practice file (`lab03_hospitals.csv`, loaded in the notebook). List each one with the row and what's wrong.

## Steps

1. Run the [week 4 notebook](../notebooks/week04_verify_sourcing.py).
2. Pick three numbers from your layer, ideally one from each source. For each, ask:
   > In marimo, load the original [source] file and show me the single row where [key] = [value], with only the [column] column. Don't transform anything.
3. Compare the values yourself and write them side by side.
4. For the practice file, ask your AI tool for help **finding**, not deciding:
   > Write checks for this hospital file: duplicate IDs, IDs that aren't 6 characters, ZIP codes that lost leading zeros, numeric columns that contain text, and values outside a plausible range. Show the rows each check flags. Don't fix anything.
5. Look at each flagged row and decide: is it a real error or a legitimate oddity? Write that down.

## The check to run before you submit

For each traced number, does the value match **exactly**, including decimals and units? If it doesn't, explain where it changed.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Ask a second AI tool (or a fresh session) to look for planted errors independently, then compare its list with yours. What did each of you miss?
- Turn your three traces into a cell that re-checks them automatically every time the notebook runs.

## Reading

Optional, about 25 minutes: Kahn et al. (2016), the "Results" section on conformance, completeness and plausibility, plus the definitions of verification and validation. See [READINGS.md](../READINGS.md).
