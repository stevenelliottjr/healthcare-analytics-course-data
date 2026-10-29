# Week 6: Validate the use; how an app is built and published

**Notebook:** [week06_validate_use.py](../notebooks/week06_validate_use.py) · [Course home](../README.md)

## Why this week matters

A health department wants to use county diabetes estimates from PLACES to decide where to open a new screening program, and next year to check whether the program worked. The PLACES authors caution that the estimates come from a model that doesn't account for local policies or interventions, so they can't show whether a local program worked. The data can be fine for the first job and wrong for the second. Verification asked "are the numbers right?" Validation asks "is this the right use of these numbers?"

## The idea

A **data card** is a one-page statement of what your layer is for and what it is not for: sources and periods, grain, what's excluded, known cautions, intended use, and uses you'd refuse. It's the page you hand to anyone who wants to reuse your work.

You'll also see how a marimo notebook becomes an **app**: the same notebook, with code hidden and controls showing, shared as a link. You'll sketch the one screen you want yours to have.

## In class

- Show and explain: one defended rate each. Two classmates ask first.
- Concept: verification vs. validation; data cards; how a marimo notebook runs as an app and how it gets shared.
- Breakouts: sketch app screens in pairs. Who is the reader, and what decision do they make?

## Your one required deliverable

1. Your [data card](../templates/data_card.md).
2. A **one-screen sketch** of the app you'll build in week 8: hand-drawn and photographed, or boxes in a slide. Label the reader, the one question it answers, and where provenance appears.

## Steps

1. Run the [week 6 notebook](../notebooks/week06_validate_use.py). It covers how a notebook becomes an app.
2. Draft your data card (your AI tool can help draft it). Then use it to find gaps:
   > Here is a data card for a public, county- and hospital-level dataset I built: [paste]. List the questions a skeptical reviewer would ask that this card doesn't answer. Don't rewrite it.
3. Write the "Not for" section yourself. Name at least one use you'd refuse and say why.
4. Sketch your screen. Keep it to one question, one chart or table, and one visible "where these numbers came from" note.

## The check to run before you submit

Does your card's **intended use** match your week 1 question, and does every caution on the card appear somewhere a reader of your app would see it?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Ask your AI tool to build a rough version of your sketch in marimo now, with placeholder numbers clearly labeled as placeholders.
- Show your sketch to someone outside the course and write down the first question they ask.

## Reading

About 10 minutes: Stephen Few, *Dashboard Confusion* (2004). See [READINGS.md](../READINGS.md).
