# OpenAI Agents SDK — Handoffs (Complete Reference)

Source: openai/openai-agents-python SDK source code + official docs

---

## What Is a Handoff?

A handoff is when one agent **permanently transfers control** to another agent. The receiving agent takes over the conversation entirely — the original agent stops executing.

**Key behavior:**
- The new agent sees the **full conversation history** (all previous messages, tool calls, and outputs)
- The original agent **does not continue** after the handoff
- The LLM sees the handoff as a tool call named `transfer_to_<agent_name>`
- The transfer is seamless — users should not see or notice the handoff

**When to use handoffs:**
- Route to ONE specialist based on user intent (e.g., billing vs technical support)
- Delegate entirely when the current agent cannot handle the request
- The specialist needs the full conversation context to respond

**When NOT to use handoffs (use `as_tool()` instead):**
- You need to call MULTIPLE specialists and combine their results
- The main agent must stay in control and process sub-agent outputs
- Sub-agents should NOT see the full conversation history

---

## Basic Usage: `handoffs=[]` on Agent

The simplest way to add handoffs — pass agent instances directly to `handoffs=`:

```python
from agents import Agent, Runner
import asyncio

# Specialist agents
billing_agent = Agent(
    name="Billing Agent",
    instructions=(
        "You handle all billing-related questions: invoices, payments, "
        "refunds, subscriptions. Be professional and empathetic."
    ),
    model="gpt-4o-mini",
)

technical_agent = Agent(
    name="Technical Agent",
    instructions=(
        "You handle all technical support: bugs, setup, errors, "
        "troubleshooting. Be clear and provide step-by-step solutions."
    ),
    model="gpt-4o-mini",
)

sales_agent = Agent(
    name="Sales Agent",
    instructions=(
        "You help with sales inquiries: pricing, features, packages, "
        "upgrades. Be enthusiastic and focus on value."
    ),
    model="gpt-4o-mini",
)

# Triage agent — routes to the right specialist
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a customer support router. Route incoming questions to the "
        "right specialist:\n"
        "- Billing Agent: invoices, payments, refunds, subscriptions\n"
        "- Technical Agent: bugs, errors, setup, troubleshooting\n"
        "- Sales Agent: pricing, features, upgrades\n"
        "- Handle general greetings yourself.\n\n"
        "Use handoffs to delegate to specialists."
    ),
    handoffs=[billing_agent, technical_agent, sales_agent],
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(triage_agent, "My invoice is wrong", max_turns=10)
    print(result.final_output)
    print(f"Handled by: {result.last_agent.name}")  # "Billing Agent"

asyncio.run(main())
```

When you pass agents directly to `handoffs=[]`, the SDK auto-generates:
- **Tool name**: `transfer_to_billing_agent` (slugified from agent name)
- **Tool description**: `"Handoff to the Billing Agent agent to handle the request."`
- **No input schema**: The LLM just calls it, no arguments needed

---

## `handoff()` Function — Full Control

For customizing names, descriptions, input filters, callbacks, and conditional enable/disable, use the `handoff()` function:

```python
from agents import Agent, handoff

handoff(
    # --- Required ---
    agent: Agent,                      # The agent to hand off to

    # --- Name & Description Overrides ---
    tool_name_override: str | None = None,
        # Custom tool name shown to LLM. Default: "transfer_to_<agent_name>" (slugified).
    tool_description_override: str | None = None,
        # Custom description. Default: "Handoff to the <name> agent to handle the request."

    # --- Handoff Callback (runs when handoff is invoked) ---
    on_handoff: Callable | None = None,
        # A function that runs BEFORE the new agent starts.
        # Two signatures:
        #   Without input: on_handoff(context: RunContextWrapper) -> None
        #   With input:    on_handoff(context: RunContextWrapper, input: THandoffInput) -> None
        # Use for: logging, state updates, side effects, validation.
    input_type: type | None = None,
        # Pydantic model or dataclass for structured handoff input.
        # Required when on_handoff takes two arguments.
        # The LLM fills in the fields when calling the handoff.

    # --- History Control ---
    input_filter: Callable[[HandoffInputData], HandoffInputData] | None = None,
        # Filter/modify the conversation history before passing to the new agent.
        # Receives HandoffInputData with: input_history, pre_handoff_items, new_items.
        # Return modified HandoffInputData.
        # Use for: removing sensitive messages, trimming history, stripping tool calls.
    nest_handoff_history: bool | None = None,
        # Override RunConfig-level nest_handoff_history for this specific handoff.
        # When True: collapses entire prior history into a single assistant summary message.
        # When None: falls back to RunConfig setting (default: False).

    # --- Conditional Enable/Disable ---
    is_enabled: bool | Callable[[RunContextWrapper, Agent], MaybeAwaitable[bool]] = True,
        # Bool: always on/off.
        # Callable: dynamically enable/disable based on context at runtime.
        # When disabled, the handoff tool is hidden from the LLM entirely.

) -> Handoff
```

---

## `handoff()` Features with Examples

### Custom Tool Name & Description

```python
from agents import Agent, handoff

specialist = Agent(
    name="Billing Specialist",
    instructions="Handle complex billing disputes and refund processing.",
)

triage = Agent(
    name="Triage",
    instructions="Route to escalate_billing for any billing disputes.",
    handoffs=[
        handoff(
            agent=specialist,
            tool_name_override="escalate_billing",
            tool_description_override="Escalate complex billing disputes to senior specialist.",
        )
    ],
)
```

### Handoff Callback (`on_handoff`) — Without Input

Run a function when the handoff happens (logging, state changes):

```python
from agents import Agent, handoff, RunContextWrapper

async def log_handoff(ctx: RunContextWrapper):
    """Log the handoff event for analytics."""
    print(f"Handoff triggered for user: {ctx.context.user_id}")
    # Could also: update database, send notification, etc.

specialist = Agent(name="Specialist", instructions="...")

triage = Agent(
    name="Triage",
    handoffs=[
        handoff(
            agent=specialist,
            on_handoff=log_handoff,  # Runs before specialist starts
        )
    ],
)
```

### Handoff Callback (`on_handoff`) — With Structured Input

The LLM can pass structured data when handing off:

```python
from pydantic import BaseModel, Field
from agents import Agent, handoff, RunContextWrapper

class EscalationInfo(BaseModel):
    reason: str = Field(description="Why this is being escalated")
    priority: str = Field(description="'low', 'medium', or 'high'")
    summary: str = Field(description="Brief summary of the issue")

async def handle_escalation(ctx: RunContextWrapper, info: EscalationInfo):
    """Process the escalation data before the specialist starts."""
    print(f"Escalation: {info.reason} (priority: {info.priority})")
    # Store escalation info in context for the specialist to access
    ctx.context.escalation = info

specialist = Agent(name="Senior Specialist", instructions="...")

triage = Agent(
    name="Triage",
    instructions=(
        "For complex issues, escalate to Senior Specialist. "
        "Provide reason, priority, and summary when escalating."
    ),
    handoffs=[
        handoff(
            agent=specialist,
            on_handoff=handle_escalation,
            input_type=EscalationInfo,  # LLM fills in these fields
        )
    ],
)
```

### Input Filter — Control What History the New Agent Sees

By default, the new agent sees the FULL conversation history. Use `input_filter` to modify this:

```python
from agents import Agent, handoff
from agents.handoffs import HandoffInputData

def strip_sensitive_history(data: HandoffInputData) -> HandoffInputData:
    """Remove all history — only pass the latest user message and handoff items."""
    # Keep only new_items (the handoff trigger + output)
    return data.clone(
        input_history=(),          # Clear all prior history
        pre_handoff_items=(),      # Clear items before the handoff turn
    )

specialist = Agent(name="Specialist", instructions="...")

triage = Agent(
    name="Triage",
    handoffs=[
        handoff(
            agent=specialist,
            input_filter=strip_sensitive_history,
        )
    ],
)
```

**`HandoffInputData` fields you can modify:**

| Field | Type | What It Contains |
|---|---|---|
| `input_history` | `str \| tuple[TResponseInputItem, ...]` | All messages before `Runner.run()` was called |
| `pre_handoff_items` | `tuple[RunItem, ...]` | Items generated before the handoff turn |
| `new_items` | `tuple[RunItem, ...]` | Items from the current turn (includes handoff trigger) |
| `input_items` | `tuple[RunItem, ...] \| None` | When set, used instead of `new_items` for the next agent's input |
| `run_context` | `RunContextWrapper \| None` | The run context at handoff time |

### Built-in Filter: `remove_all_tools`

The SDK provides a built-in filter that strips all tool calls from history:

```python
from agents import Agent, handoff
from agents.extensions.handoff_filters import remove_all_tools

specialist = Agent(name="Specialist", instructions="...")

triage = Agent(
    name="Triage",
    handoffs=[
        handoff(
            agent=specialist,
            input_filter=remove_all_tools,  # Strips function_call, file_search, web_search, etc.
        )
    ],
)
```

`remove_all_tools` removes these item types from history:
- `function_call` and `function_call_output`
- `computer_call` and `computer_call_output`
- `file_search_call` and `web_search_call`
- `HandoffCallItem`, `HandoffOutputItem`, `ToolCallItem`, `ToolCallOutputItem`, `ReasoningItem`

### Nested History (`nest_handoff_history`)

Collapses the entire prior conversation into a single assistant summary message, reducing token usage:

```python
from agents import Agent, handoff

specialist = Agent(name="Specialist", instructions="...")

triage = Agent(
    name="Triage",
    handoffs=[
        handoff(
            agent=specialist,
            nest_handoff_history=True,  # Collapse prior history into summary
        )
    ],
)
```

**What happens when `nest_handoff_history=True`:**
1. The SDK takes all prior messages (input_history + pre_handoff_items + new_items)
2. Formats them as a numbered transcript
3. Wraps them in `<CONVERSATION HISTORY>` markers
4. Passes a single assistant message containing the summary to the new agent
5. Tool calls and reasoning items are summarized but not forwarded verbatim

**Custom summary markers:**
```python
from agents.handoffs import set_conversation_history_wrappers

# Change the default <CONVERSATION HISTORY> markers
set_conversation_history_wrappers(
    start="--- PRIOR CONTEXT ---",
    end="--- END PRIOR CONTEXT ---",
)
```

**Custom history mapper:**
```python
from agents.handoffs import nest_handoff_history, HandoffInputData
from agents.items import TResponseInputItem

def custom_mapper(transcript: list[TResponseInputItem]) -> list[TResponseInputItem]:
    """Custom logic to build the summary message."""
    # Only keep the last 5 messages
    recent = transcript[-5:]
    return recent

def my_filter(data: HandoffInputData) -> HandoffInputData:
    return nest_handoff_history(data, history_mapper=custom_mapper)

specialist = Agent(name="Specialist", instructions="...")
triage = Agent(
    name="Triage",
    handoffs=[handoff(agent=specialist, input_filter=my_filter)],
)
```

### Conditional Enable/Disable (`is_enabled`)

Dynamically show/hide a handoff based on runtime context:

```python
from agents import Agent, handoff, RunContextWrapper

def premium_only(ctx: RunContextWrapper, agent: Agent) -> bool:
    """Only show this handoff for premium users."""
    return ctx.context.user_tier == "premium"

premium_specialist = Agent(name="Premium Support", instructions="...")

triage = Agent(
    name="Triage",
    handoffs=[
        handoff(
            agent=premium_specialist,
            is_enabled=premium_only,  # Hidden from free-tier users
        )
    ],
)
```

---

## RunConfig: Global Handoff Settings

Set handoff behavior for the entire run:

```python
from agents.run import RunConfig
from agents.handoffs import HandoffInputData

def trim_history(data: HandoffInputData) -> HandoffInputData:
    """Global filter: keep only last 10 items in history."""
    history = data.input_history
    if isinstance(history, tuple) and len(history) > 10:
        history = history[-10:]
    return data.clone(input_history=history)

run_config = RunConfig(
    # Global input filter — applies to ALL handoffs that don't have their own input_filter
    handoff_input_filter=trim_history,

    # Collapse prior history into summary (beta)
    # When True: all handoffs collapse history unless overridden per-handoff
    nest_handoff_history=True,

    # Custom history mapper (used when nest_handoff_history=True)
    handoff_history_mapper=None,  # Or a custom Callable[[list], list]
)

result = await Runner.run(triage, "input", run_config=run_config, max_turns=10)
```

**Priority order:**
1. Per-handoff `input_filter` (highest priority — overrides global)
2. Per-handoff `nest_handoff_history` (overrides RunConfig-level)
3. RunConfig `handoff_input_filter` (global fallback)
4. RunConfig `nest_handoff_history` (global fallback, default: False)

---

## Recommended Prompt Prefix

The SDK provides a recommended system prompt prefix for agents that use handoffs. It tells the LLM that it's part of a multi-agent system and that transfers are seamless:

```python
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

triage = Agent(
    name="Triage",
    instructions=prompt_with_handoff_instructions(
        "You are a customer support router. Route to the right specialist."
    ),
    handoffs=[billing_agent, technical_agent],
)
```

**What it prepends:**
```
# System context
You are part of a multi-agent system called the Agents SDK, designed to make agent
coordination and execution easy. Agents uses two primary abstraction: **Agents** and
**Handoffs**. An agent encompasses instructions and tools and can hand off a
conversation to another agent when appropriate.
Handoffs are achieved by calling a handoff function, generally named
`transfer_to_<agent_name>`. Transfers between agents are handled seamlessly in the
background; do not mention or draw attention to these transfers in your conversation
with the user.
```

---

## Multi-Hop Handoff Chains (A → B → C)

Handoffs can chain — agent A hands off to B, which hands off to C:

```python
from agents import Agent, Runner

# Level 3: Final specialist
refund_agent = Agent(
    name="Refund Specialist",
    instructions="Process refund requests. Ask for order number and reason.",
    model="gpt-4o-mini",
)

# Level 2: Sub-router
billing_agent = Agent(
    name="Billing Agent",
    instructions=(
        "Handle billing questions. For refund requests, "
        "hand off to Refund Specialist."
    ),
    handoffs=[refund_agent],  # Can chain further
    model="gpt-4o-mini",
)

# Level 1: Entry point
triage = Agent(
    name="Triage",
    instructions="Route billing questions to Billing Agent.",
    handoffs=[billing_agent],
    model="gpt-4o-mini",
)

# "I want a refund" → Triage → Billing Agent → Refund Specialist
result = await Runner.run(triage, "I want a refund for order #12345", max_turns=15)
print(f"Final agent: {result.last_agent.name}")  # "Refund Specialist"
```

**Critical: Always set `max_turns`** — handoff chains can loop if agents hand back and forth. Without `max_turns`, this runs indefinitely.

---

## Handoff vs Agent-as-Tool: Decision Guide

```
User message arrives
    │
    ├── Route to ONE specialist, delegate entirely?
    │       └── Use handoffs: Agent(handoffs=[a, b, c])
    │           - Control transfers permanently
    │           - New agent sees full history
    │           - Original agent stops
    │
    ├── Call MULTIPLE specialists, combine results?
    │       └── Use as_tool(): Agent(tools=[a.as_tool(), b.as_tool()])
    │           - Main agent keeps control
    │           - Sub-agents see only generated input
    │           - Main agent combines and presents results
    │
    └── Need maximum control over sub-agent?
            └── Use Runner.run() inside @function_tool
                - Custom error handling, retries, metadata
                - Full RunConfig control
```

| Behavior | Handoff | Agent-as-Tool |
|---|---|---|
| **Control** | Transfers permanently | Main agent keeps control |
| **History** | New agent sees full conversation | Sub-agent sees only generated input |
| **Multi-call** | Cannot call multiple agents per turn | Can call multiple tools per turn |
| **Result processing** | New agent produces final output directly | Main agent processes and combines results |
| **Use case** | Route to ONE specialist | Orchestrate MULTIPLE specialists |

---

## `Handoff` Dataclass — Internal Structure

The `Handoff` dataclass is what `handoff()` returns. You rarely create this directly, but it's useful to understand the internal model:

```python
@dataclass
class Handoff:
    tool_name: str                    # Tool name the LLM calls (e.g., "transfer_to_billing")
    tool_description: str             # Description the LLM sees
    input_json_schema: dict           # JSON schema for handoff input (empty if no input)
    on_invoke_handoff: Callable       # Async function that returns the target Agent
    agent_name: str                   # Name of the target agent
    input_filter: HandoffInputFilter | None  # Filter for conversation history
    nest_handoff_history: bool | None        # Override for history nesting
    strict_json_schema: bool = True          # Enforce strict JSON mode
    is_enabled: bool | Callable = True       # Conditional enable/disable
```

---

## Streaming Events from Handoffs

When using streaming, handoffs emit an `agent_updated_stream_event`:

```python
from agents import Runner

result = Runner.run_streamed(triage, "My invoice is wrong")
async for event in result.stream_events():
    if event.type == "agent_updated_stream_event":
        print(f"Handoff! New agent: {event.new_agent.name}")
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Triage agent not handing off | Make instructions explicit: "You MUST hand off to X for Y questions" |
| Handoff chains looping forever | Always set `max_turns` on `Runner.run()` |
| History growing too large | Use `input_filter` to trim, or `nest_handoff_history=True` to collapse |
| New agent confused by tool history | Use `remove_all_tools` filter from `agents.extensions.handoff_filters` |
| Handoff not showing up for LLM | Check `is_enabled` — disabled handoffs are hidden entirely |
| LLM mentioning the handoff | Use `prompt_with_handoff_instructions()` to tell LLM transfers are seamless |
| `on_handoff` taking wrong number of args | Without input_type: `on_handoff(ctx)` (1 arg). With input_type: `on_handoff(ctx, data)` (2 args) |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Using handoffs when you need combined results | Can't combine outputs from multiple specialists | Use `agent.as_tool()` instead |
| No `max_turns` in multi-agent | Handoff chains can loop indefinitely | Always set `max_turns=10` or similar |
| Huge history in handoff chains | Each agent sees everything, context bloats | Use `nest_handoff_history=True` or `input_filter` |
| Hardcoding handoff tool names | Fragile if agent names change | Let SDK auto-generate, or use `tool_name_override` |
| `on_handoff` with side effects that can fail | Handoff aborts on exception | Add error handling inside `on_handoff` |
