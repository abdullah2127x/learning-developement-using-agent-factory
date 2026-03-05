# OpenAI Agents SDK — Agent Clone (`agent.clone()`)

Source: [Official Docs](https://openai.github.io/openai-agents-python/agents/)
Verified: 2026-03-05

---

## What Is agent.clone()?

`agent.clone()` creates a **copy** of an existing agent with some properties overridden. The original agent stays untouched.

```python
base_agent = Agent(name="Base", instructions="Be helpful.", tools=[my_tool])

# Clone overrides only what you pass — everything else is copied
variant = base_agent.clone(name="Variant", instructions="Be concise.")
# variant has: name="Variant", instructions="Be concise.", tools=[my_tool] (inherited)
```

---

## When to Use agent.clone()

Use clone when you already have a **fully configured agent** and need a variation that changes **one or a few properties** while keeping everything else (tools, model_settings, handoffs, output_type, etc.) identical.

### Decision: clone() vs new Agent() vs dynamic instructions

| Situation | Use |
|-----------|-----|
| Same agent, different instructions per **request** (runtime) | **Dynamic instructions** (function) |
| Same agent config, different static instructions per **variant** (build time) | **agent.clone()** |
| Completely different agent (different tools, model, everything) | **new Agent()** |

### When clone() is the right choice

- You have a base agent with many tools/settings and need a variant with different `name` or `instructions`
- You're building multi-agent systems where specialists share the same toolset but differ in instructions
- You need to quickly spin up test variants of a production agent
- You want a "template agent" pattern — define once, clone many

### When clone() is NOT the right choice

- Instructions need to change per-request based on user context → use dynamic instructions function
- The variant needs completely different tools/model → just create a new Agent()
- You only have one agent with no variants → no need to clone

---

## What Can Be Cloned/Overridden?

Every Agent property can be overridden during clone. If you don't pass it, the original value is copied.

| Property | Inherited if not passed | Can override |
|----------|------------------------|-------------|
| `name` | ✅ | ✅ |
| `instructions` | ✅ | ✅ |
| `model` | ✅ | ✅ |
| `model_settings` | ✅ | ✅ |
| `tools` | ✅ | ✅ |
| `handoffs` | ✅ | ✅ |
| `output_type` | ✅ | ✅ |
| `mcp_servers` | ✅ | ✅ |

---

## Basic Usage

### Override instructions only

```python
base = Agent(
    name="Support",
    instructions="You are a general support agent.",
    tools=[search_docs, create_ticket],
)

# Same tools, different personality
friendly = base.clone(instructions="You are a friendly, warm support agent. Use casual language.")
formal = base.clone(instructions="You are a formal, professional support agent. Use business language.")
```

### Override name + instructions

```python
pirate = base.clone(name="Pirate", instructions="Write like a pirate.")
robot = base.clone(name="Robot", instructions="Write like a robot.")
```

### Override model for testing

```python
# Production agent
prod_agent = Agent(
    name="Analyst",
    instructions="Analyze data accurately.",
    tools=[query_db, generate_chart],
)

# Cheaper variant for testing
test_agent = prod_agent.clone(model="gpt-4o-mini")
```

---

## Use Cases

### Use Case 1: Multi-Agent Specialists from One Base

Build multiple specialist agents that share the same tools but have different instructions.

```python
base = Agent(
    name="Base",
    instructions="You are helpful.",
    tools=[search_web, summarize_text, translate],
)

researcher = base.clone(
    name="Researcher",
    instructions="You are a research specialist. Use search_web to find information, then summarize findings clearly.",
)

translator = base.clone(
    name="Translator",
    instructions="You are a translation specialist. Translate text accurately and naturally.",
)

summarizer = base.clone(
    name="Summarizer",
    instructions="You are a summarization specialist. Provide concise, accurate summaries.",
)
```

**Why clone here?** All three agents need the same tools. Without clone you'd repeat `tools=[search_web, summarize_text, translate]` three times.

---

### Use Case 2: Template Agent Pattern

Define a fully-configured "template" agent once, then spawn variants.

```python
# Template: fully configured, never used directly
template = Agent(
    name="Template",
    instructions="OVERRIDE THIS",
    tools=[get_user, update_user, search_products, place_order],
    model_settings=ModelSettings(temperature=0.3, max_tokens=1024),
)

# Spawn specialized agents from template
order_agent = template.clone(
    name="Order Agent",
    instructions="Help customers place and track orders. Be concise and action-oriented.",
)

account_agent = template.clone(
    name="Account Agent",
    instructions="Help customers with account settings, password resets, and profile updates.",
)

product_agent = template.clone(
    name="Product Agent",
    instructions="Help customers find products. Ask about preferences and suggest relevant items.",
)
```

**Why clone here?** All agents share 4 tools + identical model_settings. Template avoids repetition.

---

### Use Case 3: A/B Testing Agent Variants

Test different instructions or models against each other.

```python
baseline = Agent(
    name="Baseline",
    instructions="Answer user questions helpfully.",
    tools=[search_kb],
    model_settings=ModelSettings(temperature=0.5),
)

# Test: does a more specific instruction improve quality?
variant_a = baseline.clone(
    instructions="Answer user questions helpfully. Always cite your sources. Keep answers under 3 sentences.",
)

# Test: does lower temperature help?
variant_b = baseline.clone(
    model_settings=ModelSettings(temperature=0.1),
)

# Run both, compare results
result_a = await Runner.run(variant_a, user_query)
result_b = await Runner.run(variant_b, user_query)
```

---

### Use Case 4: Orchestrator with Specialist Clones

An orchestrator routes to specialist agents that are clones of a shared base.

```python
base_specialist = Agent(
    name="Specialist",
    instructions="OVERRIDE",
    tools=[search_docs, query_db, send_email],
)

tech_support = base_specialist.clone(
    name="Tech Support",
    instructions="You handle technical issues. Diagnose problems step by step.",
)

billing_support = base_specialist.clone(
    name="Billing Support",
    instructions="You handle billing questions. Check account status and explain charges.",
)

orchestrator = Agent(
    name="Router",
    instructions="Route the user to the right specialist based on their question.",
    handoffs=[tech_support, billing_support],
)
```

---

### Use Case 5: Language Variants

Same agent logic, different languages — at build time (not runtime).

```python
english_agent = Agent(
    name="English Support",
    instructions="You are a helpful assistant. Respond in English only.",
    tools=[search_faq, create_ticket],
)

spanish_agent = english_agent.clone(
    name="Spanish Support",
    instructions="Eres un asistente útil. Responde solo en español.",
)

arabic_agent = english_agent.clone(
    name="Arabic Support",
    instructions="أنت مساعد مفيد. أجب باللغة العربية فقط.",
)
```

**Why clone and not dynamic instructions?** Because these are fixed language variants deployed as separate agents, not per-request switching.

---

## clone() vs Dynamic Instructions — Side by Side

```python
# ── DYNAMIC INSTRUCTIONS (per-request, runtime) ──────────────
# ONE agent, instructions change every run based on context

def instructions(context, agent) -> str:
    # context = RunContextWrapper, context.context = your data
    if context and context.context.language == "es":
        return "Responde en español."
    return "Respond in English."

agent = Agent(name="Support", instructions=instructions, tools=[my_tool])

# Same agent, different behavior per run
await Runner.run(agent, "Hello", context=english_user)  # English instructions
await Runner.run(agent, "Hola", context=spanish_user)   # Spanish instructions


# ── AGENT CLONE (build-time variants) ────────────────────────
# MULTIPLE agents, instructions fixed at creation

base = Agent(name="Support", instructions="Respond in English.", tools=[my_tool])
spanish = base.clone(name="Spanish Support", instructions="Responde en español.")

# Different agents, each with fixed behavior
await Runner.run(base, "Hello")     # Always English
await Runner.run(spanish, "Hola")   # Always Spanish
```

**Rule of thumb:**
- Instructions depend on **who is calling** (user context at runtime) → dynamic instructions
- Instructions are **fixed per variant** (decided at build/deploy time) → clone

---

## Best Practices

- Always clone from a **base/template** agent, not from another clone
- Name your clones clearly — they appear in traces
- Don't clone just to change one field you could pass at runtime
- Use clone for build-time variations, dynamic instructions for runtime variations
- Keep the base agent well-documented since all clones inherit from it

---

## Summary

| Aspect | Detail |
|--------|--------|
| **What** | `agent.clone()` creates a copy with overridden properties |
| **When** | Need variations of same agent (different name/instructions/model) |
| **Why** | Avoid repeating tools, model_settings, handoffs across similar agents |
| **How** | `variant = base.clone(name="X", instructions="Y")` |
| **NOT for** | Per-request personalization (use dynamic instructions instead) |
