# OpenAI Agents SDK — Error Handling & Recovery

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)

---

## Overview

Errors happen: network issues, tool failures, invalid inputs. Agents need graceful recovery strategies.

---

## Tool Errors (Agents Handle Automatically)

When a tool fails, agent automatically:
1. Catches the error
2. Feeds error message back to LLM
3. LLM decides: retry with different args, or use different tool
4. Execution continues

```python
@function_tool
def divide(a: int, b: int) -> str:
    """Divide two numbers."""
    if b == 0:
        return "Error: Cannot divide by zero"
    return str(a / b)

# Agent will see the error message and adjust
# Example: user asks "5 / 0?" → tool returns error → agent explains to user
```

**Return error messages, don't raise exceptions** (unless you want to fail the entire run).

---

## Guardrail Tripwires

Guardrails can trigger exceptions to stop execution:

```python
from agents import (
    input_guardrail, GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
)

@input_guardrail
async def check_input(ctx, agent, input_text) -> GuardrailFunctionOutput:
    if "dangerous" in input_text.lower():
        # Tripwire: Stop execution
        raise InputGuardrailTripwireTriggered("Cannot process dangerous input")
    return GuardrailFunctionOutput(passed=True)

try:
    result = await Runner.run(agent, user_input)
except InputGuardrailTripwireTriggered as e:
    print(f"Input blocked: {e}")
```

---

## Exception Handling Pattern

```python
import asyncio
from agents import Agent, Runner

agent = Agent(...)

async def safe_run(user_input: str):
    try:
        result = await Runner.run(agent, user_input, timeout=30)
        return result.final_output
    except asyncio.TimeoutError:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

output = await safe_run("user question")
```

---

## Retry Strategies

### Automatic Retries

```python
import time

async def run_with_retries(agent, user_input, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await Runner.run(agent, user_input, timeout=30)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # exponential backoff
                print(f"Attempt {attempt + 1} failed. Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise

result = await run_with_retries(agent, "user input")
```

### Degraded Mode

```python
async def run_with_fallback(agent, user_input, fallback_text):
    try:
        result = await Runner.run(agent, user_input, timeout=10)
        return result.final_output
    except Exception as e:
        print(f"Agent failed: {e}")
        return fallback_text  # Graceful degradation
```

---

## Tool Failure Callbacks

Use `failure_error_function` to customize error handling:

```python
def tool_error_handler(tool_name: str, error: str) -> str:
    """Custom handling for tool failures."""
    if "connection" in error.lower():
        return "Network error. Please check your internet connection."
    elif "timeout" in error.lower():
        return "Operation timed out. Try with simpler input."
    else:
        return f"Tool '{tool_name}' failed: {error}"

agent = Agent(
    name="Assistant",
    instructions="...",
    tools=[my_tool],
    failure_error_function=tool_error_handler,
    model="gpt-4o-mini",
)
```

---

## Streaming Error Handling

Errors in streams need special handling:

```python
async def stream_with_error_handling(agent, user_input):
    try:
        async for event in Runner.run_streamed(agent, user_input):
            if event.type == "text":
                print(event.text, end="", flush=True)
            elif event.type == "error":
                print(f"\n⚠️ Error: {event.error}")
    except Exception as e:
        print(f"\n✗ Stream failed: {e}")
```

---

## Validation Error Handling

When structured output validation fails:

```python
from pydantic import BaseModel, ValidationError

class SafeResponse(BaseModel):
    status: str
    message: str

agent = Agent(
    name="Assistant",
    instructions="...",
    output_type=SafeResponse,
    model="gpt-4o-mini",
)

try:
    result = await Runner.run(agent, user_input)
    response = result.final_output
except ValidationError as e:
    print(f"Output validation failed: {e.errors()}")
```

Agent will **retry** if output doesn't match schema (with error feedback).

---

## Timeout Handling

```python
import asyncio

async def run_with_timeout(agent, user_input, timeout_seconds=30):
    try:
        result = await asyncio.wait_for(
            Runner.run(agent, user_input),
            timeout=timeout_seconds,
        )
        return result.final_output
    except asyncio.TimeoutError:
        return "Request timed out. Please try with simpler input."
```

---

## Comprehensive Error Handler

```python
from enum import Enum
import json

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorLog(BaseModel):
    severity: ErrorSeverity
    code: str
    message: str
    context: dict

async def run_with_logging(agent, user_input):
    errors = []

    try:
        result = await asyncio.wait_for(
            Runner.run(agent, user_input),
            timeout=30,
        )
        return result.final_output, errors

    except asyncio.TimeoutError:
        errors.append(ErrorLog(
            severity=ErrorSeverity.HIGH,
            code="TIMEOUT",
            message="Agent execution timed out",
            context={"input": user_input[:100]},
        ))
        return None, errors

    except Exception as e:
        errors.append(ErrorLog(
            severity=ErrorSeverity.CRITICAL,
            code=type(e).__name__,
            message=str(e),
            context={"input": user_input[:100]},
        ))
        return None, errors

output, errors = await run_with_logging(agent, user_input)
if errors:
    for error in errors:
        print(f"[{error.severity.value.upper()}] {error.code}: {error.message}")
```

---

## Best Practices

1. **Tools return errors as strings** (don't raise)
   ```python
   # ✅ Good
   @function_tool
   def get_file(path: str) -> str:
       try:
           with open(path) as f:
               return f.read()
       except FileNotFoundError:
           return f"Error: File '{path}' not found"
   ```

2. **Wrap runs with try/except**
   ```python
   try:
       result = await Runner.run(agent, input)
   except InputGuardrailTripwireTriggered:
       # Handle blocked input
   except OutputGuardrailTripwireTriggered:
       # Handle blocked output
   except Exception as e:
       # Handle other errors
   ```

3. **Set reasonable timeouts**
   ```python
   # Prevent hanging indefinitely
   result = await asyncio.wait_for(
       Runner.run(agent, input),
       timeout=30,  # 30 seconds max
   )
   ```

4. **Log errors for debugging**
   ```python
   import logging
   logger = logging.getLogger(__name__)

   try:
       result = await Runner.run(agent, input)
   except Exception as e:
       logger.error(f"Agent failed: {e}", exc_info=True)
   ```

5. **Provide user-friendly error messages**
   ```python
   # ❌ Bad
   "Error: FileNotFoundError: [Errno 2] No such file or directory"

   # ✅ Good
   "The requested file could not be found. Please check the path and try again."
   ```

---

## Error Codes Reference

| Code | Meaning | Recovery |
|------|---------|----------|
| `TIMEOUT` | Execution exceeded time limit | Retry with simpler input |
| `GUARDRAIL_TRIGGERED` | Input/output blocked | Review guardrail rules |
| `VALIDATION_ERROR` | Output doesn't match schema | Agent retries automatically |
| `TOOL_ERROR` | Tool function failed | Agent tries different approach |
| `NETWORK_ERROR` | Can't reach external API | Retry with backoff |
