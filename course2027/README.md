# DATA 6900: Healthcare Analytics (Spring 2027)

Fairfield University, Dolan School of Business · Tuesdays 6:30–9:30 pm, online · for MSAIBA and Egan MPH students

## What this course is

You will build one real piece of healthcare analytics from public data and be able to stand behind it. No programming is required. An AI assistant writes and explains the code; your job is to **direct it, check it, and decide**. By the end you will have your own app and a small AI agent, both built on a data layer you assembled and can defend.

## The spine

Each week adds one layer to a single project:

1. **Aggregator**: join two or three public sources into one documented table (weeks 1–3).
2. **Verify**: trace your numbers back to the source files (weeks 4–5).
3. **Validate**: check that the data actually fits the question you're asking (week 6).
4. **Comply**: confirm that what you hold and what you share is public, aggregate and safe (week 7).
5. **Apps**: build an app on your layer (week 8), discuss the human role (week 9), add an agent and test it (weeks 10–12), then review, show and reflect (weeks 13–14).

Two themes run through every week: **relevance and recency** (is this the right data, and how old is it?) and **the human role** (which calls must a person make?).

## The standard: defend every number

For any number you show, you should be able to say:

- **where it came from**: file, publisher, the date you downloaded it, and the row it sits in;
- **what it counts**: numerator, denominator and unit;
- **what was left out, and why**: suppressed values, "Not Available" rows, rows that didn't join;
- **what period it covers**: the data period, which is not the same as the release date.

If you can't answer one of these, the number isn't ready yet. "The AI said so" is never the answer.

## The weekly rhythm

**Class night (Tuesdays)**

| Time | What happens |
|---|---|
| 6:30–7:15 | **Show and explain.** Four or five students show last week's work, explain one number, and say what they decided that the AI could not. Two classmates, named the week before, ask the first questions. |
| 7:15–8:00 | Concept for the week |
| 8:00–8:10 | Break |
| 8:10–9:15 | Guided build in breakouts |
| 9:15–9:30 | "The one check I'll run before I submit" |

**Between classes:** one small required deliverable, about 3 hours of work. Each week's brief is sized at half of what seems doable, on purpose. Everything marked **power-up** is optional.

**With each deliverable**, submit your AI transcript (see [transcript guide](templates/transcript_guide.md)) and a three-line [human sign-off](templates/human_signoff.md).

## Grading (proposed; the syllabus has the final version)

| Part | Weight |
|---|---|
| Weekly deliverables (12 count, lowest dropped) | 40% |
| AI transcripts: three are graded, chosen after you submit, on whether you directed and checked the tool | 15% |
| Midterm app and explanation (week 8) | 15% |
| Final app, showcase and reflection (week 14) | 20% |
| Class discussion and peer review | 10% |

There are no exams. You may use AI to help draft written work, including defenses and reflections, but the ideas and decisions must be yours. Your live explanation in class, without the AI open, is how that gets checked.

## Tools

- **Free tools cover all required work.**
- **marimo is where your work runs.** Every course notebook is a marimo notebook. Run it on **molab** (marimo's free hosted service), or on your own computer if you prefer. marimo can also run a notebook as an app, and that is how you'll build and share yours.
- **Any AI assistant** (ChatGPT, Muse, Claude, or another) to write and explain code. Each brief includes ready-to-paste prompts.
- **Claude Code** is optional (paid). Some power-ups use it, but nothing required does.

## The data rule (from day one)

Only **public, aggregate data** goes into any AI tool. The course data is published facility-level (hospital) or county-level data from CMS and CDC. **No PHI** (protected health information, meaning individually identifiable health information), no row-level patient data, and no passwords or credentials, ever. If you aren't sure whether something counts, don't paste it. Ask first.

## The 14 weeks

| Wk | Theme | Brief | Notebook |
|---|---|---|---|
| 1 | Healthcare data, and what the human is for | [week01](weeks/week01.md) | [week01_first_chart.py](notebooks/week01_first_chart.py) |
| 2 | Where data comes from: relevance and recency | [week02](weeks/week02.md) | [week02_sources.py](notebooks/week02_sources.py) |
| 3 | Build the aggregator (guided, in class) | [week03](weeks/week03.md) | [week03_build_aggregator.py](notebooks/week03_build_aggregator.py) |
| 4 | Verify the sourcing | [week04](weeks/week04.md) | [week04_verify_sourcing.py](notebooks/week04_verify_sourcing.py) |
| 5 | Defend one number | [week05](weeks/week05.md) | [week05_defend_a_number.py](notebooks/week05_defend_a_number.py) |
| 6 | Validate the use; how an app is built and published | [week06](weeks/week06.md) | [week06_validate_use.py](notebooks/week06_validate_use.py) |
| 7 | Compliance: public aggregate data vs. PHI | [week07](weeks/week07.md) | [week07_compliance.py](notebooks/week07_compliance.py) |
| 8 | Midterm: app v1 on your aggregator | [week08](weeks/week08.md) | [week08_app_starter.py](notebooks/week08_app_starter.py) |
| 9 | The human role (seminar) | [week09](weeks/week09.md) | none (reading and discussion) |
| 10 | Let an agent query your aggregator | [week10](weeks/week10.md) | [week10_agent.py](notebooks/week10_agent.py) |
| 11 | Check the AI's answers | [week11](weeks/week11.md) | [week11_check_answers.py](notebooks/week11_check_answers.py) |
| 12 | Recency in practice | [week12](weeks/week12.md) | [week12_refresh.py](notebooks/week12_refresh.py) |
| 13 | Peer review | [week13](weeks/week13.md) | none ([peer review template](templates/peer_review.md)) |
| 14 | Showcase and reflection | [week14](weeks/week14.md) | none |

Readings are short (most weeks have none or one, never more than about 30 minutes): see [READINGS.md](READINGS.md). Templates are in [templates/](templates/).

## How to get help

1. **Ask your AI tool first, but ask it well.** Paste the error message and the cell, then ask "What does this error mean, and what is the smallest change that fixes it?"
2. **Ask a classmate.** Breakout groups are there for exactly this.
3. **Bring it to class.** Being stuck is a fine thing to show and explain: say what you tried and where it broke.
4. **Ask the instructor.** Office hours and contact details are in the syllabus. Send the link to your notebook and one sentence on what you expected and what happened instead.

Being stuck on a number is part of the work. Write down why you're stuck. That note is often the most valuable line in your submission.
