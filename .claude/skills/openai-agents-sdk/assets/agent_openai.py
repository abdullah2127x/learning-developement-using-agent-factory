"""
OpenAI Agent Template — OpenAI Agents SDK
==========================================
Copy this file and modify for your use case.
Uses native OpenAI API with official SDK.

Requirements:
    pip install openai-agents

Environment:
    OPENAI_API_KEY set in .env
"""

import asyncio
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import os

load_dotenv()


# ── Define tools (optional) ────────────────────────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Replace with real weather API call
    return f"The weather in {city} is sunny and 25°C."


# ── Define agent ──────────────────────────────────────────────────────
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    tools=[get_weather],            # Remove if no tools needed
    model="gpt-4o-mini",
)


# ── Run ────────────────────────────────────────────────────────────────
async def main():
    user_input = input("You: ").strip()
    result = await Runner.run(agent, user_input)
    print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
