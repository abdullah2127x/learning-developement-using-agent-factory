"""
Level 4: Production-Grade Agent — OpenAI Agents SDK
===================================================
Full-featured agent: tools, guardrails, structured output, error handling,
streaming, tracing.

Requirements:
    pip install openai-agents pydantic

Environment:
    OPENAI_API_KEY set in .env
"""

import asyncio
from pydantic import BaseModel
from agents import (
    Agent, Runner, function_tool, Tracer,
    input_guardrail, output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered,
    RunContextWrapper,
)
from dotenv import load_dotenv

load_dotenv()


# ── Structured output models ───────────────────────────────────────────
class WeatherResponse(BaseModel):
    """Structured weather information."""
    city: str
    temperature: int
    condition: str
    recommendation: str


# ── Define tools ───────────────────────────────────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"sunny, 25C in {city}"


@function_tool
def get_forecast(city: str, days: int = 5) -> str:
    """Get weather forecast for the next N days."""
    return f"Sunny for the next {days} days in {city}"


# ── Define guardrails ──────────────────────────────────────────────────
@input_guardrail
async def check_input_length(
    ctx: RunContextWrapper,
    agent: Agent,
    input_text: str,
) -> GuardrailFunctionOutput:
    """Reject inputs longer than 1000 characters."""
    if len(input_text) > 1000:
        raise InputGuardrailTripwireTriggered(
            "Input is too long. Please keep it under 1000 characters."
        )
    return GuardrailFunctionOutput(passed=True)


@output_guardrail
async def check_output_safety(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    """Check if output contains sensitive information."""
    blocked_phrases = ["api_key", "password", "secret"]
    for phrase in blocked_phrases:
        if phrase.lower() in output.lower():
            return GuardrailFunctionOutput(
                passed=False,
                output_override="I cannot share sensitive information.",
            )
    return GuardrailFunctionOutput(passed=True)


# ── Define agent with all features ─────────────────────────────────────
agent = Agent(
    name="Weather Assistant",
    instructions=(
        "You are a helpful weather assistant. Help users check current "
        "weather and forecasts. Always provide recommendations based on "
        "the weather conditions."
    ),
    tools=[get_weather, get_forecast],
    output_type=WeatherResponse,      # Structured output
    input_guardrails=[check_input_length],
    output_guardrails=[check_output_safety],
    model="gpt-4o-mini",
)


# ── Run with error handling and streaming ──────────────────────────────
async def main():
    tracer = Tracer()

    try:
        user_input = input("You: ").strip()

        # Stream token-by-token
        print("\nStreaming response:")
        async for event in Runner.run_streamed(agent, user_input, tracer=tracer):
            if event.type == "text":
                print(event.text, end="", flush=True)

        print("\n")

        # Also run without streaming to get final structured output
        result = await Runner.run(agent, user_input, tracer=tracer)

        if isinstance(result.final_output, WeatherResponse):
            print(f"\n✓ Structured output received:")
            print(f"  City: {result.final_output.city}")
            print(f"  Temperature: {result.final_output.temperature}°C")
            print(f"  Condition: {result.final_output.condition}")
            print(f"  Recommendation: {result.final_output.recommendation}")

        # Print trace for observability
        print(f"\nExecution trace: {tracer.get_trace()}")

    except InputGuardrailTripwireTriggered as e:
        print(f"Input blocked: {e}")
    except OutputGuardrailTripwireTriggered as e:
        print(f"Output blocked: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
