# OpenAI Agents SDK — Guardrails & Safety

Source: openai/openai-agents-python official docs (https://openai.github.io/openai-agents-python/guardrails/)

---

## Overview

Guardrails perform **checks and validations** on user input and agent output. They help prevent malicious usage, screen inappropriate content, validate quality, and short-circuit expensive model calls when issues are detected early.

---

## Guardrail Types

| Type | Scope | When It Runs | Decorator | Tripwire Exception |
|------|-------|-------------|-----------|-------------------|
| **Input guardrail** | Validates user input | Before/parallel with **first agent** only | `@input_guardrail` | `InputGuardrailTripwireTriggered` |
| **Output guardrail** | Validates agent response | After **final agent** produces output only | `@output_guardrail` | `OutputGuardrailTripwireTriggered` |
| **Tool input guardrail** | Validates tool arguments | Before every `@function_tool` call | `@tool_input_guardrail` | Rejects with message OR raises exception |
| **Tool output guardrail** | Validates tool return value | After every `@function_tool` call | `@tool_output_guardrail` | Rejects with message OR raises exception |

### Workflow Boundaries (Critical)

- **Input guardrails** run only for the **first agent** in a chain — NOT for agents reached via handoffs.
- **Output guardrails** run only for the **final agent** that produces the output — NOT for intermediate agents.
- **Tool guardrails** run on **every** `@function_tool` call, including in workflows with managers, handoffs, or delegated specialists.
- If you need checks around individual tool calls in multi-agent workflows, use **tool guardrails** — don't rely solely on input/output guardrails.

### Tool Guardrail Limitation

Tool guardrails apply **only** to function tools created with `@function_tool`. They do NOT apply to:
- Handoffs
- Hosted tools (WebSearch, CodeInterpreter, etc.)
- Built-in execution tools
- `Agent.as_tool()` wrappers

---

## Execution Modes (Parallel vs Blocking)

Input guardrails support two execution modes via `run_in_parallel`:

| Mode | Parameter | Behavior | Trade-off |
|------|-----------|----------|-----------|
| **Parallel** (default) | `run_in_parallel=True` | Guardrail runs **concurrently** with agent | Best latency, but agent may consume tokens before guardrail fails |
| **Blocking** | `run_in_parallel=False` | Guardrail completes **before** agent starts | If tripwire triggers, agent never executes — no wasted tokens, no tool side effects |

**Output guardrails** do NOT support `run_in_parallel` — they always run after the agent completes.

### When to Use Blocking Mode

Use `run_in_parallel=False` when:
- You want to **save tokens** by not running the agent if input is invalid
- Your tools have **side effects** (DB writes, API calls) that shouldn't execute on bad input
- You're using an **expensive model** and want to gate it with a cheap guardrail check first

---

## Input Guardrail

Runs on user input. Can use a separate cheap/fast agent to classify the input.

### How It Works

```
1. Guardrail receives the SAME input passed to the agent
2. Guardrail function runs → produces GuardrailFunctionOutput
3. SDK wraps it in InputGuardrailResult
4. If tripwire_triggered = True → raises InputGuardrailTripwireTriggered
5. If tripwire_triggered = False → agent proceeds normally
```

### Complete Example (Official — Math Homework Checker)

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")
    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")
```

### Function Signature

```python
@input_guardrail
async def my_guardrail(
    ctx: RunContextWrapper[YourContextType],  # or RunContextWrapper[None]
    agent: Agent,
    input: str | list[TResponseInputItem],    # NOT just str — can be message list
) -> GuardrailFunctionOutput:
    return GuardrailFunctionOutput(
        output_info=any_metadata,        # Any — stored for logging/auditing
        tripwire_triggered=True/False,   # True = block, False = allow
    )
```

**Key**: The `input` parameter is `str | list[TResponseInputItem]` — it can be a plain string OR a list of message dicts (when using sessions or `to_input_list()`).

---

## Output Guardrail

Validates the agent's **final response** before returning it. Runs only after the final agent completes.

### How It Works

```
1. Agent produces final output (typed via output_type)
2. Guardrail receives the output (as the agent's output_type, NOT raw str)
3. Guardrail function runs → produces GuardrailFunctionOutput
4. SDK wraps it in OutputGuardrailResult
5. If tripwire_triggered = True → raises OutputGuardrailTripwireTriggered
6. If tripwire_triggered = False → output returned normally
```

### Complete Example (Official — Math Output Checker)

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

class MessageOutput(BaseModel):
    response: str

class MathOutput(BaseModel):
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")
    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")
```

### Function Signature

```python
@output_guardrail
async def my_guardrail(
    ctx: RunContextWrapper[YourContextType],
    agent: Agent,
    output: YourOutputType,  # The agent's output_type — NOT raw str
) -> GuardrailFunctionOutput:
    return GuardrailFunctionOutput(
        output_info=any_metadata,
        tripwire_triggered=True/False,
    )
```

**Key**: The `output` parameter type must match the agent's `output_type`. If the agent has `output_type=MessageOutput`, the guardrail receives a `MessageOutput` instance — NOT a string.

---

## Tool-Level Guardrails

Applied per `@function_tool` call — validate arguments before execution and return values after.

### Three Behaviors

| Behavior | What Happens | Use When |
|----------|-------------|----------|
| **`allow()`** | Tool executes normally | Input/output passes validation |
| **`reject_content(message)`** | Tool call is skipped, message sent back to agent | Bad input/output but agent should continue |
| **`raise_exception()`** | Execution halts entirely | Critical violation, stop everything |

### Complete Example (Official)

```python
import json
from agents import (
    Agent,
    Runner,
    ToolGuardrailFunctionOutput,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
)

# Block tool calls that contain secrets
@tool_input_guardrail
def block_secrets(data):
    args = json.loads(data.context.tool_arguments or "{}")
    if "sk-" in json.dumps(args):
        return ToolGuardrailFunctionOutput.reject_content(
            "Remove secrets before calling this tool."
        )
    return ToolGuardrailFunctionOutput.allow()

# Redact secrets from tool output
@tool_output_guardrail
def redact_output(data):
    text = str(data.output or "")
    if "sk-" in text:
        return ToolGuardrailFunctionOutput.reject_content(
            "Output contained sensitive data."
        )
    return ToolGuardrailFunctionOutput.allow()

@function_tool(
    tool_input_guardrails=[block_secrets],
    tool_output_guardrails=[redact_output],
)
def classify_text(text: str) -> str:
    """Classify text for internal routing."""
    return f"length:{len(text)}"

agent = Agent(name="Classifier", tools=[classify_text])
result = Runner.run_sync(agent, "hello world")
print(result.final_output)
```

### Function Signatures

```python
@tool_input_guardrail
def my_input_guard(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    # data.context  → ToolContext[Any] (has .tool_arguments, .tool_name, etc.)
    # data.agent    → Agent[Any]
    return ToolGuardrailFunctionOutput.allow()

@tool_output_guardrail
def my_output_guard(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    # data.context  → ToolContext[Any]
    # data.agent    → Agent[Any]
    # data.output   → Any (the tool's return value)
    return ToolGuardrailFunctionOutput.allow()
```

**Key**: Tool guardrails can be **sync or async** — both work. Agent-level guardrails (input/output) must be **async**.

### ToolGuardrailFunctionOutput API

```python
from agents import ToolGuardrailFunctionOutput

# Allow — tool proceeds normally
ToolGuardrailFunctionOutput.allow(output_info=None)

# Reject — tool call skipped, message sent to agent, execution continues
ToolGuardrailFunctionOutput.reject_content("Reason for rejection", output_info=None)

# Raise — execution halts entirely
ToolGuardrailFunctionOutput.raise_exception(output_info=None)
```

`output_info` is optional metadata (Any type) stored for auditing/logging.

---

## Guardrails via RunConfig (Global)

Apply guardrails to ALL agents in a run — useful for organization-wide safety policies:

```python
from agents.run import RunConfig

run_config = RunConfig(
    input_guardrails=[safety_guardrail],
    output_guardrails=[pii_guardrail],
)

result = await Runner.run(agent, user_input, run_config=run_config)
```

**Note**: RunConfig guardrails are additive — they run alongside any agent-level guardrails.

---

## Tripwire Mechanism

When a guardrail triggers its tripwire:

1. SDK immediately raises `InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered`
2. Agent execution is **halted**
3. No further processing occurs

The exception object contains:
- `e.guardrail` — the guardrail that triggered
- `e.output` — the `GuardrailFunctionOutput` with `output_info` (your metadata/reasoning)

---

## Core Data Types Reference

```python
from agents import (
    # Decorators
    input_guardrail,
    output_guardrail,
    tool_input_guardrail,
    tool_output_guardrail,

    # Output types
    GuardrailFunctionOutput,          # For input/output guardrails
    ToolGuardrailFunctionOutput,      # For tool guardrails

    # Exceptions
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,

    # Context
    RunContextWrapper,
    TResponseInputItem,
)

# GuardrailFunctionOutput fields:
#   output_info: Any              — metadata for auditing
#   tripwire_triggered: bool      — True = block, False = allow

# ToolGuardrailFunctionOutput class methods:
#   .allow(output_info=None)
#   .reject_content(message, output_info=None)
#   .raise_exception(output_info=None)

# ToolInputGuardrailData fields:
#   context: ToolContext[Any]     — has .tool_arguments, .tool_name
#   agent: Agent[Any]

# ToolOutputGuardrailData fields:
#   context: ToolContext[Any]
#   agent: Agent[Any]
#   output: Any                   — the tool's return value
```

---

## Exception Handling Pattern

```python
from agents import InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from agents.exceptions import MaxTurnsExceeded

async def safe_run(agent, user_input: str, ctx=None) -> str:
    try:
        result = await Runner.run(agent, user_input, context=ctx, max_turns=15)
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        # e.guardrail — which guardrail triggered
        # e.output — GuardrailFunctionOutput with output_info
        return "I'm unable to process that request."
    except OutputGuardrailTripwireTriggered as e:
        # e.guardrail, e.output available for logging
        return "I couldn't generate a safe response for that."
    except MaxTurnsExceeded:
        return "The request took too many steps. Please try a simpler query."
    except Exception as e:
        # Log unexpected errors
        raise
```

---

## Best Practices

| Practice | Why |
|----------|-----|
| Use `gpt-4o-mini` for guardrail agents | Runs in parallel — keep it cheap and fast |
| Use `run_in_parallel=False` for costly agents | Prevents wasting tokens on blocked input |
| Catch both tripwire exceptions | `InputGuardrailTripwireTriggered` and `OutputGuardrailTripwireTriggered` |
| Return user-friendly messages on block | Don't expose internal guardrail reasons to users |
| Log `output_info` for auditing | Contains the guardrail agent's reasoning |
| Use tool guardrails in multi-agent workflows | Input/output guardrails only cover first/last agent |
| Match output guardrail type to `output_type` | Output guardrail receives the agent's `output_type`, not raw str |
| Prefer tool guardrails for sensitive tools | Scoped per-tool, runs on every call including in handoff chains |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Using `output: str` in output guardrail | Type mismatch — receives agent's `output_type` | Match the type: `output: MessageOutput` |
| Using `input: str` only in input guardrail | Misses list input from sessions/`to_input_list()` | Use `input: str \| list[TResponseInputItem]` |
| Relying on input guardrails for handoff chains | Input guardrails only run for the FIRST agent | Use tool guardrails for per-tool validation |
| Not catching tripwire exceptions | Unhandled exception crashes the app | Always `try/except` both tripwire types |
| Guardrail agent using expensive model | Wasted cost — guardrails run on every request | Use `gpt-4o-mini` for guardrail checker agents |
| Assuming output guardrails run after every agent | They only run for the FINAL agent | Design guardrails knowing the workflow boundaries |
| Putting tool guardrails on `Agent.as_tool()` | Tool guardrails only work with `@function_tool` | Use input/output guardrails on the sub-agent instead |
| Sync function for `@input_guardrail` | Input/output guardrail functions must be async | Always use `async def` for agent-level guardrails |
