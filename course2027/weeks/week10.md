# Week 10: Let an agent query your aggregator

**Notebook:** [week10_agent.py](../notebooks/week10_agent.py) · [Course home](../README.md)

## Why this week matters

A public health manager types "Which counties near Bridgeport have the highest smoking rates?" and wants an answer now, not a notebook. An AI agent can answer from your layer, but only if it uses your table rather than its memory, and says where the answer came from. In Connecticut, the agent also has to cope with PLACES reporting planning regions (such as "Greater Bridgeport") rather than counties. An agent that answers confidently without a source is worse than no agent.

## The idea

An **agent** here is an AI model that can call a small set of tools you give it, for example "look up a county in my table" or "list the measures I have", and then answers in words. Your rules for it:

1. Answer **only** from your layer, and say "I don't know" otherwise.
2. **Name the source** (file and data period) behind every number.
3. Never fill in suppressed or "Not Available" values.

Start with the simplest thing that works. A fixed lookup plus a sentence is often enough.

## In class

- Show and explain: one-page positions from week 9. Which steps did people refuse to automate?
- Concept: tools, instructions, and why an agent needs to cite sources.
- Breakouts: connect the notebook's agent to your layer and try five questions.

## Your one required deliverable

An agent, in the [week 10 notebook](../notebooks/week10_agent.py), that answers questions from your layer and **says which source it used**. Submit three example questions and its answers.

## Steps

1. Run the [week 10 notebook](../notebooks/week10_agent.py) and follow its setup instructions.
2. Connect it to your layer:
   > In this marimo agent notebook, replace the example table with my aggregator. Give the agent one tool that looks up rows by [key] and returns the value with its source name and data period. Instruct it to answer only from that tool, to say "I don't know" when the tool returns nothing, and never to treat "Not Available" as a number.
3. Ask it three questions: one it should answer, one it should refuse ("I don't know"), and one involving a suppressed value.
4. Check each answer against your table yourself.

## The check to run before you submit

For each of your three answers, does the **source it names** match where that number actually sits in your layer?

## Human sign-off

- What I checked myself:
- What I'm trusting the AI on:
- What I won't sign:

## Power-ups (optional)

- **An MCP connector.** MCP (Model Context Protocol) is a standard way to give an AI tool access to data or other tools. Expose your layer through an MCP server so your own AI assistant can query it directly, read-only and public data only.
- **The full agent workflow** (Claude Code or another coding agent): a project-instructions file with your data rule and citation rule, plan mode before changes, and a second agent that audits the first agent's answers.

## Reading

About 25 minutes: Schluntz & Zhang, *Building effective agents* (Anthropic, 2024). See [READINGS.md](../READINGS.md).
