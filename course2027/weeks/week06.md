# Week 6: Validate the use; how an app is built and published

**Notebook:** [week06_validate_use.py](../notebooks/week06_validate_use.py) · [Course home](../README.md)

## Why this week matters

A health department wants to use county diabetes estimates from PLACES to decide where to open a new screening program, and next year to check whether the program worked. The PLACES authors caution that the estimates come from a model that doesn't account for local policies or interventions, so they can't show whether a local program worked. The data can be fine for the first job and wrong for the second. Verification asked "are the numbers right?" Validation asks "is this the right use of these numbers?"

## The idea

A **data card** is a one-page statement of what your layer is for and what it is not for: sources and periods, grain, what's excluded, known cautions, intended use, and uses you'd refuse. It's the page you hand to anyone who wants to reuse your work.

You'll also see how a marimo notebook becomes an **app**: the same notebook, with code hidden and controls showing, shared as a link. You'll sketch the one screen you want yours to have.

## In class

- Show and explain: four or five of you defend your rate. The two classmates named last week ask first.
- Concept: verification vs. validation; data cards; how a marimo notebook runs as an app and how it gets shared.
- Breakouts: sketch app screens in pairs. Who is the reader, and what decision do they make?

## Your one required deliverable

1. Your [data card](../templates/data_card.md).
2. A **one-screen sketch** of the app you'll build in week 8: hand-drawn and photographed, or boxes in a slide. Label the reader, the one question it answers, and where provenance appears.

## Steps

1. Run the [week 6 notebook](../notebooks/week06_validate_use.py) and pick **"The measure at the heart of your layer"**.
2. Read sections 1–3: **whose population** the measure covers and how many hospitals have a number (the file doesn't say which patients are counted; the measure definition does); **coverage by hospital type and state**; and **county data attached to hospitals** (the ecological fallacy, plus the hospitals that get no PLACES value).
3. **Section 4, your data card.** Fill in the four boxes (what it can answer, for whom, what it can't answer, who should and shouldn't use it). The notebook adds the computed coverage. Move it into the full [data card template](../templates/data_card.md), and write the "Not for" section yourself: at least one use you'd refuse, and why. Then look for gaps:
   > Here is a data card for a public, county- and hospital-level dataset I built: [paste]. List the questions a skeptical reviewer would ask that this card doesn't answer. Don't rewrite it.
4. **Section 5, how an app is built.** Read the two-cell app: one cell makes a dropdown, the other uses its value. That's the whole idea.
5. **Section 6, your sketch.** Fill in the boxes (user, question, controls, main output, the number you'll defend, the warning the app must show), or draw it on paper or a slide.
6. **Publishing, for week 8.** Locally, `marimo run your_notebook.py` opens a notebook as an app. In molab, sharing a notebook's URL gives viewers a static preview they can copy; to share it as an app, choose **"Run as app"** from the share button on a running notebook. If molab's menus look different, trust what you see and check marimo's molab guide (docs.marimo.io/guides/molab/). Always test the link in a private browser window.

## The check to run before you submit

Open the measure definition and confirm the patient population you wrote under **"For whom"**. If you can't confirm it, write "not confirmed". Then check that every caution on your card appears somewhere on your sketch.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Use the notebook's **Ask your AI** box ("start your app") to build a rough version of your sketch in marimo now, with placeholder numbers clearly labeled as placeholders.
- Show your sketch to someone outside the course and write down the first question they ask.

## Reading

About 10 minutes: Stephen Few, *Dashboard Confusion* (2004). See [READINGS.md](../READINGS.md).
