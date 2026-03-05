# OpenAI Agents SDK — Guardrails & Safety

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)

---

## Guardrail Types

| Type | Scope | Decorator | Tripwire Exception |
|------|-------|-----------|-------------------|
| **Input guardrail** | Validates user input before agent runs | `@input_guardrail` | `InputGuardrailTripwireTriggered` |
| **Output guardrail** | Validates agent final response | `@output_guardrail` | `OutputGuardrailTripwireTriggered` |
| **Tool input guardrail** | Validates args before tool executes | `@tool_input_guardrail` | Rejects with message to agent |
| **Tool output guardrail** | Validates tool return value | `@tool_output_guardrail` | Rejects with message to agent |

---

## Input Guardrail

Runs in parallel with the agent. If tripwire triggers, `InputGuardrailTripwireTriggered` is raised.

```python
from pydantic import BaseModel
from agents import (
    Agent, Runner, RunContextWrapper,
    GuardrailFunctionOutput, InputGuardrailTripwireTriggered,
    input_guardrail,
)

class IsSafeInput(BaseModel):
    is_safe: bool
    reason: str

safety_checker = Agent(
    name="Safety Checker",
    instructions="Check if the user's input is safe and appropriate. Flag harmful, offensive, or policy-violating content.",
    output_type=IsSafeInput,
    model="gpt-4o-mini",
)

@input_guardrail
async def safety_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(safety_checker, input, context=ctx.context)
    check: IsSafeInput = result.final_output
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_safe,
    )

main_agent = Agent(
    name="Assistant",
    instructions="Help the user with their questions.",
    input_guardrails=[safety_guardrail],
)

async def handle_message(user_input: str):
    try:
        result = await Runner.run(main_agent, user_input, max_turns=10)
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        return "I can't help with that request."
```

---

## Output Guardrail

Validates the agent's final response before it's returned.

```python
from pydantic import BaseModel
from agents import (
    Agent, Runner, RunContextWrapper,
    GuardrailFunctionOutput, OutputGuardrailTripwireTriggered,
    output_guardrail,
)

class ContainsPII(BaseModel):
    has_pii: bool
    pii_types: list[str]

pii_checker = Agent(
    name="PII Checker",
    instructions="Check if the text contains PII (email, phone, SSN, credit card). List detected types.",
    output_type=ContainsPII,
    model="gpt-4o-mini",
)

@output_guardrail
async def pii_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(pii_checker, str(output), context=ctx.context)
    check: ContainsPII = result.final_output
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.has_pii,
    )

main_agent = Agent(
    name="Assistant",
    instructions="Help the user. Never expose PII.",
    output_guardrails=[pii_guardrail],
)

async def handle(user_input: str):
    try:
        result = await Runner.run(main_agent, user_input)
        return result.final_output
    except OutputGuardrailTripwireTriggered as e:
        return "Response contained sensitive data and was blocked."
```

---

## Tool-Level Guardrails

Applied per tool call — block or allow based on args/output.

```python
import json
from agents import (
    Agent, Runner,
    ToolGuardrailFunctionOutput,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
)

# Block tool calls that contain secrets
@tool_input_guardrail
def block_secrets_in_args(data) -> ToolGuardrailFunctionOutput:
    args = json.loads(data.context.tool_arguments or "{}")
    if any(k in json.dumps(args).lower() for k in ["sk-", "api_key", "password", "secret"]):
        return ToolGuardrailFunctionOutput.reject_content(
            "Remove sensitive data before calling this tool."
        )
    return ToolGuardrailFunctionOutput.allow()

# Redact secrets from tool output
@tool_output_guardrail
def redact_secrets_in_output(data) -> ToolGuardrailFunctionOutput:
    output = str(data.output or "")
    if "sk-" in output or "password" in output.lower():
        return ToolGuardrailFunctionOutput.reject_content(
            "Tool output contained sensitive data and was redacted."
        )
    return ToolGuardrailFunctionOutput.allow()

@function_tool(
    tool_input_guardrails=[block_secrets_in_args],
    tool_output_guardrails=[redact_secrets_in_output],
)
async def query_database(query: str) -> str:
    """Execute a database query and return results."""
    return await db.execute(query)
```

---

## Guardrails via RunConfig (Global)

Apply guardrails to ALL agents in a run:

```python
from agents.run import RunConfig

run_config = RunConfig(
    input_guardrails=[safety_guardrail],
    output_guardrails=[pii_guardrail],
)

result = await Runner.run(agent, user_input, run_config=run_config)
```

---

## Guardrail Best Practices

| Practice | Why |
|----------|-----|
| Use `gpt-4o-mini` for guardrail agents | Runs in parallel — keep it cheap and fast |
| Catch both tripwire exceptions | `InputGuardrailTripwireTriggered` and `OutputGuardrailTripwireTriggered` |
| Return user-friendly messages on block | Don't expose internal guardrail reasons |
| Log `output_info` for auditing | Contains the guardrail agent's reasoning |
| Prefer tool guardrails for sensitive tools | Scoped, faster than full output guardrail |
| Don't await `Runner.run()` inside sync guardrail | Use async guardrail functions for async calls |

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
        # Log: e.guardrail, e.output (GuardrailFunctionOutput)
        return "I'm unable to process that request."
    except OutputGuardrailTripwireTriggered as e:
        # Log: e.guardrail, e.output
        return "I couldn't generate a safe response for that."
    except MaxTurnsExceeded:
        return "The request took too many steps. Please try a simpler query."
    except Exception as e:
        # Log unexpected errors
        raise
```
