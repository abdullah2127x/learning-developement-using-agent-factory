"""
LiteLLM Agent Template — OpenAI Agents SDK
===========================================
Copy this file and modify for your use case.
LiteLLM provides a unified interface for 20+ LLM providers (OpenAI, Anthropic, Gemini, Azure, etc.)

Requirements:
    uv add openai-agents litellm
    # (or: pip install openai-agents litellm)

Environment:
    LITELLM_MODEL: Model ID in "provider/model-name" format
    Provider-specific API keys (GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

See references/litellm-provider.md for complete provider list and configuration.
"""


import asyncio
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner, function_tool
from agents.run import RunConfig

from dotenv import load_dotenv
import os 

gemini_api_key = os.getenv("GEMINI_API_KEY")

# ── Pick a provider + model ────────────────────────────────────────────────
# Format: "provider/model-id"


# ──── Google Gemini (Cheapest) ─────────────────────────────────────────────
MODEL = "gemini/gemini-2.5-flash"         
API_KEY = gemini_api_key



# ── Build LiteLLM model wrapper ────────────────────────────────────────────
model = LitellmModel(
    model=MODEL,
    api_key=API_KEY,
)

# RunConfig: applies model + disables tracing for non-OpenAI providers
run_config = RunConfig(
    model=model,
    tracing_disabled=True,
)

# ── Define tools (optional) ────────────────────────────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Replace with real weather API call
    return f"The weather in {city} is sunny and 25°C."


# ── Define agent ───────────────────────────────────────────────────────────
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    tools=[get_weather],            # Remove if no tools needed
    model=model,
)

 
# ── Run ────────────────────────────────────────────────────────────────────
async def main():
    user_input = input("You: ").strip() 
    result = await Runner.run(agent, user_input, run_config=run_config)
    print(f"Agent: {result.final_output}")
 


if __name__ == "__main__":
    asyncio.run(main())
