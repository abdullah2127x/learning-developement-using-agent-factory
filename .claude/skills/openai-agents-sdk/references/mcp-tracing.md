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

### Understanding stdio vs HTTP — When to Use Which

Both are ways your agent **communicates** with an MCP server. The transport does NOT determine
whether the data is local or remote — it determines how your code talks to the MCP server process.

| Question | Use `MCPServerStdio` | Use `MCPServerStreamableHttp` |
|----------|---------------------|-------------------------------|
| Is the MCP server an npm/CLI package? | Yes — `npx`, `python`, `node` | No |
| Do you have a URL like `http://...`? | No — you have a command to run | Yes |
| Who starts the server process? | The SDK spawns it automatically | You or someone else starts it separately |
| Server lifetime | Dies when your agent stops | Runs independently 24/7 |
| Example | `npx @upstash/context7-mcp` | `https://mcp.company.com/mcp` |

**Key insight:** `MCPServerStdio` spawns a local subprocess and talks through stdin/stdout pipes.
That subprocess can internally call remote APIs (like Context7 calling its cloud service), but
YOUR code communicates with the subprocess locally via pipes — not HTTP.

`MCPServerStreamableHttp` sends HTTP requests directly to a URL where an MCP server is already running.

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
            # -y auto-confirms npm install prompts. Without it, npx may HANG
            # waiting for user confirmation on first install.
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

### MCPServerStdio — All Parameters

```python
MCPServerStdio(
    name="My Server",                        # readable name for logs/traces
    params={
        "command": "npx",                    # command to spawn
        "args": ["-y", "@package/name"],     # args (-y is critical for npx!)
        "env": {},                           # extra env vars for the subprocess
    },
    cache_tools_list=True,                   # cache tools to avoid round-trip each turn
    client_session_timeout_seconds=30,       # timeout for MCP protocol messages (default: 5)
                                             # IMPORTANT: increase for npx cold starts,
                                             # especially on Windows where 5s is too short
    max_retry_attempts=3,                    # retry failed tool calls (default: 0)
    retry_backoff_seconds_base=1.0,          # exponential backoff: 1s, 2s, 4s (default: 1.0)
    tool_filter=["tool_a", "tool_b"],        # only expose these tools (default: all)
    require_approval="always",               # human-in-the-loop before tool runs
                                             # also accepts: "never", or dict per tool
    use_structured_content=False,            # use structured_content field (default: False)
    message_handler=my_handler,              # callback for raw MCP protocol messages
    failure_error_function=my_error_fn,      # custom error when tool fails
                                             # set to None to raise exceptions instead
)
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

`MCPServerManager` provides **graceful degradation**: if one server fails to connect,
the others still work. `manager.active_servers` contains only the servers that connected
successfully — failed servers are silently excluded.

This is much safer than `async with server1, server2:` which crashes entirely if ANY server fails.

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
        # If Calendar API fails to connect, manager.active_servers still has Docs + Filesystem
        # If ALL fail, active_servers is empty — agent runs with no MCP tools
        print(f"Connected {len(manager.active_servers)}/{len(servers)} MCP servers")

        agent = Agent(
            name="Assistant",
            instructions="Use available tools to help the user.",
            mcp_servers=manager.active_servers,
        )
        result = await Runner.run(agent, "What can you help me with?")
        print(result.final_output)

asyncio.run(main())
```

### MCPServerManager vs Manual `async with` — Comparison

```python
# ❌ FRAGILE — one server failure crashes everything
async with server_a, server_b, server_c:
    agent = Agent(mcp_servers=[server_a, server_b, server_c])

# ✅ RESILIENT — failed servers excluded, rest still work
async with MCPServerManager([server_a, server_b, server_c]) as manager:
    agent = Agent(mcp_servers=manager.active_servers)
```

---

## MCP Connection Error Handling

MCP servers can fail to connect (npx not installed, server down, timeout). Always handle these.

### Pattern 1: try/except Around `async with` (Single Server)

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from mcp.shared.exceptions import McpError

async def main():
    server = MCPServerStdio(
        name="Context7",
        params={"command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"]},
        client_session_timeout_seconds=30,
    )

    try:
        async with server:
            agent = Agent(name="Assistant", instructions="...", mcp_servers=[server])
            result = await Runner.run(agent, "Hello")
            print(result.final_output)
    except McpError as e:
        print(f"MCP server failed to connect: {e}")
        # Fallback: run agent without MCP tools
        agent = Agent(name="Assistant", instructions="...", tools=[])
        result = await Runner.run(agent, "Hello")
        print(result.final_output)
```

### Pattern 2: MCPServerManager (Multiple Servers — Recommended)

```python
from agents.mcp import MCPServerManager

servers = [context7_server, playwright_server, some_flaky_server]

async with MCPServerManager(servers) as manager:
    if not manager.active_servers:
        print("WARNING: No MCP servers connected. Running without tools.")
    else:
        print(f"Connected: {len(manager.active_servers)}/{len(servers)} servers")

    agent = Agent(mcp_servers=manager.active_servers)
    # Agent works with whatever servers connected — even if some failed
```

### MCP Tool Call Failures at Runtime

Even after successful connection, individual tool calls can fail mid-conversation
(server crashes, network drops, tool returns error). Use `failure_error_function`
on the MCP server to control what the LLM sees:

```python
def mcp_error_handler(tool_name: str, error: str) -> str:
    """Custom error when an MCP tool fails at runtime."""
    return f"The '{tool_name}' tool is temporarily unavailable. Try a different approach."

server = MCPServerStdio(
    name="Context7",
    params={"command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"]},
    failure_error_function=mcp_error_handler,  # LLM sees friendly message
    # Set to None to raise exceptions instead (crashes the run)
)
```

---

## Windows-Specific Setup

Windows requires extra configuration for the asyncio event loop and npx behavior.

### Required: Event Loop Policy

```python
import asyncio

# MUST be set BEFORE any async code runs on Windows
# Without this, you get "RuntimeError: Event loop is closed" or similar errors
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Required: Increase MCP Timeout

The default `client_session_timeout_seconds=5` is too short for npx cold starts on Windows.
npx needs to download, install, and start the MCP server subprocess — this can take 10-30s
on the first run.

```python
# ❌ Default 5s — will timeout on Windows cold starts
MCPServerStdio(params={"command": "npx", "args": ["-y", "@package"]})

# ✅ Set 30s — gives npx time to install and start
MCPServerStdio(
    params={"command": "npx", "args": ["-y", "@package"]},
    client_session_timeout_seconds=30,
)
```

### Required: `-y` Flag for npx

Always include `-y` in npx args. Without it, npx may prompt "Need to install @package, OK?" and
**hang forever** waiting for stdin confirmation (which never comes because the SDK controls stdin).

```python
# ❌ May hang waiting for install confirmation
"args": ["@upstash/context7-mcp@latest"]

# ✅ Auto-confirms, never hangs
"args": ["-y", "@upstash/context7-mcp@latest"]
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
