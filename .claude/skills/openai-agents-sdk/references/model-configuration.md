# OpenAI Agents SDK — Model Configuration (3 Levels)

Source: openai/openai-agents-python official docs + panaversity/learn-agentic-ai verified examples
Verified: 2026-03-04 against live Gemini via OpenAIChatCompletionsModel

---

## Overview

The SDK resolves which model to use at three configuration levels. Each level has a clear priority — higher levels override lower ones.

**Priority (highest wins):**
```
Agent Level  >  Run Level  >  Global Level
 (Highest)      (Medium)       (Lowest)
```

| Level | Set Where | Scope | Overridden By |
|-------|-----------|-------|---------------|
| **Global** | Module-level functions | All agents, all runs | Run Level, Agent Level |
| **Run** | `RunConfig` passed to `Runner.run()` | One specific run | Agent Level |
| **Agent** | `model=` on `Agent()` | One specific agent | Nothing — highest priority |

---

## Level 1: Global Level (Lowest Priority)

Set **once** at module level. Applies to ALL agents and ALL runs in the process. Used as the fallback when neither Agent nor RunConfig specifies a model/client.

### Key Functions

| Function | Purpose |
|----------|---------|
| `set_default_openai_client(client)` | Set the default AsyncOpenAI client for all agents |
| `set_default_openai_api("chat_completions")` | Switch to Chat Completions API (required for Gemini/OpenRouter) |
| `set_tracing_disabled(True)` | Disable tracing globally (required for non-OpenAI providers) |
| `set_default_openai_key(key)` | Set default OpenAI API key (alternative to env var) |

### Environment Variable Alternative

For OpenAI models only, you can set the default model via environment variable:
```bash
export OPENAI_DEFAULT_MODEL=gpt-4o-mini
```

### Example: Global Level with Gemini

```python
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)
from app.core.config import settings

# ── Global configuration (set ONCE at module level) ──────────────────
set_tracing_disabled(True)                   # required for non-OpenAI
set_default_openai_api("chat_completions")   # required for Gemini/OpenRouter

client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(client)            # all agents use this client

# ── Agent uses just a string model name ──────────────────────────────
# No OpenAIChatCompletionsModel wrapper needed.
# No RunConfig needed.
# The global client resolves the model name.
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model="gemini-2.5-flash",    # string — resolved by global client
)

# ── Run — no run_config needed ───────────────────────────────────────
result = await Runner.run(agent, "Hello!")
print(result.final_output)
```

### When to Use Global Level

- Single-provider app — all agents use the same LLM provider
- Simple scripts and prototypes
- You want the cleanest possible `Runner.run()` calls (no run_config param)
- Setting tracing/API mode defaults for non-OpenAI providers

---

## Level 2: Run Level (Medium Priority)

Set per `Runner.run()` call via `RunConfig`. Overrides Global defaults for **that specific run only**.

### RunConfig Key Fields

```python
@dataclass
class RunConfig:
    model: str | Model | None = None        # override model for this run
    model_provider: ModelProvider = ...      # client to resolve model names
    model_settings: ModelSettings | None = None  # temperature, etc.
    tracing_disabled: bool = False           # disable tracing for this run
```

### Example: Run Level with Gemini

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents.run import RunConfig
from app.core.config import settings

# ── Create client and model wrapper ──────────────────────────────────
client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client,
)

run_config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

# ── Agent has NO model — gets it from RunConfig ─────────────────────
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
)

# ── RunConfig determines the model used ──────────────────────────────
result = Runner.run_sync(agent, "Hello!", run_config=run_config)
print(result.final_output)
```

### Example: Switching Models Per Request

```python
# Two different models
fast_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client)
smart_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

fast_config = RunConfig(model=fast_model, model_provider=client, tracing_disabled=True)
smart_config = RunConfig(model=smart_model, model_provider=client, tracing_disabled=True)

# Same agent, different models per run
result1 = await Runner.run(agent, "Simple question", run_config=fast_config)
result2 = await Runner.run(agent, "Complex analysis", run_config=smart_config)
```

### When to Use Run Level

- Switch models per-request without recreating agents
- Mix cheap/expensive models based on query complexity
- A/B testing different models with the same agent
- Override global defaults for specific runs

---

## Level 3: Agent Level (Highest Priority)

Set directly on `Agent()`. Overrides **both** Run Level and Global Level. Each agent is locked to its own model.

### Example: Agent Level with Gemini

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from app.core.config import settings

# ── Create client and model ──────────────────────────────────────────
client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# ── Model set ON the agent — highest priority ───────────────────────
agent = Agent(
    name="Assistant",
    instructions="You only respond in Urdu.",
    model=agent_model,   # Agent Level — overrides RunConfig and Global
)

# Even if run_config has a different model, this agent uses gemini-2.5-flash
result = await Runner.run(agent, "Hello!")
print(result.final_output)
```

### Example: Multi-Agent with Different Models

```python
# Cheap model for routing
triage_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client)

# Smart model for analysis
analysis_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

triage_agent = Agent(
    name="Triage",
    instructions="Route to the right specialist.",
    model=triage_model,        # cheap and fast
    handoffs=[analysis_agent],
)

analysis_agent = Agent(
    name="Analyzer",
    instructions="Provide deep analysis.",
    model=analysis_model,      # smarter and more capable
)
```

### When to Use Agent Level

- Multi-agent systems where each agent needs its own model
- Lock an agent to a specific model regardless of run config
- Pair cheap models with simple agents, expensive models with complex agents
- The agent's model should NEVER change at runtime

---

## Which Level Should You Choose?

```
START
  │
  ├─ Single agent, single provider?
  │    └─ YES → Global Level (simplest, cleanest code)
  │
  ├─ Need to switch models per-request?
  │    └─ YES → Run Level (RunConfig)
  │
  ├─ Multiple agents needing different models?
  │    └─ YES → Agent Level (each agent gets its own model)
  │
  └─ Mix of the above?
       └─ Use Global as fallback + Agent Level for specific agents
          that need their own model
```

| Scenario | Recommended Level |
|----------|------------------|
| Simple script, one agent, one provider | **Global** |
| CLI chatbot, single agent | **Global** |
| API server switching models per request | **Run Level** |
| A/B testing models | **Run Level** |
| Multi-agent with cheap triage + smart analyzer | **Agent Level** |
| Production multi-agent orchestration | **Agent Level** + Global as fallback |
| Prototype/learning | **Global** (least boilerplate) |

---

## Combining Levels

You can use multiple levels together. Higher levels override lower ones:

```python
from openai import AsyncOpenAI
from agents import (
    Agent, Runner, OpenAIChatCompletionsModel,
    set_default_openai_client, set_default_openai_api, set_tracing_disabled,
)
from agents.run import RunConfig
from app.core.config import settings

# ── Level 1: Global (fallback for any agent without a model) ────────
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

global_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(global_client)

# ── Level 2: Run Level (override for specific runs) ─────────────────
run_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=global_client)
run_config = RunConfig(model=run_model, model_provider=global_client, tracing_disabled=True)

# ── Level 3: Agent Level (highest priority — this agent's model is locked) ──
agent_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=global_client)

# Agent WITH model= set (Agent Level)
locked_agent = Agent(name="Locked", instructions="...", model=agent_model)

# Agent WITHOUT model= (falls back to RunConfig → Global)
flexible_agent = Agent(name="Flexible", instructions="...")

# locked_agent ALWAYS uses gemini-2.5-flash (Agent Level wins)
await Runner.run(locked_agent, "Hello", run_config=run_config)

# flexible_agent uses gemini-2.0-flash from RunConfig (Run Level wins over Global)
await Runner.run(flexible_agent, "Hello", run_config=run_config)

# flexible_agent uses Global client with model string (Global Level)
await Runner.run(flexible_agent, "Hello")
```

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Setting `model=` on both Agent and RunConfig | Agent Level wins — RunConfig model is ignored for that agent | Only set model on one level, or be intentional about overrides |
| Using `OPENAI_DEFAULT_MODEL` env var with Gemini/OpenRouter | Env var only works with OpenAI's default provider | Use `set_default_openai_client()` for custom providers |
| Forgetting `set_default_openai_api("chat_completions")` | Global Level with Gemini/OpenRouter defaults to Responses API which they don't support | Always call this for non-OpenAI providers at Global Level |
| Forgetting `set_tracing_disabled(True)` | Tracing tries to reach OpenAI and fails for Gemini/OpenRouter | Set at Global Level or in RunConfig |
| Wrapping model in `OpenAIChatCompletionsModel` at Global Level | Global Level only needs `set_default_openai_client()` + string model name | Only wrap in `OpenAIChatCompletionsModel` for Run Level and Agent Level |

---

## Summary

| Level | How to Set | Priority | Model Format | Needs RunConfig? |
|-------|-----------|----------|-------------|-----------------|
| **Global** | `set_default_openai_client()` + `set_default_openai_api()` | Lowest | String: `"gemini-2.5-flash"` | No |
| **Run** | `RunConfig(model=..., model_provider=...)` | Medium | `OpenAIChatCompletionsModel` object | Yes |
| **Agent** | `Agent(model=...)` | Highest | `OpenAIChatCompletionsModel` object | No |
