"""
OpenRouter Agent Template — OpenAI Agents SDK
==============================================
Copy this file and modify for your use case.
OpenRouter lets you switch models (OpenAI, Anthropic, Gemini, Meta) from one API.

Requirements:
    uv add openai-agents
    # (or: pip install openai-agents)

Environment:
    OPENROUTER_API_KEY set in .env (or loaded via src/config.py)
"""

import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig

# ── Import global config (type-safe, auto-completion) ────────────────────
from src.config import settings

# ── Pick a model ──────────────────────────────────────────────────────────
# Uncomment the model you want to use:
MODEL = "stepfun/step-3.5-flash:free"               # OpenAI — fast, cheap
# MODEL = "anthropic/claude-3-5-sonnet"    # Anthropic — smart, versatile
# MODEL = "google/gemini-2.0-flash"        # Google — cost-effective
# MODEL = "meta-llama/llama-3.2-3b-instruct:free"  # Meta — FREE
# Full list: https://openrouter.ai/docs/models

BASE_URL = "https://openrouter.ai/api/v1"

# ── Build provider client + model wrapper ────────────────────────────────
client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=settings.openrouter_api_key,  # Type-safe access from config
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
