# Week 1: Healthcare data, and what the human is for

**Notebook:** [week01_first_chart.py](../notebooks/week01_first_chart.py) · [Course home](../README.md)

## Why this week matters

CMS publishes a file describing 5,419 U.S. hospitals, including a "Hospital overall rating". Some hospitals have a star rating, and some have the text "Not Available". If you chart the ratings, someone has to decide what happens to the "Not Available" hospitals: drop them, show them, or footnote them. An AI tool will happily make that choice for you without saying so. This course is about noticing those choices and making them yourself.

## The idea

Public healthcare data is plentiful, but every file has a grain (what one row is), a period, and gaps. The AI can write the code. **You** decide what question to ask, which rows count, and whether the result is honest. This week you make one chart and write down the question your project will answer.

## In class

- Tour of the public sources the course uses (CMS hospital files, CDC county files) and the data rule: public, aggregate data only, and no PHI.
- Open the week 1 notebook in molab and run it top to bottom together.
- Breakouts: make a first chart and share the link with your group.

## Your one required deliverable

1. **One chart from one CMS file**, shared as a link that a classmate can open.
2. **One sentence**: the question you want your aggregator to answer (for example, "Do hospitals in counties with higher diabetes prevalence have higher heart-failure readmission rates?"). It can change later.

That's all. Don't build more.

## Steps

1. Open the [week 1 notebook](../notebooks/week01_first_chart.py) in molab and run it. Read the "Where these numbers came from" table.
2. Pick one column to chart. If you want the AI to change the chart, paste this into your AI tool along with the cell:
   > Here is a marimo cell that charts CMS Hospital General Information with altair. Change it to show [your column] by [state / hospital type]. Do not convert "Not Available" to zero. Show how many hospitals are in the chart and how many were left out, and say why they were left out.
3. Ask the AI to explain what it did:
   > Explain this code line by line in plain English for someone who doesn't code. Which rows does it drop or change?
4. Share the notebook as a link and open it in a private browser window to make sure it works for someone else.
5. Write your one-sentence question.

## The check to run before you submit

Does your chart say **how many hospitals it includes and how many it left out**? Check that the two numbers add up to the file's row count shown in the notebook.

## Human sign-off

Use the [human sign-off template](../templates/human_signoff.md):

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- Make a second version of the chart that treats "Not Available" differently, and write one line on which version is more honest.
- Install Claude Code (paid) or any other coding agent and ask it to explain the setup cell to you.

## Reading

Optional, about 5 minutes: Young & Fiedler, *What can be done to improve all-payer claims databases?* (see [READINGS.md](../READINGS.md)). It explains why so much commercial claims data isn't public.
