from agents import Agent, OpenAIChatCompletionsModel
from agents.run import RunConfig
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.agent_service import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)


def create_provider():
    """Create the LLM client, model wrapper, and run config."""
    client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=client,
    )

    run_config = RunConfig(
        model=model,
        model_provider=client,
        tracing_disabled=True,
    )

    return client, model, run_config


TOOLS = [list_todos, get_todo, create_todo, update_todo, delete_todo]


def create_agent(model, AGENT_INSTRUCTIONS):
    """Create the todo assistant agent with tools and instructions."""
    return Agent(
        name="Todo Assistant",
        instructions=AGENT_INSTRUCTIONS,
        tools=TOOLS,
        model=model,
    )


async def handle_stream(result):
    """Process streaming events — print text deltas and tool call progress."""
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            data = event.data
            if hasattr(data, "delta") and isinstance(data.delta, str):
                print(data.delta, end="", flush=True)

        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                tool_name = getattr(event.item.raw_item, "name", "tool")
                print(f"\n  [Calling: {tool_name}]", end="", flush=True)
            elif event.item.type == "tool_call_output_item":
                print(" -> done", end="", flush=True)

