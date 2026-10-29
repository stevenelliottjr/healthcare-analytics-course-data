# Week 11: Check the AI's answers

**Notebook:** [week11_check_answers.py](../notebooks/week11_check_answers.py) · [Course home](../README.md)

## Why this week matters

Your agent answered three questions well last week. Would you let it answer a hospital CEO's question unsupervised? Maryland has two "Baltimore" rows in PLACES, Baltimore County (24005) and Baltimore city (24510), and PLACES names drop the word "city". Ask an agent about "Baltimore" and it may silently pick one. You only find failures like this by asking questions whose answers you already know.

## The idea

A **test set** is a list of questions with **known answers** that you worked out yourself from your layer. Run the agent on every question, compare, and sort its mistakes: wrong number, wrong source, wrong period, answered when it should have said "I don't know", or refused when it shouldn't have. The point is not a score. The point is knowing *where* and *why* it fails.

## In class

- Show and explain: one agent answer each, with its source traced.
- Concept: test questions, known answers, kinds of failure, and why you can't let the AI grade itself unchecked.
- Breakouts: swap five questions with a partner and run them on each other's agents.

## Your one required deliverable

**Ten test questions** with known answers, the agent's answer to each, and for every wrong answer one sentence on **why** it went wrong.

## Steps

1. Write ten questions. Include at least: two simple lookups, two that need a filter, two involving suppressed or "Not Available" values, two the agent should refuse, and two tricky ones (Connecticut, Baltimore, or a period mismatch).
2. Work out each answer **yourself** in the [week 11 notebook](../notebooks/week11_check_answers.py), by filtering the table, not by asking the agent.
3. Run the agent on all ten and record its answers next to yours.
4. Ask your AI tool to help sort the failures, then check its sorting:
   > Here are ten questions, my known answers, and my agent's answers: [paste]. For each mismatch, suggest which kind of failure it is: wrong number, wrong source, wrong period, should have refused, or refused wrongly. Say how confident you are. I'll make the final call.
5. Write your "why" sentence for each failure. You make the final call on each one.

## The check to run before you submit

Pick two of your known answers and re-derive them a **second way** (a different filter, or the original source file). Do they still hold?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Fix one failure (change the agent's instructions or tool), rerun all ten, and report whether anything else broke.
- Have a second AI model grade the agent's answers against your known answers, then check where the grader disagrees with you.

## Reading

About 20 minutes: Hamel Husain, *Your AI Product Needs Evals* (2024). See [READINGS.md](../READINGS.md).
