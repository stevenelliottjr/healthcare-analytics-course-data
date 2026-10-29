# Week 11: Check the AI's answers

**Notebook:** [week11_check_answers.py](../notebooks/week11_check_answers.py) · [Course home](../README.md)

## Why this week matters

Your agent answered three questions well last week. Would you let it answer a hospital CEO's question unsupervised? Maryland has two "Baltimore" rows in PLACES, Baltimore County (24005) and Baltimore city (24510), and PLACES names drop the word "city". Ask an agent about "Baltimore" and it may silently pick one. You only find failures like this by asking questions whose answers you already know.

## The idea

A **test set** is a list of questions with **known answers**. Run the agent on every question, compare, and sort its mistakes: wrong number, wrong period, treated a suppressed value as zero, answered a question the data can't answer, or refused one it could. The point is not a score. The point is knowing *where* and *why* it fails.

The [week 11 notebook](../notebooks/week11_check_answers.py) gives you ten questions about the **course default layer** (the one week 10 uses by default) and computes the true answer to each from the layer itself. They include easy lookups, an aggregation, a join, and traps: Connecticut, suppressed values, a period mismatch, release year vs. data year, and one question the data can't answer.

## In class

- Show and explain: four or five of you show one agent answer, with its source traced.
- Concept: test questions, known answers, kinds of failure, and why you can't let the AI grade itself unchecked.
- Breakouts: run the ten questions on your agents and compare verdicts with a partner.

## Your one required deliverable

The downloaded **scorecard** (ten questions, your agent's answers, your verdicts) and a short paragraph: **where your agent is wrong, and why**, with one sentence for every wrong answer.

## Steps

1. **Section 1.** Ask your week 10 agent each of the ten questions, **in a fresh chat each time** (paste the brief first), using the same AI tool as week 10. The questions are about the course default layer, so use the brief week 10 makes for the default layer (no upload). Run each SQL it writes in week 10's query box.
2. **Section 2.** Record the final answer it gave you for each question, and tick **"named the source and period"** where it did. Turn on the demo switch if you want to see how scoring works with made-up answers first.
3. **Section 3, the scorecard.** The notebook scores each answer. Turn on **"Show the known answers"** only after you've recorded your agent's answers.
4. **Section 4, your verdict.** The scorer matches numbers and key words, and it can be fooled. Read every answer yourself and overrule it where it's wrong. Then use **Download the scorecard** (`week11_scorecard.csv`).
5. **Section 5, why.** For each wrong answer, decide whether the fix lives in the brief, the layer or the question, and write your "why" sentence. The notebook's **Ask your AI** box can help you find the one line to add to your brief. You make the final call.

## The check to run before you submit

Pick one question the scorer marked **correct** and confirm it yourself in the layer. A scorer can be wrong too.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Fix one failure (change the agent brief), rerun all ten, and report whether anything else broke.
- If your agent uses your own layer, write five more test questions for it with the notebook's second **Ask your AI** prompt, including one about a suppressed value and one about a reporting period, and work out each answer yourself. A "Baltimore" question is a good trap.
- Have a second AI model grade the agent's answers against the known answers, then check where the grader disagrees with you.

## Reading

About 20 minutes: Hamel Husain, *Your AI Product Needs Evals* (2024). See [READINGS.md](../READINGS.md).
