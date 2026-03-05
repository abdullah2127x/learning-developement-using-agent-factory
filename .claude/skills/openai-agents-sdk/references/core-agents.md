# OpenAI Agents SDK — Core Agents, Tools & Context

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)

---

## Install

```bash
pip install openai-agents
export OPENAI_API_KEY=sk-proj-...
```

---

## Agent Configuration

```python
from agents import Agent

agent = Agent(
    name="Assistant",                          # required, shown in traces
    instructions="You are a helpful assistant.", # system prompt
    model="gpt-4o-mini",                       # optional, defaults to gpt-4o
    tools=[my_tool, another_tool],             # list of @function_tool functions
    handoffs=[specialist_agent],               # agents this one can hand off to
    output_type=MyPydanticModel,               # structured output (optional)
    mcp_servers=[mcp_server],                  # MCP servers (optional)
)
```

### Model Options

| Model | Use When |
|-------|----------|
| `gpt-4o-mini` | Dev, low cost, fast |
| `gpt-4o` | Production, complex reasoning |
| `gpt-4.1` | Latest, best capabilities |
| `gpt-4.1-mini` | Production + cost-efficient |
| `o3-mini` | Reasoning tasks |

---

## Function Tools

```python
from agents import function_tool, RunContextWrapper
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: str
    db: DatabaseSession            # injected dependency — NOT sent to LLM

@function_tool
async def get_user_profile(
    wrapper: RunContextWrapper[AppContext],
    user_id: str,
) -> dict:
    """Fetch the user's profile information. Use this when the user asks about their account."""
    # wrapper.context → your AppContext
    profile = await wrapper.context.db.get_user(user_id)
    return profile.model_dump()
```

**Rules for `@function_tool`:**
- Docstring → tool description shown to the LLM (make it descriptive)
- First param `wrapper: RunContextWrapper[TContext]` → injects context (optional)
- All other params → schema sent to LLM (use type annotations)
- Return any JSON-serializable type
- Always `async` for I/O operations

### Sync tool (no I/O)

```python
@function_tool
def calculate_tax(amount: float, rate: float) -> float:
    """Calculate tax for a given amount and rate."""
    return round(amount * rate, 2)
```

### Custom tool name/description

```python
from agents import function_tool

@function_tool(
    name_override="search_knowledge_base",
    description_override="Search the internal knowledge base for relevant articles.",
)
async def search_kb(wrapper: RunContextWrapper[AppContext], query: str) -> list[str]:
    results = await wrapper.context.db.search(query)
    return [r.title for r in results]
```

---

## RunContextWrapper

```python
from dataclasses import dataclass
from agents import RunContextWrapper

@dataclass
class AppContext:
    user_id: str
    locale: str = "en"
    # Add any dependencies: db session, config, auth token, etc.
    # NEVER include sensitive data that should go to the LLM

@function_tool
async def my_tool(wrapper: RunContextWrapper[AppContext], param: str) -> str:
    """Tool description."""
    user_id =  wrapper.context.user_id   # access your context
    usage = wrapper.usage               # token usage so far
    return f"Done for {user_id}"
```

**Key rule:** Context is **local only** — never sent to the LLM. Pass app state (DB sessions, user info, config) via context.

---

## Structured Output

```python
from pydantic import BaseModel, Field
from agents import Agent, Runner

class AnalysisResult(BaseModel):
    summary: str = Field(description="One-sentence summary")
    sentiment: str = Field(description="positive | negative | neutral")
    confidence: float = Field(description="0.0 to 1.0")
    key_points: list[str] = Field(description="Up to 5 key points")

agent = Agent(
    name="Analyzer",
    instructions="Analyze the given text and return structured results.",
    output_type=AnalysisResult,
)

result = await Runner.run(agent, "The product launch was a massive success!")
output: AnalysisResult = result.final_output   # fully typed
print(output.sentiment, output.confidence)
```

Supported `output_type` values: Pydantic `BaseModel`, dataclasses, `list[T]`, `TypedDict`.

---

## Runner Methods

```python
from agents import Runner

# Synchronous (blocking) — use in scripts, tests
result = Runner.run_sync(agent, "input text")

# Async — use in FastAPI, async frameworks
result = await Runner.run(agent, "input text", context=my_ctx)

# Streaming — use when you need real-time output
result = Runner.run_streamed(agent, "input text", context=my_ctx)
async for event in result.stream_events():
    ...   # see references/streaming.md

# With RunConfig
from agents.run import RunConfig
result = await Runner.run(
    agent,
    "input",
    run_config=RunConfig(model="gpt-4o", max_turns=10),
)

# result properties
result.final_output          # str or output_type instance
result.new_items             # list of new RunItems produced
result.last_agent            # the agent that produced final output
```

### max_turns

Always set in production:
```python
result = await Runner.run(agent, input, max_turns=15)
# Raises MaxTurnsExceeded if exceeded
```

---

## Dynamic Instructions

Instead of static instructions, pass a **function** that generates instructions at runtime:

```python
# Define a function that returns instructions
# IMPORTANT: context is RunContextWrapper — access your data via context.context
def dynamic_instructions(context, agent) -> str:
    """Generate instructions based on context."""
    if context is None:
        return "You are a helpful assistant."
    user = context.context  # <-- RunContextWrapper.context = your actual data
    return f"You are helping {user.name}. Be helpful and concise."

# Pass the function (not string) to Agent
agent = Agent(
    name="Assistant",
    instructions=dynamic_instructions,  # Function, not string!
)

# Instructions are computed on every run
result = await Runner.run(agent, "Hello", context=my_context)
```

**Use when**: Different users need different instructions, role-based behavior, personalization, language adaptation.

**Critical**: The `context` parameter in the function is a `RunContextWrapper`, NOT your data object directly. Always access your data via `context.context`.

### Async Dynamic Instructions (with I/O)

```python
async def async_instructions(context, agent) -> str:
    """Fetch preferences from database."""
    if not context:
        return "You are helpful."

    user = context.context  # <-- your actual data object
    prefs = await db.get_user_preferences(user.user_id)
    return f"Help {user.name}. Language: {prefs['language']}"

agent = Agent(instructions=async_instructions)
```

---

## Complete Level 2 Example

```python
import asyncio
import os
from dataclasses import dataclass
from pydantic import BaseModel
from agents import Agent, Runner, RunContextWrapper, function_tool

@dataclass
class Context:
    user_id: str

class TaskSummary(BaseModel):
    title: str
    priority: str
    estimated_minutes: int

@function_tool
async def get_user_tasks(wrapper: RunContextWrapper[Context]) -> list[dict]:
    """Get all tasks for the current user."""
    # Replace with real DB call
    return [{"id": 1, "title": "Review PR", "priority": "high"}]

agent = Agent(
    name="Task Assistant",
    instructions="Help the user manage their tasks. Be concise.",
    model="gpt-4o-mini",
    tools=[get_user_tasks],
)

async def main():
    ctx = Context(user_id="user_123")
    result = await Runner.run(
        agent,
        "What are my highest priority tasks?",
        context=ctx,
        max_turns=10,
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```
