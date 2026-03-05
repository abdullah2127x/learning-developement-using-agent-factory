# OpenAI Agents SDK — ModelSettings

Source: openai/openai-agents-python official docs + verified examples
Verified: 2026-03-04 against live Gemini and OpenAI APIs

---

## Overview

**ModelSettings controls HOW the model generates responses** — it's separate from model selection (WHICH model to use).

Think of it this way:
- **Model** = "Use GPT-4o-mini" (which model to use)
- **ModelSettings** = "Temperature 0.2, max 500 tokens" (how it behaves)

ModelSettings can be set at two levels:
1. **Agent Level**: `Agent(model_settings=...)` — default behavior for that agent
2. **Run Level**: `RunConfig(model_settings=...)` — override for specific runs (has priority)

---

## Core Concept

ModelSettings is a dataclass that holds generation parameters:

```python
from agents import ModelSettings

settings = ModelSettings(
    temperature=0.7,
    max_tokens=1024,
    tool_choice="auto",
    # ... more fields
)
```

**Key rule**: All fields are optional. `None` = use provider default.

---

## Generation Parameters

### `temperature`: float (0.0 - 2.0)

Controls randomness in responses.

| Value | Behavior | Use When |
|-------|----------|----------|
| **0.0** | Fully deterministic, same input → same output every time | Factual Q&A, data extraction, consistent results required |
| **0.5-0.7** | Balanced — consistent but with variety | Most use cases (default for general purpose) |
| **1.0+** | More creative, varied responses | Creative writing, brainstorming, diverse outputs |
| **2.0** | Maximum randomness | Highly creative, experimental contexts |

```python
ModelSettings(temperature=0.2)  # Deterministic — good for classification
ModelSettings(temperature=0.8)  # Balanced creativity
```

**Note**: Do NOT use `temperature` and `top_p` together — choose one.

---

### `top_p`: float (0.0 - 1.0)

**Nucleus sampling** — only consider tokens whose cumulative probability is within top_p.

| Value | Behavior | Compare to temp |
|-------|----------|-----------------|
| **0.1** | Very focused, top 10% of tokens | Deterministic focus |
| **0.5** | Moderately focused | Balanced |
| **1.0** | All tokens considered | Maximum variety |

```python
ModelSettings(top_p=0.9)  # Consider top 90% of likely tokens
```

**Why use top_p instead of temperature?**
- `temperature` penalizes low-probability tokens equally
- `top_p` removes tail (low-probability) tokens completely
- Use `top_p` for cleaner, more confident responses

---

### `max_tokens`: int

Maximum output tokens the model can generate in a single response.

| Value | Typical Use |
|-------|------------|
| **256** | Short factual answers, classifications |
| **512** | Medium-length responses, summaries |
| **1024** | Full responses, detailed explanations (default range) |
| **2048+** | Long-form content, creative writing |

```python
ModelSettings(max_tokens=512)  # Limit response length
```

**Why set it?**
- Control costs (especially for expensive models)
- Force concise responses
- Prevent runaway generations
- Enforce API limits

---

## Repetition Control

### `frequency_penalty`: float (-2.0 to 2.0)

Penalize tokens based on how often they've appeared in the response so far.

| Value | Behavior | Use When |
|-------|----------|----------|
| **-2.0** | Encourage repetition | You want repeated phrases (e.g., counting, lists) |
| **0.0** | No penalty (default) | Most cases |
| **0.5-1.0** | Reduce repetition moderately | Varied vocabulary preferred |
| **2.0** | Strong penalty on repetition | Avoid redundancy at all costs |

```python
ModelSettings(frequency_penalty=0.5)  # Avoid repeating words
```

---

### `presence_penalty`: float (-2.0 to 2.0)

Penalize tokens that have appeared AT ALL in the response (regardless of frequency).

| Value | Behavior | Use When |
|-------|----------|----------|
| **-2.0** | Encourage staying on topic | Generate content about specific subject |
| **0.0** | No penalty (default) | Most cases |
| **0.5-1.0** | Encourage variety | Generate diverse topics/ideas |
| **2.0** | Maximize diversity | Brainstorming, list generation, novelty |

```python
ModelSettings(presence_penalty=1.0)  # Encourage diverse topics
```

**Difference from frequency_penalty:**
- `frequency_penalty`: Penalizes word that appeared 5 times more than word that appeared 1 time
- `presence_penalty`: Penalizes both equally (only cares IF it appeared, not HOW MUCH)

---

## Tool Behavior

### `tool_choice`: str

Tells the model when/if it should call tools.

| Value | Behavior |
|-------|----------|
| **"auto"** (default) | Model decides when to use tools (can skip them) |
| **"required"** | Model MUST call a tool every turn (always uses a tool) |
| **"none"** | Model cannot call any tools (forced text-only response) |

```python
# Default — model decides
ModelSettings(tool_choice="auto")

# Force tool use
ModelSettings(tool_choice="required")

# Disable tools
ModelSettings(tool_choice="none")
```

**When to use each:**
- `"auto"`: General purpose agents with optional tools
- `"required"`: Function-calling agents where you need guaranteed tool execution
- `"none"`: When you want pure text responses (disable tools temporarily)

---

### `parallel_tool_calls`: bool

Whether the model can call multiple tools in ONE turn.

| Value | Behavior |
|-------|----------|
| **True** (default) | Model calls multiple tools simultaneously if needed |
| **False** | Model calls one tool at a time (sequential) |
| **None** | Use provider default (usually True) |

```python
# Allow multiple tool calls in one response
ModelSettings(parallel_tool_calls=True)

# One tool at a time
ModelSettings(parallel_tool_calls=False)
```

**When to disable (set False):**
- Tools have side effects that should be sequential
- Your API can't handle concurrent tool calls
- You need to verify each tool result before next tool runs

---

## Truncation

### `truncation`: str

What happens if input exceeds context window.

| Value | Behavior |
|-------|----------|
| **"auto"** (default) | Automatically truncate long inputs without error |
| **"disabled"** | Raise error if input exceeds context window |

```python
ModelSettings(truncation="auto")      # Safe — truncates gracefully
ModelSettings(truncation="disabled")  # Strict — fails if too long
```

**Use cases:**
- `"auto"`: Production systems where truncation is acceptable
- `"disabled"`: Safety-critical applications where you need to know if input was truncated

---

## OpenAI-Specific Fields

These fields may NOT work with Gemini or OpenRouter. Check provider docs before using.

### `reasoning`: Reasoning object

For reasoning models (o3-mini, o1, future reasoning models).

```python
from agents import Reasoning

ModelSettings(
    reasoning=Reasoning(effort="high")  # "low", "medium", "high"
)
```

---

### `verbosity`: str

Control output level for reasoning models.

```python
ModelSettings(verbosity="low")      # "low" | "medium" | "high"
```

---

### `store`: bool

Store response for later retrieval (batch processing, caching).

```python
ModelSettings(store=True)  # Store for later access
```

---

### `prompt_cache_retention`: str

How long to keep cached prompts.

```python
ModelSettings(prompt_cache_retention="24h")  # "in_memory" | "24h"
```

---

### `include_usage`: bool

Include token usage in response.

```python
ModelSettings(include_usage=True)
```

---

## Usage Patterns

### Pattern 1: Agent Level (Default Behavior)

Set once per agent:

```python
from agents import Agent, ModelSettings

default_settings = ModelSettings(
    temperature=0.7,
    max_tokens=1024,
    tool_choice="auto",
)

agent = Agent(
    name="Assistant",
    instructions="You are helpful.",
    model="gpt-4o-mini",
    model_settings=default_settings,  # Default for all runs
)
```

All runs using this agent will use these settings unless overridden.

---

### Pattern 2: Run Level Override

Override for specific runs:

```python
from agents import Agent, Runner, ModelSettings
from agents.run import RunConfig

agent = Agent(
    name="Assistant",
    instructions="You are helpful.",
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.7, max_tokens=1024),
)

# Override for this run only
run_settings = ModelSettings(
    temperature=0.2,  # Deterministic for this run
    max_tokens=512,   # Shorter for this run
)

run_config = RunConfig(model_settings=run_settings)

result = await Runner.run(agent, "input", run_config=run_config)
```

Result: Run uses `temperature=0.2` and `max_tokens=512`, ignoring agent's defaults.

---

### Pattern 3: Both Levels Together

Use Agent level as default + Run level for overrides:

```python
# Agent default: creative responses
agent_settings = ModelSettings(
    temperature=0.8,      # Creative
    top_p=0.95,
    max_tokens=1024,
)

agent = Agent(
    name="Brainstormer",
    instructions="Generate creative ideas.",
    model="gpt-4o-mini",
    model_settings=agent_settings,
)

# Override 1: Deterministic
deterministic_config = RunConfig(
    model_settings=ModelSettings(temperature=0.1)  # Only override temperature
)

# Override 2: Constrained
constrained_config = RunConfig(
    model_settings=ModelSettings(max_tokens=256)  # Only override max_tokens
)

# Same agent, different behaviors
idea1 = await Runner.run(agent, "ideas for app", run_config=deterministic_config)
idea2 = await Runner.run(agent, "ideas for game", run_config=constrained_config)
```

**Priority**: Non-None fields in RunConfig override Agent level.

---

## Common Configurations

### Fast & Cheap (Classify/Extract)

```python
ModelSettings(
    temperature=0.0,      # Deterministic
    max_tokens=256,       # Short response
    tool_choice="none",   # No tools
)
```

### Balanced (General Purpose)

```python
ModelSettings(
    temperature=0.7,      # Balanced
    max_tokens=1024,      # Medium length
    tool_choice="auto",   # Use tools if helpful
)
```

### Creative (Brainstorm/Generate)

```python
ModelSettings(
    temperature=1.0,                # Creative
    top_p=0.95,                     # Diverse tokens
    frequency_penalty=0.5,          # Reduce repetition
    presence_penalty=1.0,           # Diverse topics
    max_tokens=2048,                # Long-form
)
```

### Tool-Heavy (Function Calling)

```python
ModelSettings(
    temperature=0.3,              # Focused on tool selection
    tool_choice="required",       # Always use tools
    parallel_tool_calls=True,     # Multiple tools at once
    max_tokens=512,               # Shorter responses
)
```

### Safe & Strict

```python
ModelSettings(
    temperature=0.0,          # Deterministic
    truncation="disabled",    # Fail if too long
    tool_choice="none",       # Disable tools
)
```

---

## Field Reference Table

| Field | Type | Range | Default | Priority |
|-------|------|-------|---------|----------|
| `temperature` | float | 0.0-2.0 | Provider default | Run > Agent |
| `top_p` | float | 0.0-1.0 | Provider default | Run > Agent |
| `max_tokens` | int | 1+ | Provider default | Run > Agent |
| `frequency_penalty` | float | -2.0 to 2.0 | 0.0 | Run > Agent |
| `presence_penalty` | float | -2.0 to 2.0 | 0.0 | Run > Agent |
| `tool_choice` | str | "auto", "required", "none" | "auto" | Run > Agent |
| `parallel_tool_calls` | bool | True, False, None | Provider default | Run > Agent |
| `truncation` | str | "auto", "disabled" | "auto" | Run > Agent |
| `reasoning` | Reasoning | - | None (OpenAI only) | Run > Agent |
| `verbosity` | str | "low", "medium", "high" | Provider default | Run > Agent |
| `store` | bool | True, False | False (OpenAI only) | Run > Agent |
| `prompt_cache_retention` | str | "in_memory", "24h" | None (OpenAI only) | Run > Agent |
| `include_usage` | bool | True, False | False (OpenAI only) | Run > Agent |

---

## Provider Support

| Field | OpenAI | Gemini | OpenRouter | Notes |
|-------|--------|--------|-----------|-------|
| `temperature` | ✅ | ✅ | ✅ | Universal |
| `top_p` | ✅ | ✅ | ✅ | Universal |
| `max_tokens` | ✅ | ✅ | ✅ | Universal |
| `frequency_penalty` | ✅ | ❌ | ⚠️ | Some routed models support |
| `presence_penalty` | ✅ | ❌ | ⚠️ | Some routed models support |
| `tool_choice` | ✅ | ✅ | ✅ | Universal for tool-supporting models |
| `parallel_tool_calls` | ✅ | ✅ | ✅ | Universal |
| `truncation` | ✅ | ✅ | ✅ | Universal |
| `reasoning` | ✅ (o3) | ❌ | ❌ | OpenAI reasoning models only |
| `verbosity` | ✅ (o3) | ❌ | ❌ | OpenAI reasoning models only |
| `store` | ✅ | ❌ | ❌ | OpenAI only |
| `prompt_cache_retention` | ✅ | ❌ | ❌ | OpenAI only |
| `include_usage` | ✅ | ⚠️ | ⚠️ | Check provider |

**Note**: If your provider doesn't support a field, it's silently ignored (no error).

---

## Anti-Patterns

| Anti-Pattern | Why Problematic | Fix |
|---|---|---|
| Using both `temperature` AND `top_p` | Conflicting sampling strategies | Choose ONE sampling method |
| Setting `max_tokens=0` | Invalid input | Use positive integer or None |
| `tool_choice="required"` without tools | Agent can't call tools that don't exist | Only use with agent.tools defined |
| Setting `frequency_penalty=-2.0` in classification | Encourages repetition when you need variety | Use 0.0-1.0 for normal cases |
| Not setting `max_tokens` in production | Responses can be unexpectedly long/expensive | Always set for cost control |
| Ignoring provider support | Settings silently ignored on unsupported providers | Check provider docs before using |

---

## Summary

- **ModelSettings** = How the model behaves (separate from model selection)
- **Set at Agent Level**: Default for all runs with that agent
- **Override at Run Level**: Use RunConfig to override for specific runs
- **All fields optional**: None = use provider default
- **Provider-specific fields**: Check docs for Gemini, OpenRouter, etc.
- **Priority**: Run Level overrides Agent Level
- **No errors**: Unsupported fields are silently ignored

