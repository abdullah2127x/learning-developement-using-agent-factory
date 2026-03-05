# OpenAI Agents SDK — MCP Integration & Tracing

Source: openai/openai-agents-python, openai.github.io/openai-agents-python (Context7, High reputation)

---

## MCP (Model Context Protocol)

MCP servers expose external tools to agents. Three transport types:

| Type | Use When | Class |
|------|----------|-------|
| `stdio` | Local subprocess (CLI tools, filesystem) | `MCPServerStdio` |
| `streamable_http` | Remote HTTP server, custom infra | `MCPServerStreamableHttp` |
| `sse` | Legacy SSE (deprecated, avoid for new work) | `MCPServerSse` |

**Install MCP support:**
```bash
pip install openai-agents[mcp]
```

---

## stdio — Local Subprocess

```python
from pathlib import Path
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
import asyncio

async def main():
    # npx-based MCP server (filesystem example)
    async with MCPServerStdio(
        name="Filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/data"],
        },
        cache_tools_list=True,    # cache tool list to avoid re-fetching each turn
    ) as server:
        agent = Agent(
            name="File Assistant",
            instructions="Help the user work with files in the data directory.",
            mcp_servers=[server],
        )
        result = await Runner.run(agent, "List all files available.")
        print(result.final_output)

asyncio.run(main())
```

---

## Streamable HTTP — Remote Server

```python
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
import asyncio

async def main():
    async with MCPServerStreamableHttp(
        name="My API Server",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": f"Bearer {os.environ['MCP_TOKEN']}"},
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        agent = Agent(
            name="API Agent",
            instructions="Use the available MCP tools to answer questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="auto"),
        )
        result = await Runner.run(agent, "What tools do you have?")
        print(result.final_output)

asyncio.run(main())
```

---

## Multiple MCP Servers with MCPServerManager

```python
from agents import Agent, Runner
from agents.mcp import MCPServerManager, MCPServerStreamableHttp, MCPServerStdio
from pathlib import Path
import asyncio

async def main():
    servers = [
        MCPServerStreamableHttp(
            name="Calendar API",
            params={"url": "http://localhost:8001/mcp"},
        ),
        MCPServerStreamableHttp(
            name="Docs API",
            params={"url": "http://localhost:8002/mcp"},
        ),
        MCPServerStdio(
            name="Local Filesystem",
            params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.cwd())]},
        ),
    ]

    async with MCPServerManager(servers) as manager:
        # manager.active_servers = servers that connected successfully
        agent = Agent(
            name="Assistant",
            instructions="Use available tools to help the user.",
            mcp_servers=manager.active_servers,
        )
        result = await Runner.run(agent, "What can you help me with?")
        print(result.final_output)

asyncio.run(main())
```

---

## Tracing

The SDK traces every run automatically to the OpenAI platform. Traces appear at https://platform.openai.com/traces.

### Default Tracing (no config needed)

```python
# Tracing is ON by default with OPENAI_API_KEY
result = await Runner.run(agent, input)
```

### Disable Tracing

```python
# Per-run
from agents.run import RunConfig
result = await Runner.run(agent, input, run_config=RunConfig(tracing_disabled=True))

# Globally (e.g. for tests)
import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
```

### Name Runs for the Dashboard

```python
run_config = RunConfig(
    workflow_name="Customer Support",     # logical name in traces
    group_id=session_id,                  # links traces across multiple turns
    trace_metadata={"user_id": user_id, "env": "production"},
    trace_include_sensitive_data=False,   # hide LLM inputs/outputs in traces
)
result = await Runner.run(agent, input, run_config=run_config)
```

### Custom Trace Processor

```python
from agents.tracing import add_trace_processor, TracingProcessor

class MyProcessor(TracingProcessor):
    def on_trace_start(self, trace):
        print(f"[Trace started] {trace.workflow_name}")

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        print(f"[Span] {span.span_data.type}: {span.duration_ms}ms")

    def on_trace_end(self, trace):
        # Send to your observability platform
        my_observability.record(trace)

    def shutdown(self): pass
    def force_flush(self): pass

add_trace_processor(MyProcessor())
```

---

## Production Environment Config

```bash
# Required
OPENAI_API_KEY=sk-proj-...

# Optional — use different base URL (Azure, OpenRouter, proxy)
OPENAI_BASE_URL=https://your-proxy.com/v1

# Disable tracing in CI/tests
OPENAI_AGENTS_DISABLE_TRACING=1
```

```python
import os
from agents import Agent, Runner, set_default_openai_key

# Programmatic key setup (alternative to env var)
set_default_openai_key(os.environ["OPENAI_API_KEY"])
```

### Custom Model Provider (OpenRouter, Azure, etc.)

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Custom provider (e.g. OpenRouter)
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

model = OpenAIChatCompletionsModel(
    model="anthropic/claude-3-5-sonnet",
    openai_client=client,
)

agent = Agent(
    name="Assistant",
    instructions="Be helpful.",
    model=model,
)

# Disable built-in tracing when using non-OpenAI provider
result = await Runner.run(
    agent,
    "Hello",
    run_config=RunConfig(tracing_disabled=True),
)
```

---

## ModelSettings Reference

```python
from agents.model_settings import ModelSettings

settings = ModelSettings(
    temperature=0.7,          # 0.0 (deterministic) to 2.0 (creative)
    max_tokens=2048,          # max output tokens
    top_p=0.9,
    tool_choice="auto",       # "auto" | "required" | "none"
    parallel_tool_calls=True, # allow multiple tools per turn
)

# Per-agent
agent = Agent(name="...", model_settings=settings)

# Global override via RunConfig
run_config = RunConfig(model_settings=settings)
```
