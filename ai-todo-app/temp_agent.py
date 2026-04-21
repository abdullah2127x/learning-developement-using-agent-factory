from agents import (
    Agent,
    AgentHooks,
    AsyncOpenAI,
    ModelSettings,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    Runner,
    enable_verbose_stdout_logging,
    function_tool,
    handoff,
    set_tracing_disabled,
)

from agents.extensions.memory import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine

from pydantic import BaseModel

from app.core.config import settings

set_tracing_disabled(disabled=True)
# enable_verbose_stdout_logging()
# ── Model Setup (OpenRouter) ─────────────────────────────────────────────────

OPENROUTER_API_KEY = settings.openrouter_api_key
MODEL = "stepfun/step-3.5-flash:free"  # Change to gemini-2.0-flash if needed
BASE_URL = "https://openrouter.ai/api/v1"
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY, base_url=BASE_URL
)

# GEMINI_API_KEY = settings.gemini_api_key
# MODEL = "gemini-2.5-flash"  # Change to gemini-2.0-flash if needed
# BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# external_client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)


model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client,
)


class UserInfo(BaseModel):
    email: str


# user_info = UserInfo(email="abdullah@gmail.com", name="abdullah", city="Karachi")
user_info = UserInfo(email="abdullah@gmail.com")


# ── Tool 1: Get user profile (name, email) ──────────────────────────────────
@function_tool
def get_user_context(wrapper: RunContextWrapper[UserInfo]) -> dict:
    """Returns the user's profile: name email and city."""
    return {
        "email": wrapper.context.email,
        "name": "abdullah",
    }


# ── Tool 2: Get user's city (from their profile) ────────────────────────────
@function_tool
def get_user_city(name: str) -> str:
    """Returns the city where the user lives. Call this BEFORE get_weather when the user asks about 'my weather' without specifying a city."""
    return "Karachi" if name == "abdullah" else "Lahore"


# ── Tool 3: Get weather (needs a city name as input) ────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city. Requires a city name — if the user didn't provide one, call get_user_city first to find their city."""
    return f"The weather in {city} is sunny, 32°C"


class MyAgentHooks(AgentHooks):

    async def on_start(self, context, agent):
        print("\n===== AGENT START =====")
        print("Agent:", agent.name)
        print("Context:", context)
        print("=======================\n")
        return "Agent Started"
        

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print("\n===== LLM CALL START =====")
        print("Agent:", agent.name)

        print("\nSystem Prompt:")
        print(system_prompt)

        print("\nInput Items:")
        for item in input_items:
            print(item)

        print("==========================\n")

    async def on_llm_end(self, context, agent, response):
        print("\n===== LLM CALL END =====")
        print("Agent:", agent.name)

        print("\nLLM Raw Response:")
        print(response)

        # if SDK exposes output text
        if hasattr(response, "output_text"):
            print("\nLLM Output Text:")
            print(response.output_text)

        print("========================\n")

    async def on_tool_start(self, context, agent, tool):
        print("\n===== TOOL START =====")
        print("Agent:", agent.name)
        print("Tool Name:", tool.name)

        if hasattr(tool, "description"):
            print("Tool Description:", tool.description)

        print("======================\n")

    async def on_tool_end(self, context, agent, tool, result):
        print("\n===== TOOL END =====")
        print("Agent:", agent.name)
        print("Tool Name:", tool.name)

        print("\nTool Result:")
        print(result)

        print("=====================\n")

    async def on_end(self, context, agent, output):
        print("\n===== AGENT FINISHED =====")
        print("Agent:", agent.name)

        print("\nFinal Output:")
        print(output)

        print("==========================\n")

agent = Agent[UserInfo](
    name="user Agent",
    instructions=(
        "You help users with their profile info and weather.\n"
        "Tools available:\n"
        "- get_user_context: returns user's name and email\n"
        "- get_user_city: returns the city where the user lives\n"
        "- get_weather(city): returns weather for a specific city\n\n"
    ),
    tools=[get_user_context, get_user_city, get_weather],
    model=model,
    # name="Helper Bot",
    # instructions="You are a helpful assistant that can answer questions.",
)

agent.hooks = MyAgentHooks()


# ── Run ──────────────────────────────────────────────────────────────────────


def main():

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "quit":
            print("Goodbye!")
            break
        result = Runner.run_sync(agent, user_input, context=user_info, max_turns=10)
        print(f"\n{result.last_agent.name}: {result.final_output}\n")


if __name__ == "__main__":
    main()
