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

1. Start from the [week 8 app starter](../notebooks/week08_app_starter.py). It's a small working app on the course data, with its provenance shown.
2. Point it at your own layer:
   > Here is my marimo app starter and my aggregator cell. Replace the example data with my table. Keep the provenance panel visible on the main screen. Add one dropdown that filters by [state / county / hospital type]. Under the chart, show "n = [rows shown] of [total rows]; [excluded] excluded because [reason]".
3. Ask for an honest review:
   > Look at this app as a hospital board member who doesn't code. What would confuse you? What would you not trust? List problems only; don't fix them.
4. Fix what matters. Then rehearse: pick one number on screen and trace it to the source file in under a minute.
5. Open the shared link in a private browser window to make sure it works.

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
