# Week 5: Defend one number

**Notebook:** [week05_defend_a_number.py](../notebooks/week05_defend_a_number.py) · [Course home](../README.md)

## Why this week matters

A hospital board member reads "our heart-failure readmission rate is above the national rate" and asks: out of how many patients, over what period, and compared with whom? In the CMS Unplanned Hospital Visits file, only 3,253 hospitals have a numeric value for the heart-failure readmission measure (READM_30_HF). The rest carry text such as "Not Available". In the HRRP file, some hospitals show "Too Few to Report" instead of a number of readmissions. Any honest answer has to account for those hospitals.

## The idea

Every rate has four parts you must be able to name:

- **Numerator**: what's being counted (for example, readmissions within 30 days).
- **Denominator**: out of what (for example, eligible discharges), and who's excluded.
- **Suppression**: which values are withheld or unavailable, and why. Withheld is never zero.
- **Reporting period**: the dates the rate covers. HRRP is 07/2021–06/2024, while READM_30_* in Unplanned Hospital Visits is 07/2023–06/2025.

## In class

- Show and explain: one traced number each, and the planted error you found hardest to spot.
- Concept: anatomy of a rate; suppression; why two "readmission rates" for the same hospital can differ.
- Breakouts: take one HRRP rate apart together.

## Your one required deliverable

A one-page [defend-a-number](../templates/defend_a_number.md) walkthrough of **one rate** from your layer: its numerator, denominator, suppression and reporting period. You may draft it with AI help, but you must be able to explain every line in class without the AI open.

## Steps

1. Run the [week 5 notebook](../notebooks/week05_defend_a_number.py) and use its controls to pick a hospital and measure.
2. Ask your AI tool to show you the pieces, not to explain them away:
   > For [measure] in [file], write a marimo cell that counts how many rows are numeric, how many say "Not Available", "Too Few to Report", "N/A" or other text, and shows each distinct text value with its count. Do not convert any of them to numbers.
3. Find the measure's definition on the publisher's page (linked in the notebook's "Where these numbers came from" table). Note the numerator, denominator and period yourself.
4. Ask the AI to challenge you:
   > Here is my explanation of this rate: [paste]. Ask me the five hardest questions a skeptical hospital executive would ask about it. Don't answer them.
5. Answer those questions on your page. Use the AI to help with the wording if you like, but the answers have to be ones you can give out loud.

## The check to run before you submit

Read your page aloud as if to a classmate who has never seen the file. Could they repeat back **what the rate counts, out of what, for when, and what's missing**?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Put the same hospital's heart-failure readmission figure from HRRP and from Unplanned Hospital Visits side by side, and explain in three sentences why they differ.

## Reading

About 5 minutes: the CMS page *Hospital Readmissions Reduction Program (HRRP)*. See [READINGS.md](../READINGS.md).
