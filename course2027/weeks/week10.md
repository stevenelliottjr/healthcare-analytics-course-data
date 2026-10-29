# Week 10: Let an agent query your aggregator

**Notebook:** [week10_agent.py](../notebooks/week10_agent.py) · [Course home](../README.md)

## Why this week matters

A public health manager types "Which counties near Bridgeport have the highest smoking rates?" and wants an answer now, not a notebook. An AI agent can answer from your layer, but only if it uses your table rather than its memory, and says where the answer came from. In Connecticut, the agent also has to cope with PLACES reporting planning regions (such as "Greater Bridgeport") rather than counties. An agent that answers confidently without a source is worse than no agent.

## The idea

An **agent** here is an AI model that is allowed to do one thing: **write a query against your layer**. The notebook, not the AI, runs the query and attaches the source and reporting period to the answer. The AI proposes, the data answers, and you check. The rules the agent is given:

1. Answer **only** from your layer, and say "I can't answer that from this data" otherwise.
2. **Name the source** and reporting period of every column it used.
3. Missing values are missing, never zero, and it says how many rows were left out.

This is the simplest thing that works, and it needs no API key: any free AI chat will do.

## In class

- Show and explain: four or five of you present your week 9 position. Which steps did people refuse to automate?
- Concept: tools, instructions, and why an agent needs to cite sources.
- Breakouts: build your agent brief, paste it into a chat, and try five questions.

## Your one required deliverable

An agent, in the [week 10 notebook](../notebooks/week10_agent.py), that answers questions from your layer and **says which source it used**. Submit the agent brief you used, your AI chat transcript, and **three questions**, each with the query, the answer, and the source and period the notebook showed. One of the three should be a question it correctly refused.

## Steps

1. Run the [week 10 notebook](../notebooks/week10_agent.py). **Section 1:** use the course default layer, or upload your own layer (your week 3 export) and paste your week 6 data card into the box.
2. **Section 2, the agent brief.** Read the column list and the brief: anything wrong in it, the agent will repeat. Copy the brief, or use **Download the brief** (`agent_brief.txt`).
3. Paste the brief into any AI chat (ChatGPT, Muse or another), then type your question under it. The AI replies with a SQL query.
4. **Section 3.** Type your question into **"The question you asked the AI"** and paste the AI's reply into the query box (just the SQL, or the whole reply). The notebook runs only one read-only query and shows the answer with the source and period of each column it used. Anything else is refused.
5. Ask three questions: one it should answer, one it should refuse (for example, what a hospital charges), and one involving a suppressed or "Not Available" value.
6. **Section 4.** Check every answer: did it follow the rules, can you read the query in plain words (ask your AI to explain it), and did it count missing values as zero?

The optional section at the end connects a chat directly with your own API key. You don't need it.

## The check to run before you submit

For one of your three answers, find the same number yourself in the layer table (week 8's app works) and say whether it matches, and whether the source the notebook showed is where that number really sits.

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **An MCP connector.** MCP (Model Context Protocol) is a standard way to give an AI tool access to data or other tools. Expose your layer through an MCP server so your own AI assistant can query it directly, read-only and public data only.
- **The full agent workflow** (Claude Code or another coding agent): a project-instructions file with your data rule and citation rule, plan mode before changes, and a second agent that audits the first agent's answers.

## Reading

About 25 minutes: Schluntz & Zhang, *Building effective agents* (Anthropic, 2024). See [READINGS.md](../READINGS.md).
