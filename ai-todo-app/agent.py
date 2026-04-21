# # import asyncio
# # from agents.mcp import MCPServerStdio
# # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# # import time

# # from agents import (
# #     Agent,
# #     # enable_verbose_stdout_logging,
# #     SQLiteSession,
# #     AsyncOpenAI,
# #     OpenAIChatCompletionsModel,
# #     Runner,
# #     function_tool,
# #     set_tracing_disabled,
# # )
# # from agents.lifecycle import AgentHookContext, RunHooks
# # from pydantic import BaseModel

# # from app.core.config import settings

# # set_tracing_disabled(disabled=True)
# # # enable_verbose_stdout_logging()
# # # ── Model Setup (OpenRouter) ─────────────────────────────────────────────────
# # # OPENROUTER_API_KEY = settings.openrouter_api_key
# # # MODEL = "stepfun/step-3.5-flash:free"  # Change to gemini-2.0-flash if needed
# # # BASE_URL = "https://openrouter.ai/api/v1"

# # # external_client: AsyncOpenAI = AsyncOpenAI(
# # #     api_key=OPENROUTER_API_KEY, base_url=BASE_URL
# # # )

# # GEMINI_API_KEY = settings.gemini_api_key
# # MODEL = "gemini-2.5-flash"  # Change to gemini-2.0-flash if needed
# # BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# # external_client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)


# # model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
# #     model=MODEL,
# #     openai_client=external_client,
# # )


# # class LoggingRunHooks(RunHooks):
# #     """Global hooks that fire for all agents — logs timing and events."""

# #     def __init__(self):
# #         self.turn_start: float | None = None

# #     async def on_agent_start(self, context: AgentHookContext, agent: Agent) -> None:
# #         self.turn_start = time.time()
# #         print(f"\n{'─' * 50}")
# #         print(f"[HOOK] Agent started: {agent.name}")

# #     async def on_agent_end(
# #         self, context: AgentHookContext, agent: Agent, output
# #     ) -> None:
# #         elapsed = time.time() - self.turn_start if self.turn_start else 0
# #         print(f"[HOOK] Agent finished: {agent.name} ({elapsed:.2f}s)")
# #         print(f"[HOOK] Token usage: {context.usage}")
# #         print(f"{'─' * 50}")

# #     async def on_llm_start(self, context, agent, system_prompt, input_items) -> None:
# #         print(f"[HOOK] LLM call starting for {agent.name}...")

# #     async def on_llm_end(self, context, agent, response) -> None:
# #         print(f"[HOOK] LLM responded for {agent.name}")

# #     async def on_tool_start(self, context, agent, tool) -> None:
# #         print(f"[HOOK] Tool '{tool.name}' starting...")

# #     async def on_tool_end(self, context, agent, tool, result) -> None:
# #         print(f"[HOOK] Tool '{tool.name}' → {result[:80]}")


# # @function_tool
# # def get_user_info(name: str) -> str:
# #     """Returns user profile info. In a real app, this would query a database."""
# #     # This intentionally returns PII to demonstrate the output guardrail catching it
# #     fake_data = {
# #         "alice": "Alice Smith, email: alice@example.com, phone: 555-0123",
# #         "bob": "Bob Jones, email: bob@corp.com",
# #     }
# #     return fake_data.get(name.lower(), f"No user found with name: {name}")


# # # Add Context7 as stdio MCP server (free, local)
# # context7_server = MCPServerStdio(
# #     name="Context7 MCP",
# #     params={
# #         "command": "npx",
# #         "args": ["@upstash/context7-mcp@latest"],
# #         "env": {}  # Add any env vars if needed
# #     },
# #     cache_tools_list=True
# # )

# # playwright_server = MCPServerStdio(
# #     name="Playwright MCP",
# #     params={
# #         "command": "npx",
# #         "args": ["@playwright/mcp@latest"],
# #         "env": {}
# #     },
# #     cache_tools_list=True
# # )
# # agent = Agent(
# #     name="Guarded Assistant",
# #     instructions=("You are a helpful assistant"),
# #     model=model,
# # )

# # agent.mcp_server = [context7_server, playwright_server]

# # async def main():
# #     session = SQLiteSession("free_mcp_session")  # Free local storage
# #     while True:
# #         user_input = input("You: ").strip()
# #         if not user_input:
# #             continue
# #         if user_input.lower() in ("quit", "exit"):
# #             print("Goodbye!")
# #             break


# #         result = await Runner.run(
# #             agent,
# #             user_input,
# #             session=session,

# #         )
# #         print(f"\nAssistant: {result.final_output}\n")


# # if __name__ == "__main__":
# #     asyncio.run(main())


# import asyncio

# from agents.mcp import MCPServerStdio

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# import time

# from agents import (
#     Agent,
#     AsyncOpenAI,
#     ModelSettings,
#     OpenAIChatCompletionsModel,
#     Runner,
#     # enable_verbose_stdout_logging,
#     SQLiteSession,
#     function_tool,
#     set_tracing_disabled,
# )
# from agents.lifecycle import AgentHookContext, RunHooks
# from pydantic import BaseModel

# from app.core.config import settings  # Assuming this loads your env vars

# set_tracing_disabled(disabled=True)
# # enable_verbose_stdout_logging()

# # ── Model Setup (Gemini via OpenAI-compatible API) ────────────────────────────
# GEMINI_API_KEY = settings.gemini_api_key
# MODEL = "gemini-2.5-flash"  # Free tier; fallback to "gemini-1.5-flash-latest" if needed
# BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"  # Corrected for standard Gemini endpoint
# external_client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
# model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
#     model=MODEL,
#     openai_client=external_client,
# )


# class LoggingRunHooks(RunHooks):
#     """Global hooks that fire for all agents — logs timing and events."""

#     def __init__(self):
#         self.turn_start: float | None = None

#     async def on_agent_start(self, context: AgentHookContext, agent: Agent) -> None:
#         self.turn_start = time.time()
#         print(f"\n{'─' * 50}")
#         print(f"[HOOK] Agent started: {agent.name}")

#     async def on_agent_end(
#         self, context: AgentHookContext, agent: Agent, output
#     ) -> None:
#         elapsed = time.time() - self.turn_start if self.turn_start else 0
#         print(f"[HOOK] Agent finished: {agent.name} ({elapsed:.2f}s)")
#         print(f"[HOOK] Token usage: {context.usage}")
#         print(f"{'─' * 50}")

#     async def on_llm_start(self, context, agent, system_prompt, input_items) -> None:
#         print(f"[HOOK] LLM call starting for {agent.name}...")

#     async def on_llm_end(self, context, agent, response) -> None:
#         print(f"[HOOK] LLM responded for {agent.name}")

#     async def on_tool_start(self, context, agent, tool) -> None:
#         print(f"[HOOK] Tool '{tool.name}' starting...")

#     async def on_tool_end(self, context, agent, tool, result) -> None:
#         print(f"[HOOK] Tool '{tool.name}' → {result[:80]}")


# @function_tool
# def get_user_info(name: str) -> str:
#     """Returns user profile info. In a real app, this would query a database."""
#     # This intentionally returns PII to demonstrate the output guardrail catching it
#     fake_data = {
#         "alice": "Alice Smith, email: alice@example.com, phone: 555-0123",
#         "bob": "Bob Jones, email: bob@corp.com",
#     }
#     return fake_data.get(name.lower(), f"No user found with name: {name}")


# # Add Context7 as stdio MCP server (free, local)
# # NOTE: client_session_timeout_seconds must be high enough for npx cold starts on Windows
# context7_server = MCPServerStdio(
#     name="Context7 MCP",
#     params={
#         "command": "npx",
#         "args": ["@upstash/context7-mcp@latest"],
#         "env": {},
#     },
#     cache_tools_list=True,
#     client_session_timeout_seconds=30,
# )

# playwright_server = MCPServerStdio(
#     name="Playwright MCP",
#     params={"command": "npx", "args": ["@playwright/mcp@latest"], "env": {}},
#     cache_tools_list=True,
#     client_session_timeout_seconds=30,
# )

# agent = Agent(
#     name="Guarded Assistant",
#     instructions=(
#         "You are a helpful assistant. Always use available MCP tools (like Playwright for browser tasks or Context7 for docs) "
#         "when the query involves external operations, instead of manual instructions."
#     ),
#     model=model,
#     model_settings=ModelSettings(
#         tool_choice="required"
#     ),  # Force tool use when possible (helps with Gemini)
# )
# agent.mcp_servers = [context7_server, playwright_server]  # Fixed: Plural 'mcp_servers'


# async def main():
#     # MCP servers MUST be connected before Runner.run() can use them.
#     # Use `async with` to auto-connect and auto-disconnect on exit.
#     print("Connecting to MCP servers (this may take a moment on first run)...")
#     async with context7_server, playwright_server:
#         print("MCP servers connected!\n")
#         session = SQLiteSession("free_mcp_session")  # Free local storage
#         while True:
#             user_input = input("You: ").strip()
#             if not user_input:
#                 continue
#             if user_input.lower() in ("quit", "exit"):
#                 print("Goodbye!")
#                 break

#             try:
#                 result = await Runner.run(
#                     agent,
#                     user_input,
#                     session=session,
#                 )
#                 print(f"\nAssistant: {result.final_output}\n")
#             except Exception as e:
#                 print(f"\n[ERROR] {type(e).__name__}: {e}\n")


# if __name__ == "__main__":
#     asyncio.run(main())
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# ========================================================
#
#
#
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    # enable_verbose_stdout_logging,
    set_tracing_disabled,
)
from agents.mcp import MCPServerStdio, MCPServerStreamableHttp

from app.core.config import settings  # Assuming this loads your env vars

set_tracing_disabled(disabled=True)
# enable_verbose_stdout_logging()

# ── Model Setup (Gemini via OpenAI-compatible API) ────────────────────────────
GEMINI_API_KEY = settings.gemini_api_key
MODEL = "gemini-2.5-flash"  # Free tier; fallback to "gemini-1.5-flash-latest" if needed
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"  # Corrected for standard Gemini endpoint
external_client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client,
)


async def main():
    async with MCPServerStreamableHttp(
        name="my-custom-server",
        # name="custom-stdio",
        # params={
        #     "command": "fastmcp",
        #     "args": ["run", "custom_server.py:mcp"],
        # },
        # client_session_timeout_seconds=30,
        # name="custom-http",
        params={
            "url": "http://localhost:8001/mcp",
        },
        client_session_timeout_seconds=30,
    ) as server:
        # Create agent INSIDE the async with block
        agent = Agent(
            name="Assistant",
            mcp_servers=[server],
            model=model,
        )

        result = await Runner.run(agent, "What tools do you have available?")
        print(result.final_output)


asyncio.run(main())
