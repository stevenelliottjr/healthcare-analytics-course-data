# Week 7: Compliance: public aggregate data vs. PHI

**Notebook:** [week07_compliance.py](../notebooks/week07_compliance.py) · [Course home](../README.md)

## Why this week matters

The CMS HRRP file prints "Too Few to Report" instead of a count when a hospital has very few readmissions. That is a deliberate choice by the publisher. Small-cell rules like this exist because tiny counts in a narrow group can point toward real people, and because a rate built on a handful of cases isn't reliable. If your app back-calculates a withheld count from other columns, or shows a count that CMS chose not to show, you've undone a protection the publisher put in place. Compliance is checking, deliberately, that you haven't.

## The idea

- **PHI** (protected health information) is individually identifiable health information. **Course data is not PHI**: it's public, facility-level (hospital) or county-level aggregate data published by CMS and CDC.
- Even with public aggregate data, three things need checking:
  1. **Small cells**: respect the publisher's suppression. Never fill, back-calculate or zero out withheld values. If you cite a numeric small-cell threshold, name the policy and link the page you read. Don't take a number from memory or from an AI.
  2. **Identifiers**: your layer should hold facility and county identifiers only, never anything about a person.
  3. **What goes into an AI tool**: public, aggregate data and your own code only. No PHI, no row-level patient data, no credentials, and nothing from your workplace.

## In class

- Show and explain: four or five of you show your data card and app sketch.
- Concept: PHI vs. public aggregate data; why suppression exists; what you may paste into an AI tool.
- Breakouts: run the checklist on one classmate's layer, then on your own.

## Your one required deliverable

Pass the [compliance checklist](../templates/compliance_checklist.md) on your layer, with one line of evidence for each item: a row count, a cell output, or a sentence.

## Steps

1. Run the [week 7 notebook](../notebooks/week07_compliance.py). Try it first on the example layer (HRRP joined to hospital information) to see what each check does.
2. Under **"Run the checklist on"**, choose **My exported CSV** and upload your week 3 export (`aggregator_<measure>.csv`).
3. Read the four checks: **1 Identifiers** (hospital names, addresses and phones are public facts about a facility; anything about a patient fails), **2 Small cells** (counts below the **small-cell threshold** slider), **3 Suppression markers preserved**, and **4 What you may give an AI tool** (a credential scan plus three boxes you tick yourself).
4. The slider starts at 11 to match what the HRRP file shows. CMS's suppression convention is described in the notebook; confirm the current policy before you cite any number.
5. Fix or explain every FAIL or CHECK in the summary table. To fix one, use the notebook's **Ask your AI** box, pasting only column names and the check result.
6. Copy the summary into the full [compliance checklist](../templates/compliance_checklist.md). Review your AI transcripts from weeks 1–6 for section C, note anything you shouldn't have shared honestly, and sign it yourself.

## The check to run before you submit

Open your exported CSV and find one value the source suppressed ("Too Few to Report", "Not Available"). Is it still there as text, or did it become a blank or a zero? You'll run the same check on your app before week 8.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **Price transparency files.** Hospitals now publish machine-readable files of their prices. Download one Connecticut hospital's file from the hospital's own website, find one service, and compare the prices listed for different payers. Write down what made it hard. (Reading below.)
- Write a one-paragraph "what I would never paste into an AI tool at work" policy for your own job.

## Reading

None required. Optional for the price-transparency power-up, about 20 minutes: Kurani et al., *Early results from federal price transparency rule show difficulty in estimating the cost of care* (Peterson-KFF, 2021). See [READINGS.md](../READINGS.md).
