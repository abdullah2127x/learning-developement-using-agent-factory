"""
Level 1: Hello World Agent — OpenAI Agents SDK
==============================================
Simplest possible agent. No tools, no complexity.

Requirements:
    pip install openai-agents

Environment:
    OPENAI_API_KEY set in .env or shell
"""

import asyncio
from agents import Agent, Runner


# ── Define agent (minimal) ─────────────────────────────────────────────
agent = Agent(
    name="Echo",
    instructions="Repeat what the user says verbatim.",
    model="gpt-4o-mini",
)


# ── Run ────────────────────────────────────────────────────────────────
async def main():
    user_input = input("You: ").strip()
    result = await Runner.run(agent, user_input)
    print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
