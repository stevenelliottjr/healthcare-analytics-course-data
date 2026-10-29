# Week 4: Verify the sourcing

**Notebook:** [week04_verify_sourcing.py](../notebooks/week04_verify_sourcing.py) · [Course home](../README.md)

## Why this week matters

Suppose your layer says a Connecticut county has an adult diabetes estimate of some value. Which file did that come from, which row, which column, and was it the crude or the age-adjusted estimate? PLACES publishes both for every county. If you can't trace a number to one cell in a source file, you can't defend it, and you can't spot when an AI step changed it.

## The idea

**Verification** means checking that the numbers in your layer are exactly what the source says, with nothing added, dropped or shifted along the way. You do it two ways:

1. **Trace**: pick a number in your layer and find the same value in the original file, by key.
2. **Inspect**: look for the kinds of errors that creep into files, such as duplicates, impossible values, codes that lost their leading zeros, and text where numbers should be.

## In class

- Show and explain: four or five of you show a join ledger. What disappeared, and why?
- Concept: tracing a number; common file defects; why "Not Available" is not zero.
- Breakouts: hunt for planted errors in a practice file together.

## Your one required deliverable

1. **Trace three numbers** from your layer back to the source file: file, line, column, raw text, and reporting period.
2. **Find the planted errors** in the provided practice file (`lab03_hospitals.csv`, loaded in the notebook). For each kind of error: what is wrong, how many rows, how you found it, and what it would break.

## Steps

1. Run the [week 4 notebook](../notebooks/week04_verify_sourcing.py).
2. **Part A, trace.** Choose the **Source file** (Unplanned Hospital Visits or HRRP), **State**, **Hospital**, **Measure** and **Column**. The notebook shows the number as it sits in your layer next to the source row (file, line in the file, raw text, period, footnote), plus a state average and every row behind it. Copy the trace block it gives you. Do this three times, using hospitals and measures from your layer.
3. For a number Part A doesn't cover (a PLACES or ACS value, for example), use the **Ask your AI** box under Part A, then open the file yourself at that line.
4. **Part B, planted errors.** Use the five tools: **1** row counts, **2** Facility IDs that appear more than once, **3** format check (pick a column), **4** value distribution side by side (pick a column), **5** compare one hospital to the clean file (type a Facility ID exactly as it appears). The tools find things; you decide what each one means.
5. Remember that duplicate rows also change the counts in Tool 4. Which differences are *not* explained by duplicates?
6. Write your findings in the **My findings** box. AI can help you word them, but each one must be something you can explain live.

## The check to run before you submit

For one of your three traces, open the source CSV yourself at the line number shown and read the raw text with your own eyes. Does it match **exactly**, including decimals? If it doesn't, explain where it changed.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Ask a second AI tool (or a fresh session) to look for planted errors independently, then compare its list with yours. What did each of you miss?
- Use the notebook's second **Ask your AI** box to turn your findings into a `check(df)` cell that fails on the practice file and passes on the clean one.
- Turn your three traces into a cell that re-checks them automatically every time the notebook runs.

## Reading

Optional, about 25 minutes: Kahn et al. (2016), the "Results" section on conformance, completeness and plausibility, plus the definitions of verification and validation. See [READINGS.md](../READINGS.md).
