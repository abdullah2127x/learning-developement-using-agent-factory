# OpenAI Agents SDK — Streaming

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)
Verified: 2026-03-04 against live Gemini + OpenRouter via OpenAIChatCompletionsModel

---

## Overview

`Runner.run_streamed()` returns a `RunResultStreaming` object. Iterate with `.stream_events()` to receive events as they're produced.

```python
from agents import Runner

result = Runner.run_streamed(agent, "input text")

async for event in result.stream_events():
    # process events here
    pass

# After stream completes, access full result
print(result.final_output)
```

**Signature** (same params as `Runner.run()`):
```python
Runner.run_streamed(
    agent,
    input,
    context=None,
    max_turns=10,
    run_config=None,      # Works with RunConfig (custom providers)
    session=None,          # Works with SQLiteSession (conversation history)
)
```

---

## Event Types

Three event types from `.stream_events()`:

| Event Type | `event.type` value | When It Fires | Use For |
|------------|-------------------|---------------|---------|
| Raw response | `"raw_response_event"` | Every LLM token delta | Token-level streaming to UI |
| Run item | `"run_item_stream_event"` | When an item is fully complete | Progress updates (tool called, message done) |
| Agent updated | `"agent_updated_stream_event"` | When a handoff occurs | Multi-agent UI updates |

**IMPORTANT**: Not all events have the same attributes. Always use `getattr()` or `hasattr()` for safe access.

---

## ToolCallItem Attribute Access (CRITICAL)

**BUG WARNING**: `ToolCallItem` does NOT have a `.name` attribute directly. The tool name is on `.raw_item.name`:

```python
# WRONG — crashes with AttributeError
if event.item.type == "tool_call_item":
    print(event.item.name)  # AttributeError: 'ToolCallItem' object has no attribute 'name'

# CORRECT — access via raw_item
if event.item.type == "tool_call_item":
    tool_name = getattr(event.item.raw_item, "name", "tool")
    print(f"[Calling: {tool_name}]")
```

**ToolCallItem attributes:**
- `event.item.type` → `"tool_call_item"` (always present)
- `event.item.raw_item` → The underlying `ResponseFunctionToolCall` object
- `event.item.raw_item.name` → The tool function name (e.g. `"list_todos"`)
- `event.item.raw_item.arguments` → JSON string of arguments
- `event.item.raw_item.call_id` → Unique call ID
- `event.item.description` → Optional description (may be None)

---

## Text Delta Access (Provider Compatibility)

Different providers return different delta formats. Use the safe pattern:

```python
# WRONG — only works with native OpenAI Responses API
if hasattr(data, "type") and data.type == "response.output_text.delta":
    print(data.delta)

# CORRECT — works with ALL providers (OpenAI, Gemini, OpenRouter)
if hasattr(data, "delta") and isinstance(data.delta, str):
    print(data.delta, end="", flush=True)
```

**Why**: When using `OpenAIChatCompletionsModel` (Gemini, OpenRouter), the delta event format differs from native OpenAI's Responses API. The safe `hasattr + isinstance` check works universally.

---

## Pattern 1: CLI Streaming with Tools (Recommended)

Complete pattern for CLI agents with tool calls, streaming, session, and error handling. **This is the production-tested pattern.**

```python
import asyncio
from agents import Agent, Runner, OpenAIChatCompletionsModel, SQLiteSession, function_tool
from agents.run import RunConfig
from openai import AsyncOpenAI

# Provider setup (works with Gemini, OpenRouter, or any OpenAI-compatible API)
client = AsyncOpenAI(api_key=settings.api_key, base_url="https://openrouter.ai/api/v1")
model = OpenAIChatCompletionsModel(model="google/gemini-2.5-flash", openai_client=client)
run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)

@function_tool
def my_tool(query: str) -> str:
    """Search for something."""
    return f"Result for: {query}"

agent = Agent(name="Assistant", instructions="Be helpful.", model=model, tools=[my_tool])

async def main():
    session = SQLiteSession("my_chat", "chat_history.db")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        print("Agent: ", end="", flush=True)

        try:
            result = Runner.run_streamed(
                agent, user_input, run_config=run_config, session=session
            )

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

            print("\n")

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                print("Rate limit hit. Please wait and try again.\n")
            else:
                print(f"Error: {error_msg}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Pattern 2: Simple Token Streaming (No Tools)

Minimal streaming for agents without tools:

```python
result = Runner.run_streamed(agent, user_input, run_config=run_config)

async for event in result.stream_events():
    if event.type == "raw_response_event":
        data = event.data
        if hasattr(data, "delta") and isinstance(data.delta, str):
            print(data.delta, end="", flush=True)

print()  # newline after stream
```

---

## Pattern 3: Item-Level Streaming (Progress Tracking)

React to complete items — best for tool call monitoring and progress:

```python
from agents import Runner, ItemHelpers

result = Runner.run_streamed(agent, user_input)

async for event in result.stream_events():
    if event.type == "raw_response_event":
        continue  # skip low-level deltas

    elif event.type == "agent_updated_stream_event":
        print(f"[Switched to agent: {event.new_agent.name}]")

    elif event.type == "run_item_stream_event":
        item = event.item
        if item.type == "tool_call_item":
            tool_name = getattr(item.raw_item, "name", "tool")
            print(f"[Calling tool: {tool_name}]")
        elif item.type == "tool_call_output_item":
            print(f"[Tool result: {item.output[:100]}]")
        elif item.type == "message_output_item":
            text = ItemHelpers.text_message_output(item)
            print(f"[Assistant]: {text}")
```

---

## Pattern 4: FastAPI Streaming Endpoint (SSE)

Stream agent output via Server-Sent Events to a frontend:

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from agents import Agent, Runner, ItemHelpers
import json

app = FastAPI()
agent = Agent(name="Assistant", instructions="Be helpful.", model="gpt-4o-mini")

@app.post("/stream")
async def stream_agent(request: Request):
    body = await request.json()
    user_input = body.get("message", "")

    async def event_generator():
        result = Runner.run_streamed(agent, user_input)
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                data = event.data
                if hasattr(data, "delta") and isinstance(data.delta, str):
                    payload = json.dumps({"type": "delta", "text": data.delta})
                    yield f"data: {payload}\n\n"

            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    tool_name = getattr(event.item.raw_item, "name", "tool")
                    payload = json.dumps({"type": "tool_call", "name": tool_name})
                    yield f"data: {payload}\n\n"
                elif event.item.type == "message_output_item":
                    text = ItemHelpers.text_message_output(event.item)
                    payload = json.dumps({"type": "message_complete", "text": text})
                    yield f"data: {payload}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## RunResultStreaming Properties

After the stream completes:

```python
result = Runner.run_streamed(agent, input)
async for event in result.stream_events():
    pass  # consume stream first

# Then access:
result.final_output          # str or output_type instance
result.new_items             # list[RunItem] — all items generated this run
result.last_agent            # Agent that produced final output
result.input                 # original input
result.is_complete           # True after stream ends
```

---

## ItemHelpers

```python
from agents import ItemHelpers

# Extract plain text from a message output item
text = ItemHelpers.text_message_output(item)

# Concatenate text across all message items
full_text = ItemHelpers.text_message_outputs(result.new_items)

# Extract input text from input items
input_text = ItemHelpers.input_to_new_input_list(result.input)
```

---

## Common Bugs & Fixes

| Bug | Cause | Fix |
|-----|-------|-----|
| `AttributeError: 'ToolCallItem' object has no attribute 'name'` | `item.name` doesn't exist | Use `getattr(item.raw_item, "name", "tool")` |
| `{}` or garbage printed in output | Non-text delta events being printed | Check `hasattr(data, "delta") and isinstance(data.delta, str)` |
| `data.type == "response.output_text.delta"` doesn't match | Using OpenAIChatCompletionsModel (Gemini/OpenRouter), not native OpenAI | Use `hasattr(data, "delta")` instead of type check |
| `'AgentUpdatedStreamEvent' object has no attribute 'data'` | Not all events have `.data` | Only access `.data` on `raw_response_event` |
| Crash on rate limit (429) | No error handling around stream | Wrap in try/except, check for "429" in error message |

---

## Best Practices

1. **Always use `getattr()` for item attributes** — SDK item objects don't always have the attributes you expect. Use `getattr(item.raw_item, "name", "fallback")`.
2. **Use the safe delta check** — `hasattr(data, "delta") and isinstance(data.delta, str)` works across all providers.
3. **Wrap streaming in try/except** — Rate limits, network errors, and provider issues can crash mid-stream.
4. **`flush=True` on print** — Always use `print(delta, end="", flush=True)` to ensure tokens appear immediately.
5. **Works with RunConfig and SQLiteSession** — `run_streamed()` accepts the same parameters as `run()`.
6. **Don't access `.data` on all events** — Only `raw_response_event` has `.data`. `agent_updated_stream_event` has `.new_agent`. `run_item_stream_event` has `.item`.
