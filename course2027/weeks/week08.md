# Week 8: Midterm: app v1 on your aggregator

**Notebook:** [week08_app_starter.py](../notebooks/week08_app_starter.py) · [Course home](../README.md) · [Rubric](../templates/app_rubric.md)

## Why this week matters

A quality director doesn't open notebooks. She opens a link, picks her hospital or county, and reads one answer. If that answer is wrong, or right but impossible to trace, the app does harm with a professional look. This week your layer becomes something a non-technical reader can use, and you show that you know its numbers are right.

## The idea

Your app is your week 6 sketch, built: one question, one main view, controls instead of code, and provenance a reader can see. Keep it small. A single screen you can fully defend beats three screens you can't.

## In class

- **Midterm showcase.** Each student shows their app and gives a **5-minute explanation of how you know its numbers are right**: trace one number on screen, name what's excluded and why, and say what you decided that the AI could not.
- Classmates ask questions. That's part of the grade, for both sides.

## Your one required deliverable

1. A **working app** on your aggregator, shared as a link that opens for a classmate.
2. A **5-minute explanation** in class, with a few notes or one slide, of how you know its numbers are right.

Graded with the [app rubric](../templates/app_rubric.md) (midterm column).

## Steps

1. Start from the [week 8 app starter](../notebooks/week08_app_starter.py). It has the four parts every app in this course needs: filters, a chart, the table of rows behind the chart, and an always-visible **"Where these numbers came from"** panel (sources, reporting periods, rows shown out of how many, and why the rest were left out).
2. **Choose your layer.** Option A, the course default layer, lets you swap the **CMS measure** and the **CDC PLACES county measure**. Option B: upload your week 3 export (`aggregator_<measure>.csv`) and the app uses it instead.
3. Set the controls: **Number to chart**, **Compare against** (or a histogram), **States** and **Hospital types**. Read the panel: do the row counts add up, and do you agree with every exclusion reason?
4. Make it answer *your* question with the notebook's **Ask your AI** prompts (change the chart, add a filter, choose the period columns). After every change, check that the panel's row counts still add up and one number in the table still matches the source file.
5. Ask for an honest review:
   > Look at this app as a hospital board member who doesn't code. What would confuse you? What would you not trust? List problems only; don't fix them.
6. Fix what matters. Then rehearse: pick one number on screen and trace it to the source file in under a minute.
7. Share it as an app (section 3 of the notebook: in molab, **"Run as app"** from the share button; locally, `marimo run`). Open the link in a private browser window to make sure it works.

## The check to run before you submit

Choose a number on your app **at random** (not one you've already checked) and trace it to the source file. If you can't do it in a few minutes, simplify the app.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **A predictive model.** Add a simple model, such as a logistic or linear regression, that relates a county measure to a hospital outcome. Report how you tested it on data it didn't see, and say in the app what it must *not* be used for. A model is just one more number to defend.
- Add a "download this table" button so readers can check your numbers themselves.

## Reading

None this week.
