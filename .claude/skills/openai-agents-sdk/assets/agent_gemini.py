"""
Gemini Agent Template — OpenAI Agents SDK
==========================================
Copy this file and modify for your use case.

Requirements:
    uv add openai-agents
    # (or: pip install openai-agents)

Environment:
    GEMINI_API_KEY set in .env (or loaded via src/config.py)
"""

import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig

# ── Import global config (type-safe, auto-completion) ────────────────────
from src.config import settings

# ── Build provider client + model wrapper ────────────────────────────────
MODEL = "gemini-2.5-flash"          # Change to gemini-2.0-flash if needed
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

client = AsyncOpenAI(
    api_key=settings.gemini_api_key,  # Type-safe access from config
    base_url=BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=client,
)

# RunConfig: applies model + disables tracing for non-OpenAI providers
run_config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

# ── Define tools (optional) ──────────────────────────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Replace with real weather API call
    return f"The weather in {city} is sunny and 25°C."


# ── Define agent ──────────────────────────────────────────────────────────
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    tools=[get_weather],            # Remove if no tools needed
    model=model,
)


# ── Run ───────────────────────────────────────────────────────────────────
async def main():
    user_input = input("You: ").strip()
    result = await Runner.run(agent, user_input, run_config=run_config)
    print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
