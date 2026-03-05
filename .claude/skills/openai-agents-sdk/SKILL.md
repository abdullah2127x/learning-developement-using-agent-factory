---
name: openai-agents-sdk
description: |
  Builder and Guide for creating AI agents using the OpenAI Agents SDK (Python).
  Covers the full progression from hello world agents to production-grade multi-agent systems
  with tools, handoffs, guardrails, MCP integration, streaming, error handling, and observability.
  This skill should be used when building any agent with the OpenAI Agents SDK — whether creating
  a first agent, adding function tools, wiring multi-agent handoffs, implementing guardrails,
  integrating MCP servers, or hardening agents for production.
  Supports three multi-agent control patterns:
    1. Handoffs (peer-to-peer delegation where control transfers permanently to a specialist)
    2. Agent-as-Tool via agent.as_tool() (main agent keeps control, calls sub-agents like tools,
       sub-agents receive only generated input not conversation history, main agent combines results)
    3. Runner-inside-tool (manual Runner.run() inside @function_tool for maximum control over
       sub-agent execution, error handling, retries, and metadata)
  Detects existing project structure and patterns before generating code.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# OpenAI Agents SDK

**Builder + Guide** for AI agents using OpenAI Agents (Python). Based on official OpenAI documentation.

## What This Skill Does

- Builds agents from hello world → multi-agent orchestration → production-grade systems
- Generates `@function_tool` functions with automatic schema and validation
- Creates multi-agent topologies with three distinct control patterns:
  - **Handoffs** (`handoffs=[agent_a, agent_b]`): Route to ONE specialist — control transfers permanently, new agent sees full conversation history. Use when you want to delegate entirely.
  - **Agent-as-Tool** (`agent.as_tool()`): Call sub-agents like regular tools — main agent keeps control, sub-agent receives only generated input (not history), main agent processes and combines results. Use when orchestrating MULTIPLE specialists or when you need to stay in the driver's seat.
  - **Runner-inside-Tool** (`Runner.run()` inside `@function_tool`): Maximum control pattern — manually run a sub-agent inside a function tool with custom error handling, retries, metadata, and conditional logic. Use when `as_tool()` parameters aren't enough.
- Implements input/output guardrails with tripwire validation
- Integrates MCP servers (stdio, HTTP, SSE, custom)
- Configures streaming (token-level, structured output, nested agents)
- Sets up observability, tracing, error handling, sessions
- Detects existing agents/tools/patterns before generating

## What This Skill Does NOT Do

- Build the frontend/UI (separate concern)
- Manage OpenAI API billing or rate limits
- Deploy to cloud platforms (generates runnable code only)
- Create realtime voice agents (separate Agent type, use realtimeagent-sdk instead)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing agent definitions, tools, project structure, conventions |
| **Conversation** | User's specific use case, build level, agent topology, features needed |
| **Skill References** | Domain patterns from `references/` (official API, best practices, examples) |
| **User Guidelines** | Project constraints, team standards, preferred approaches |

Only ask user for THEIR specific requirements. All SDK knowledge is in this skill's references.

---

## Quick Start: 3 Steps

### Step 1: Choose Your Provider & Model

**ONE question**: Which LLM provider do you prefer?

| Provider | Model | Cost | Speed | Best For |
|----------|-------|------|-------|----------|
| **OpenAI API** (default) | `gpt-4o-mini` | $$ | Very Fast | Production, best quality |
| **Gemini** | `gemini-2.5-flash` | $ | Fast | Prototyping, cost-sensitive |
| **OpenRouter** | Free models | Free + $$ | Varies | Model flexibility, fallbacks |
| **LiteLLM** | 20+ providers | Varies | Varies | Multi-provider, enterprise |

**Templates available**: Copy from `assets/` and customize agent for your use case.

### Step 2: Install & Setup

```bash
# Install SDK
pip install openai-agents

# (Optional) MCP support
pip install openai-agents[mcp]
```

### Step 2b: Environment Management (MANDATORY — pydantic-settings)

**CRITICAL**: ALL env variables MUST be loaded via `pydantic-settings` BaseSettings — NEVER use raw `os.getenv()` or `load_dotenv()` + `os.getenv()`. This ensures type safety, startup validation, and a single source of truth.

**Rules:**
1. Check if `.env` and `.env.example` exist in the project root. If not, create them.
2. Add the provider's API key placeholder to BOTH files.
3. If a `Settings` class already exists (e.g., `app/core/config.py`), add the API key field there.
4. If no Settings class exists, create one in the agent file or a config module.
5. NEVER use `os.getenv()` — always access keys via `settings.field_name`.
6. NEVER commit real API keys — `.env` should be in `.gitignore`.

**The pattern — ALWAYS use this for env vars:**

```python
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    # Provider keys — add only the one you need
    openai_api_key: str = ""       # For OpenAI provider
    gemini_api_key: str = ""       # For Gemini provider
    openrouter_api_key: str = ""   # For OpenRouter provider

settings = Settings()

# Then use: settings.gemini_api_key (NOT os.getenv("GEMINI_API_KEY"))
```

**Why `extra="ignore"`**: Allows `.env` files with other vars (DATABASE_URL, DEBUG, etc.) without validation errors.

**If a Settings class already exists** (e.g., in a FastAPI project), just add the key field to it:
```python
# app/core/config.py — ADD to existing Settings class
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./todo.db"
    debug: bool = False
    gemini_api_key: str = ""       # <-- ADD THIS
```

**Per-provider `.env` placeholders to add:**

| Provider | Add to `.env` and `.env.example` |
|----------|----------------------------------|
| **OpenAI** | `OPENAI_API_KEY=` with comment `# Get key from: https://platform.openai.com/api-keys` |
| **Gemini** | `GEMINI_API_KEY=` with comment `# Get key from: https://aistudio.google.com/apikey` |
| **OpenRouter** | `OPENROUTER_API_KEY=` with comment `# Get key from: https://openrouter.ai/keys` |
| **LiteLLM** | Provider-specific key (e.g., `GEMINI_API_KEY=`) |

**Why pydantic-settings over os.getenv():**
- **Type safety** — IDE autocomplete, typo detection at write-time
- **Startup validation** — missing required keys crash immediately with a clear error, not deep in runtime
- **Single source of truth** — one `settings` object, one import, no scattered `os.getenv()` calls
- **Consistency** — same pattern as FastAPI projects (fastapi-builder skill uses this)

### Step 3: Create Agent

Copy template from `assets/` matching your provider choice, then customize:

```python
from agents import Agent, Runner, function_tool

@function_tool
async def your_tool(param: str) -> str:
    """Tool description (shown to LLM)."""
    return f"Result: {param}"

agent = Agent(
    name="Your Agent Name",
    instructions="What should the agent do?",
    tools=[your_tool],
    model="gpt-4o-mini",  # Or your chosen model
)

# Run
result = await Runner.run(agent, "User input here")
print(result.final_output)
```

---

## Build Levels

Choose your complexity level:

```
Level 1 — Hello World (simplest)
  └── Single Agent + basic execution
  └── Plain text output
  └── Time to working agent: 5 minutes

Level 2 — Agent with Tools ← DEFAULT
  └── @function_tool decorated functions
  └── Structured output (Pydantic models)
  └── Type-safe validation
  └── Time to working agent: 15 minutes

Level 3 — Multi-Agent Orchestration
  └── Handoff patterns: Agent(handoffs=[a, b]) — control transfers permanently to specialist
  └── Orchestrator patterns: Agent(tools=[a.as_tool(), b.as_tool()]) — main agent keeps control,
      calls sub-agents as tools, combines results. Sub-agents receive only generated input.
  └── Runner-inside-tool: Runner.run() inside @function_tool — maximum control over sub-agent
      execution with custom error handling, retries, metadata, and conditional logic.
  └── Template: assets/agent_l3_handoff.py (handoffs), assets/agent_l3_orchestrator.py (as_tool)
  └── Time to working agent: 30 minutes

Level 4 — Production-Grade
  └── Input/output guardrails + tripwires
  └── Tool-level guardrails & error handling
  └── MCP server integration
  └── Sessions & persistent memory
  └── Streaming (token, structured output, nested)
  └── Tracing & observability
  └── Time to working agent: 1-2 hours
```

**Decision**: No tools? → L1. Tools needed? → L2. Route between agents? → L3. Safety/observability needed? → L4.

---

## Workflow

### Step 1: Understand the Scope

| Question | Answer → Path |
|----------|---|
| "Which provider?" | Copy `assets/agent_[provider].py` template |
| "Which config level?" | Global, Run, or Agent level (see `references/model-configuration.md`) |
| "How to control model behavior?" | Use ModelSettings (temperature, max_tokens, tool_choice, etc.) (see `references/model-settings.md`) |
| "What tools needed?" | Use `@function_tool` for each tool (see `references/tools.md`) |
| "Need to pass app state to tools?" | Use RunContextWrapper for dependency injection (see `references/core-agents.md`) |
| "Personalize per-request?" | Use dynamic instructions function — `instructions=my_func` (see `references/core-agents.md` → Dynamic Instructions section) |
| "Need agent variants with shared config?" | Use `agent.clone()` to create build-time copies with overridden properties (see `references/agent-clone.md`) |
| "Multiple agents?" | Three patterns — see decision tree below and `references/multi-agent.md` |
| "Keep control in main agent?" | Use `agent.as_tool()` — main agent calls sub-agents as tools, receives output, combines results (see `references/multi-agent.md` → Pattern 2 and `as_tool()` API) |
| "Delegate entirely to specialist?" | Use `handoffs=` — control transfers permanently, specialist sees full history (see `references/multi-agent.md` → Pattern 1) |
| "Need max control over sub-agent?" | Use `Runner.run()` inside `@function_tool` — custom error handling, retries, metadata (see `references/multi-agent.md` → Runner Inside Tool) |
| "Safety critical?" | Add guardrails (see `references/guardrails.md`) |
| "Need streaming?" | Add streaming config (see `references/streaming.md`) |
| "External APIs?" | Add MCP servers (see `references/mcp.md`) |
| "Need conversation memory?" | Add session — `SQLiteSession` for local dev, `SQLAlchemySession` for production PostgreSQL, or manual `to_input_list()` for full control. Pass `session=` to `Runner.run()`. See `references/sessions.md` for all 3 approaches, integration with guardrails/handoffs/streaming, anti-patterns, and troubleshooting. |
| "Need observability?" | Enable tracing (see `references/tracing.md` or `references/mcp-tracing.md`) |

### Step 2: Read Relevant References

- **Core concepts?** → `references/core-agents.md` (agent, tools, context injection, **dynamic instructions**)
- **No tools?** → `references/agents.md`
- **Adding tools?** → `references/tools.md`
- **Context/dependency injection?** → `references/core-agents.md` (RunContextWrapper, passing app state)
- **Dynamic instructions?** → `references/core-agents.md` → Dynamic Instructions section (pass a function, not a string, to `instructions=`)
- **Agent clone/variants?** → `references/agent-clone.md` (build-time copies with overridden name/instructions/model; template pattern; multi-agent specialists from one base; A/B testing)
- **Handoffs (control transfers)?** → `references/handoffs.md` (complete `handoff()` API, input filters, nested history, callbacks, `on_handoff`, `remove_all_tools`, recommended prompt prefix, multi-hop chains, streaming events)
- **Multi-agent?** → `references/multi-agent.md`
- **Safety/validation?** → `references/guardrails.md`
- **Persistent state / conversation memory?** → `references/sessions.md` (manual `to_input_list()`, `SQLiteSession` for local dev, `SQLAlchemySession` for production PostgreSQL)
- **Structured outputs?** → `references/structured-output.md`
- **Real-time responses?** → `references/streaming.md`
- **External integrations?** → `references/mcp.md`
- **Error handling?** → `references/error-handling.md`
- **Observability?** → `references/tracing.md` or `references/mcp-tracing.md`
- **Advanced patterns?** → `references/advanced-patterns.md`
- **Provider setup?** → `references/custom-llm-providers.md`, `references/litellm-provider.md`

### Step 3: Copy Template & Customize

**Minimal template:**
```python
from agents import Agent, Runner

agent = Agent(
    name="MyAgent",
    instructions="You are helpful.",
    model="gpt-4o-mini",
)

result = await Runner.run(agent, "Hi")
print(result.final_output)
```

**Add tools:**
```python
from agents import function_tool

@function_tool
async def get_weather(city: str) -> str:
    """Get weather for a city."""
    return "sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Help users check weather.",
    tools=[get_weather],
    model="gpt-4o-mini",
)
```

**Add guardrails:**
```python
from agents import guardrails

@guardrails.input_guardrail
def check_input(context, input_text):
    if len(input_text) > 1000:
        raise guardrails.GuardrailTriggered("Input too long")
    return input_text

agent = Agent(..., input_guardrails=[check_input])
```

See templates in `assets/` for complete examples.

### Step 4: Run & Test

```python
# Synchronous
result = Runner.run_sync(agent, "input")

# Async (recommended)
result = await Runner.run(agent, "input")

# Streaming
async for event in Runner.run_streamed(agent, "input"):
    if event.type == "text":
        print(event.text, end="", flush=True)
```

---

## Core Concepts (Quick Reference)

**Agent**: LLM equipped with instructions and tools. It follows a loop: receive input → decide actions → call tools → process results → respond.

**Tools**: Functions agents can call. Five types:
- Function tools (your Python functions via `@function_tool`)
- Agents as tools (nested agents via `agent.as_tool()`)
- Hosted tools (OpenAI's WebSearch, CodeInterpreter, etc.)
- MCP servers (external via stdio/HTTP/SSE)
- Custom tools (implement Tool interface)

**Multi-Agent Patterns** (three control levels):
- **Handoffs** (`handoffs=[a, b]`): Control transfers permanently to specialist. New agent sees full conversation history. Main agent stops. Use for routing to ONE specialist.
- **Agent-as-Tool** (`agent.as_tool()`): Sub-agent is wrapped as a `FunctionTool`. Main agent calls it like any tool, stays in control, and processes the result. Sub-agent sees only generated input (not history). Use for orchestrating MULTIPLE specialists and combining results.
- **Runner-inside-Tool** (`Runner.run()` in `@function_tool`): Manually invoke a sub-agent inside a function tool. Full control over error handling, max_turns, RunConfig, metadata. Use when `as_tool()` parameters aren't sufficient.

**Guardrails**: Validation gates before/after agent execution. Tripwire when violated.

**Streaming**: Real-time token output (token, text, structured results) for responsive UI.

**MCP**: Model Context Protocol servers provide standardized tool interfaces (filesystem, git, custom APIs).

**Sessions**: Persistent conversation memory across `Runner.run()` calls. By default each run is stateless — sessions fix this. Three main approaches:
  - **`to_input_list()`** (manual, in-memory): You manage a Python list of messages yourself. Full control, but lost on restart.
  - **`SQLiteSession`** (automatic, local file): SDK auto-loads/saves history to a SQLite file. Good for local dev, CLI agents, prototyping.
  - **`SQLAlchemySession`** (automatic, production DB): Same auto behavior but backed by PostgreSQL/Neon/MySQL. Production-ready.
  The Runner flow: `get_items()` → merge with new input → run agent → `add_items()`. Just pass `session=` to `Runner.run()`.
  See `references/sessions.md` for full details, patterns, and anti-patterns.

**Tracing**: Built-in observability visualizing agent loops and tool calls.

---

## Common Patterns

### Hello World (L1)
```python
from agents import Agent, Runner

agent = Agent(name="Echo", instructions="Repeat what user says.", model="gpt-4o-mini")
result = await Runner.run(agent, "Hello!")
print(result.final_output)
```

### With Tools (L2)
```python
@function_tool
async def add(a: int, b: int) -> int:
    return a + b

agent = Agent(
    name="Calculator",
    instructions="Use add tool for math.",
    tools=[add],
    model="gpt-4o-mini",
)
result = await Runner.run(agent, "What is 2 + 3?")
```

### Multi-Agent Handoff (L3) — Control Transfers Permanently
```python
math_agent = Agent(name="Math", instructions="Answer math questions.", model="gpt-4o-mini")
history_agent = Agent(name="History", instructions="Answer history questions.", model="gpt-4o-mini")
triage = Agent(
    name="Triage",
    instructions="Route to specialist.",
    handoffs=[math_agent, history_agent],
    model="gpt-4o-mini",
)
result = await Runner.run(triage, "What is 2+2?")  # Routes to math_agent, triage loses control
```

### Orchestrator with Agent-as-Tool (L3) — Main Agent Keeps Control
```python
# Sub-agents used as tools — orchestrator stays in charge
spanish_agent = Agent(name="Spanish", instructions="Translate to Spanish. Return only translation.")
french_agent = Agent(name="French", instructions="Translate to French. Return only translation.")

orchestrator = Agent(
    name="Orchestrator",
    instructions="Translate text using tools. Combine and present results.",
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_spanish",
            tool_description="Translate text to Spanish.",
        ),
        french_agent.as_tool(
            tool_name="translate_french",
            tool_description="Translate text to French.",
        ),
    ],
    model="gpt-4o-mini",
)
result = await Runner.run(orchestrator, "Translate 'hello' to Spanish and French")
# Orchestrator calls both tools, receives results, combines them, stays in control
```

### Runner Inside @function_tool (L3) — Maximum Control
```python
@function_tool
async def research(topic: str) -> str:
    """Research a topic and return a brief report."""
    agent = Agent(name="Researcher", instructions="Research thoroughly.", model="gpt-4o")
    result = await Runner.run(agent, f"Research: {topic}", max_turns=5)
    return str(result.final_output)

# Use like any other tool — orchestrator gets full control over when/how to call it
orchestrator = Agent(name="Main", instructions="Help users.", tools=[research])
```

### With Guardrails (L4)
```python
@guardrails.input_guardrail
def check_length(context, input_text):
    if len(input_text) > 500:
        raise guardrails.GuardrailTriggered("Input exceeds 500 chars")
    return input_text

@guardrails.output_guardrail
def check_safety(context, output):
    if "unsafe" in output.lower():
        return "I can't respond to that."
    return output

agent = Agent(
    name="Safe",
    instructions="Be helpful and safe.",
    input_guardrails=[check_length],
    output_guardrails=[check_safety],
    model="gpt-4o-mini",
)
```

---

## Provider Support

All providers use same Agent API. Only setup differs:

| Provider | Env Var | Template | Model | Notes |
|----------|---------|----------|-------|-------|
| OpenAI | `OPENAI_API_KEY` | `assets/agent_openai.py` | `gpt-4o-mini` | Default, best quality |
| Gemini | `GEMINI_API_KEY` | `assets/agent_gemini.py` | `gemini-2.5-flash` | Cheapest |
| OpenRouter | `OPENROUTER_API_KEY` | `assets/agent_openrouter.py` | Free models | Most flexible |
| LiteLLM | Various | `assets/agent_litellm.py` | Any (20+ providers) | Multi-provider support |

See `references/providers.md` for complete setup guide.

---

## Anti-Patterns

| Anti-Pattern | Why Problematic | Fix |
|---|---|---|
| No docstrings on tools | LLM doesn't know what tool does | Always add clear docstring |
| `Runner.run_sync()` in async code | Blocks event loop | Use `await Runner.run()` instead |
| Ignoring guardrail tripwires | Silent failures | Catch `GuardrailTriggered` exception |
| Tools without error handling | Crashes stop agent | Use `failure_error_function` |
| Hardcoding API keys | Security risk | Use `pydantic-settings` BaseSettings with `.env` file |
| Using `os.getenv()` / `load_dotenv()` | No type safety, no startup validation, scattered access | Use `pydantic-settings` BaseSettings (see Step 2b) — access via `settings.field_name` |
| No `.env` / `.env.example` created | User gets `None` key errors, doesn't know which env var to set | ALWAYS create `.env` with placeholder + `.env.example` (see Step 2b) |
| No context typing | Type errors at runtime | Use `Agent[YourContextType]` |
| Large tool outputs | Context overflow | Return structured data, not raw text |
| Tools with side effects in prompts | LLM calls tools unnecessarily | Use `tool_choice="required"` to require explicit use |

---

## Observability

Enable tracing to visualize agent behavior:

```python
from agents import Tracer

tracer = Tracer()

async def main():
    result = await Runner.run(agent, "input", tracer=tracer)
    print(tracer.get_trace())  # Visualize in OpenAI Dashboard
```

Tracing shows: agent loops, tool calls, LLM reasoning, timing.

---

## Reference Files

| File | What's Inside |
|------|--------------|
| `references/core-agents.md` | **START HERE** — Agent basics, tools, @function_tool, RunContextWrapper, context injection, structured output, runner methods, **dynamic instructions** (pass a function to `instructions=` for runtime personalization), complete L2 example |
| `references/agent-clone.md` | **agent.clone()** — Create build-time copies of agents with overridden properties (name, instructions, model, etc.). Covers: when to use clone vs dynamic instructions vs new Agent(); template agent pattern; multi-agent specialists from one base; A/B testing variants; orchestrator with cloned specialists; language variants. Decision table for choosing the right approach. |
| `references/lifecycle-hooks.md` | **Lifecycle Hooks (dedicated reference)** — Two hook systems: `RunHooks` (global, fires for ALL agents, passed to `Runner.run(hooks=...)`) and `AgentHooks` (per-agent, fires for ONE agent, set via `Agent(hooks=...)`). Both fire concurrently via `asyncio.gather()`. **7 hook methods each:** `on_agent_start`/`on_start`, `on_agent_end`/`on_end`, `on_llm_start`, `on_llm_end`, `on_tool_start`, `on_tool_end`, `on_handoff`. Covers: complete execution order timeline, context types (`AgentHookContext` vs `RunContextWrapper`), the agent run loop diagram showing when each hook fires, practical examples (timing, token tracking, tool auditing, handoff tracking). **IMPORTANT:** Hooks are observers — they cannot modify LLM input, tool results, or agent behavior. Do NOT pass `AgentHooks` to `Runner.run()` (TypeError) or `RunHooks` to `Agent(hooks=...)`. All hook methods must be `async`. |
| `references/run-lifecycle.md` | **Run Lifecycle (dedicated reference)** — Complete flow from `Runner.run()` call to `RunResult`. Covers: **Three runner methods** (`run()` async, `run_sync()` blocking, `run_streamed()` streaming) with all parameters. **The main while loop** with visual diagram: initialization → turn counter → input guardrails (first turn only) → single turn execution → NextStep routing. **What counts as a "turn"** — one LLM invocation (tool calls don't add turns, parallel tools = same turn, handoff decision = 1 turn). **`max_turns`** — default 10, what happens when exceeded, `MaxTurnsExceeded` exception, how to choose the right value (table by agent type), graceful handling via `error_handlers["max_turns"]` or try/except. **Four NextStep types:** `NextStepFinalOutput` (done), `NextStepRunAgain` (tool called, loop again), `NextStepHandoff` (switch agent), `NextStepInterruption` (tool needs approval). **`RunResult` fields:** `final_output`, `last_agent`, `new_items`, `raw_responses`, `context_wrapper.usage`, `interruptions`, `to_input_list()`, `to_state()`. **`RunConfig`** — global settings (model override, model_settings, handoff filters, guardrails, tracing) with priority table vs agent-level settings. **Input guardrails** — sequential vs parallel, run only on turn 1, parallel guardrails cancel LLM if tripwire fires. **Output guardrails** — run only on final output, not on tool turns or after handoffs. **`RunState`** — resuming interrupted runs after tool approval. **Complete 26-step timeline** showing exact order of every hook, guardrail, and LLM call for a tool-using agent. |
| `references/tools.md` | Tool creation, validation, error handling, @function_tool decorator, **agents-as-tools** (`as_tool()` as a tool type alongside function tools, when to use each, Runner-inside-tool pattern) |
| `references/handoffs.md` | **Handoffs (dedicated reference)** — Complete `handoff()` function API with all parameters. Covers: basic `handoffs=[]`, custom `handoff()` with `on_handoff` callbacks (with/without input), `input_filter` for history control, `HandoffInputData` fields, built-in `remove_all_tools` filter, `nest_handoff_history` for collapsing history, `prompt_with_handoff_instructions()` recommended prompt, multi-hop chains (A→B→C), RunConfig global settings, conditional `is_enabled`, streaming events, `Handoff` dataclass internals. |
| `references/multi-agent.md` | **Three multi-agent patterns**: (1) Triage with handoffs (control transfers), (2) Orchestrator with `agent.as_tool()` (main agent keeps control, sub-agents called as tools), (3) Runner inside `@function_tool` (maximum control). Includes **complete `as_tool()` API reference** with all parameters (is_enabled, custom_output_extractor, on_stream, parameters, needs_approval, run_config, max_turns, etc.) and code examples for each feature. |
| `references/guardrails.md` | **Guardrails & Safety (dedicated reference)** — Three guardrail types: input (first agent only), output (final agent only), tool (every `@function_tool` call). **Execution modes**: parallel (default, `run_in_parallel=True`) vs blocking (`run_in_parallel=False` — agent never runs if tripwire fires). **Official code examples**: input guardrail with math homework checker agent, output guardrail with `output_type` matching, tool guardrails with `allow()`/`reject_content()`/`raise_exception()` behaviors. **Correct function signatures**: input uses `str \| list[TResponseInputItem]`, output receives agent's `output_type` not raw str, tool guardrails can be sync or async. **Workflow boundaries**: tool guardrails only apply to `@function_tool` (NOT handoffs, hosted tools, `as_tool()`). **RunConfig** global guardrails, **tripwire mechanism**, **data types reference**, **exception handling pattern**, **best practices**, and **anti-patterns**. |
| `references/streaming.md` | Token streaming, structured output streaming, event handling |
| `references/structured-output.md` | Pydantic models, TypedDict, output_type configuration |
| `references/mcp-tracing.md` | MCP servers (stdio, HTTP, SSE) + detailed tracing setup |
| `references/sessions.md` | **Session Memory (dedicated reference)** — By default `Runner.run()` is stateless; sessions add persistent conversation memory. **Three main approaches covered:** (1) Manual `to_input_list()` — you manage an in-memory Python list, full control but lost on restart, includes truncation pattern; (2) `SQLiteSession` — SDK auto-saves/loads to a SQLite file, good for local dev and CLI agents, includes resuming across restarts, conversation loop example; (3) `SQLAlchemySession` — production-ready with PostgreSQL/Neon/MySQL via `from_url()` or shared engine, works with custom providers (OpenRouter, Gemini). **Session Interface** — `Session` protocol and `SessionABC` with 4 async methods (`get_items`, `add_items`, `pop_item`, `clear_session`). **Runner flow**: load history → merge new input → run agent → save new items. **Database architecture** — two-table schema (`agent_sessions` + `agent_messages`), JSON-serialized messages. **Integration** — sessions + guardrails (new turn only), handoffs (shared history), streaming, RunConfig, lifecycle hooks. **Common patterns** — user-per-session, new conversation each run, multi-agent chains. **Anti-patterns** — unbounded history, shared session IDs, new ID each run. **SDK runtime methods**, **truncation**, **troubleshooting**, and **best practices**. **IMPORTANT:** Sessions are incompatible with `conversation_id`/`previous_response_id`/`auto_previous_response_id`. |
| `references/error-handling.md` | Exception handling, failure functions, recovery strategies |
| `references/model-configuration.md` | 3-level model config: Global, Run, Agent — priority, when to use each, combining levels |
| `references/model-settings.md` | ModelSettings fields: temperature, max_tokens, tool_choice, penalties, truncation; Agent vs Run level; provider support |
| `references/custom-llm-providers.md` | Custom LLM provider setup and configuration |
| `references/litellm-provider.md` | LiteLLM multi-provider integration and routing |

## Templates

Copy-paste starters matching your provider:

| File | Provider | Model | Base Level |
|------|----------|-------|-----------|
| `assets/agent_openai.py` | OpenAI | gpt-4o-mini | L2 (tools) |
| `assets/agent_gemini.py` | Gemini | gemini-2.5-flash | L2 (tools) |
| `assets/agent_openrouter.py` | OpenRouter | free-model | L2 (tools) |
| `assets/agent_litellm.py` | LiteLLM | gemini-2.5-flash | L2 (tools) |
| `assets/agent_l1_hello_world.py` | OpenAI | gpt-4o-mini | L1 (no tools) |
| `assets/agent_l3_handoff.py` | OpenAI | gpt-4o-mini | L3 (handoffs — control transfers) |
| `assets/agent_l3_orchestrator.py` | OpenAI | gpt-4o-mini | L3 (agent-as-tool — main agent keeps control) |
| `assets/agent_l4_production.py` | OpenAI | gpt-4o-mini | L4 (full features) |
| `assets/.env.example` | - | - | Configuration |

---

## Next Steps

1. **Read Step 1 workflow** (choose provider)
2. **Copy relevant template** from `assets/`
3. **Add API key** to `.env`
4. **Customize agent** (name, instructions, tools)
5. **Read reference** for the feature you need (tools, guardrails, etc.)
6. **Test locally** before deploying

---

## Sources

- [OpenAI Agents SDK Official Docs](https://openai.github.io/openai-agents-python/)
- [GitHub Repository](https://github.com/openai/openai-agents-python)
- [Official Examples](https://openai.github.io/openai-agents-python/examples/)
- [MCP Server Integration](https://openai.github.io/openai-agents-python/ref/mcp/server/)
- [Tools API Reference](https://openai.github.io/openai-agents-python/tools/)
