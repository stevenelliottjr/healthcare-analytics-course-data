# Week 5: Defend one number

**Notebook:** [week05_defend_a_number.py](../notebooks/week05_defend_a_number.py) · [Course home](../README.md)

## Why this week matters

A hospital board member reads "our heart-failure readmission rate is above the national rate" and asks: out of how many patients, over what period, and compared with whom? In the CMS Unplanned Hospital Visits file, only 3,253 hospitals have a numeric value for the heart-failure readmission measure (READM_30_HF). The rest carry text such as "Not Available". In the HRRP file, some hospitals show "Too Few to Report" instead of a number of readmissions. Any honest answer has to account for those hospitals.

## The idea

Every rate has four parts you must be able to name:

- **Numerator**: what's being counted (for example, readmissions within 30 days). Not every file publishes it: for READM_30_HF, the Unplanned Hospital Visits file has no filled-in numerator column, and you should say so.
- **Denominator**: out of what (for example, eligible discharges), and who's excluded.
- **Suppression**: which values are withheld or unavailable, and why. Withheld is never zero.
- **Reporting period**: the dates the rate covers. HRRP is 07/2021–06/2024, while READM_30_* in Unplanned Hospital Visits is 07/2023–06/2025.

## In class

- Show and explain: four or five of you show a traced number and the planted error you found hardest to spot.
- Concept: anatomy of a rate; suppression; why two "readmission rates" for the same hospital can differ.
- Breakouts: take one HRRP rate apart together.

## Your one required deliverable

A one-page [defend-a-number](../templates/defend_a_number.md) walkthrough of **one rate** from your layer: what kind of number it is, its numerator and denominator (or why the file doesn't give them), suppression and footnotes, reporting period, how it compares, and what it does not tell you. The notebook assembles a draft page you can use. You may draft it with AI help, but you must be able to explain every line in class without the AI open.

## Steps

1. Run the [week 5 notebook](../notebooks/week05_defend_a_number.py). Choose the **Source file** (Unplanned Hospital Visits or HRRP), **State**, **Hospital** and **Measure**, ideally a number that's in your layer.
2. Read the **"Which columns hold numbers"** table before you claim a numerator or denominator. A column that exists isn't always filled in.
3. Read the facts the notebook gathers from the file (what it is, numerator and denominator, period, suppression and footnotes, how it compares, what it doesn't tell you) and the chart showing where your hospital sits.
4. Find the measure's definition and CMS's footnote list on the source page (linked in "Where these numbers came from"). Confirm the unit and the patient population yourself.
5. Fill in the three boxes: what the number means for a reader, why you believe it, and what you'd refuse to claim from it. The draft page below them combines your answers with the facts.
6. Use the **Ask your AI** box to stress-test the draft (it lists every claim and asks two skeptical-executive questions). Answer those questions on your page, in words you can say out loud.
7. Read your page aloud as if to a classmate who has never seen the file. Could they repeat back what the rate counts, out of what, for when, and what's missing?

## The check to run before you submit

Open the measure definition on the CMS source page and confirm the **unit** and the **patient population** you describe. If you can't find them, write "not confirmed" rather than guess.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Put the same hospital's heart-failure readmission figure from HRRP and from Unplanned Hospital Visits side by side, and explain in three sentences why they differ.

## Reading

About 5 minutes: the CMS page *Hospital Readmissions Reduction Program (HRRP)*. See [READINGS.md](../READINGS.md).
