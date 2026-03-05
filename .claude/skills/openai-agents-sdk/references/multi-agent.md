# OpenAI Agents SDK — Multi-Agent Orchestration

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)

---

## Two Multi-Agent Patterns

| Pattern | When to Use | Mechanism |
|---------|-------------|-----------|
| **Triage → Handoff** | Route to ONE specialist based on intent | `handoffs=[agent_a, agent_b]` |
| **Orchestrator → Tools** | Call MULTIPLE specialists, combine results | `agent.as_tool(...)` |

---

## Pattern 1: Triage with Handoffs

The triage agent inspects input and fully hands off to the appropriate specialist. Control does not return to triage.

```python
from agents import Agent, Runner
import asyncio

# Specialists
billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle all billing questions: invoices, payments, refunds.",
    model="gpt-4o-mini",
)

technical_agent = Agent(
    name="Technical Agent",
    instructions="Handle all technical support: bugs, setup, errors.",
    model="gpt-4o-mini",
)

# Triage — routes to the right specialist
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a customer support router. "
        "For billing questions, hand off to Billing Agent. "
        "For technical issues, hand off to Technical Agent. "
        "For anything else, handle it yourself."
    ),
    handoffs=[billing_agent, technical_agent],
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(triage_agent, "My invoice is wrong", max_turns=10)
    print(result.final_output)
    print(f"Handled by: {result.last_agent.name}")

asyncio.run(main())
```

### Handoff with Custom Filter

Control what history the receiving agent sees:

```python
from agents import Agent, handoff
from agents.run import RunConfig

def filter_sensitive(inputs):
    # Strip previous agent messages, pass only the last user message
    return [item for item in inputs if item.get("role") == "user"][-1:]

specialist = Agent(name="Specialist", instructions="...")

triage = Agent(
    name="Triage",
    instructions="Route to specialist when needed.",
    handoffs=[
        handoff(
            agent=specialist,
            input_filter=filter_sensitive,
            tool_name_override="escalate_to_specialist",
            tool_description_override="Escalate complex issues to specialist.",
        )
    ],
)
```

---

## Pattern 2: Orchestrator with Agents as Tools

The orchestrator calls sub-agents like regular tools and combines results. **Control stays with the orchestrator throughout** — this is the critical difference from handoffs.

### How It Works (Mechanism)

When you call `agent.as_tool()`, the SDK:
1. Wraps the sub-agent inside a `FunctionTool` (same type as `@function_tool` creates)
2. The LLM sees it as a normal tool with a name, description, and input schema
3. When the LLM calls the tool, the SDK runs `Runner.run()` internally on the sub-agent
4. The sub-agent receives **only the generated input** (NOT the conversation history)
5. The sub-agent's output is returned to the orchestrator as a tool result
6. The orchestrator continues its own conversation — it decides what to do next

### Handoff vs Agent-as-Tool: When to Use Each

| Behavior | Handoff (`handoffs=`) | Agent-as-Tool (`as_tool()`) |
|---|---|---|
| **Control flow** | Transfers to new agent permanently | Main agent keeps control |
| **Conversation history** | New agent sees full history | Sub-agent sees only generated input |
| **Result handling** | New agent produces final output | Main agent processes sub-agent output |
| **Multi-call** | Cannot call multiple agents in one turn | Can call multiple tools per turn |
| **Use when** | Route to ONE specialist | Combine results from MULTIPLE specialists |

### Basic Example

```python
from agents import Agent, Runner
import asyncio

# Specialists (defined as pure agents)
spanish_agent = Agent(
    name="Spanish Translator",
    instructions="Translate the user's message to Spanish. Return only the translation.",
)

french_agent = Agent(
    name="French Translator",
    instructions="Translate the user's message to French. Return only the translation.",
)

summarizer_agent = Agent(
    name="Summarizer",
    instructions="Summarize the provided text in one sentence.",
)

# Orchestrator uses them as tools — stays in control
orchestrator = Agent(
    name="Orchestrator",
    instructions=(
        "You coordinate translation and summarization tasks. "
        "Call the relevant tools based on what the user needs."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate text to Spanish.",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate text to French.",
        ),
        summarizer_agent.as_tool(
            tool_name="summarize_text",
            tool_description="Summarize a block of text.",
        ),
    ],
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(
        orchestrator,
        "Translate 'Good morning' to Spanish and French, then summarize both.",
        max_turns=15,
    )
    print(result.final_output)

asyncio.run(main())
```

---

## `as_tool()` — Complete API Reference

The `as_tool()` method is defined on the `Agent` class. It returns a `FunctionTool` that wraps the sub-agent's execution.

```python
agent.as_tool(
    # --- Required (positional) ---
    tool_name: str | None,          # Name shown to LLM. Falls back to agent.name (slugified).
    tool_description: str | None,   # Description shown to LLM. Make this clear and specific.

    # --- Output Control ---
    custom_output_extractor: Callable[[RunResult | RunResultStreaming], Awaitable[str]] | None = None,
        # Extract specific fields from the sub-agent's RunResult.
        # If not provided, returns run_result.final_output as-is.

    # --- Conditional Enable/Disable ---
    is_enabled: bool | Callable[[RunContextWrapper[Any], AgentBase[Any]], MaybeAwaitable[bool]] = True,
        # Bool: always on/off.
        # Callable: dynamically enable/disable based on context at runtime.
        # When disabled, the tool is hidden from the LLM entirely.

    # --- Streaming ---
    on_stream: Callable[[AgentToolStreamEvent], MaybeAwaitable[None]] | None = None,
        # When provided, the nested agent runs in STREAMING mode.
        # Callback receives AgentToolStreamEvent dict with keys:
        #   "event": the stream event, "agent": current nested agent, "tool_call": originating call.

    # --- Execution Config ---
    run_config: RunConfig | None = None,     # Override model, settings, guardrails for this sub-agent.
    max_turns: int | None = None,            # Max turns for the nested run. ALWAYS set to prevent loops.
    hooks: RunHooks | None = None,           # Lifecycle hooks for the nested run.

    # --- Conversation Continuity ---
    previous_response_id: str | None = None, # For multi-turn with Responses API.
    conversation_id: str | None = None,      # For conversation continuity.
    session: Session | None = None,          # For persistent session state.

    # --- Error Handling ---
    failure_error_function: ToolErrorFunction | None = default_tool_error_function,
        # Custom error handler when the nested run fails.
        # If None, the exception propagates (crashes the parent).
        # Default: sends error message back to the LLM for graceful recovery.

    # --- Human-in-the-Loop ---
    needs_approval: bool | Callable[[RunContextWrapper[Any], dict[str, Any], str], Awaitable[bool]] = False,
        # Bool: always require/skip approval.
        # Callable: dynamically decide based on context and tool arguments.
        # When True, pauses execution until approved.

    # --- Structured Input ---
    parameters: type[Any] | None = None,     # Pydantic model or dataclass for structured tool input.
        # Replaces the default { "input": str } schema with your custom fields.
    input_builder: StructuredToolInputBuilder | None = None,
        # Custom function to format structured input before sending to the sub-agent.
    include_input_schema: bool = False,
        # When True with custom parameters, includes full JSON schema in the input sent to sub-agent.

) -> FunctionTool  # Returns a FunctionTool — same type as @function_tool creates.
```

---

## `as_tool()` Features with Examples

### Conditional Enable/Disable (`is_enabled`)

Dynamically show/hide a tool based on runtime context:

```python
from agents import Agent, RunContextWrapper, AgentBase
from pydantic import BaseModel

class AppContext(BaseModel):
    user_tier: str  # "free" or "premium"

def premium_only(ctx: RunContextWrapper[AppContext], agent: AgentBase) -> bool:
    """Only show this tool to premium users."""
    return ctx.context.user_tier == "premium"

advanced_agent = Agent(
    name="Advanced Analyzer",
    instructions="Perform deep analysis on the given data.",
)

orchestrator = Agent(
    name="Assistant",
    instructions="Help the user. Use advanced_analysis for premium users.",
    tools=[
        advanced_agent.as_tool(
            tool_name="advanced_analysis",
            tool_description="Deep analysis (premium feature).",
            is_enabled=premium_only,  # Hidden from free-tier users entirely
        ),
    ],
)
```

### Custom Output Extraction (`custom_output_extractor`)

Extract specific fields instead of raw `final_output`:

```python
from agents import Agent
from agents.result import RunResult

async def extract_translation_only(run_result: RunResult) -> str:
    """Extract just the translation, strip any extra commentary."""
    output = str(run_result.final_output)
    # Post-process the sub-agent output before returning to orchestrator
    return output.strip().split("\n")[0]  # First line only

translator = Agent(
    name="Translator",
    instructions="Translate text to Spanish. Return only the translation.",
)

orchestrator = Agent(
    name="Coordinator",
    tools=[
        translator.as_tool(
            tool_name="translate_spanish",
            tool_description="Translate to Spanish.",
            custom_output_extractor=extract_translation_only,
        ),
    ],
)
```

### Streaming from Nested Agent (`on_stream`)

Get real-time token output from the sub-agent:

```python
from agents import Agent

async def handle_nested_stream(event):
    """Process streaming events from the nested agent run."""
    stream_event = event["event"]       # The actual stream event
    nested_agent = event["agent"]       # Which nested agent is running
    tool_call = event["tool_call"]      # The originating tool call (or None)
    print(f"[{nested_agent.name}] {stream_event}")

researcher = Agent(
    name="Researcher",
    instructions="Research the topic thoroughly.",
)

orchestrator = Agent(
    name="Orchestrator",
    tools=[
        researcher.as_tool(
            tool_name="research",
            tool_description="Research a topic in depth.",
            on_stream=handle_nested_stream,  # Enables streaming mode for this sub-agent
        ),
    ],
)
```

### Structured Input (`parameters` + `input_builder`)

Replace the default `{ "input": str }` with custom typed fields:

```python
from pydantic import BaseModel, Field
from agents import Agent

class TranslationRequest(BaseModel):
    text: str = Field(description="Text to translate")
    target_language: str = Field(description="Target language code, e.g. 'es', 'fr'")
    formality: str = Field(default="neutral", description="'formal', 'informal', or 'neutral'")

translator = Agent(
    name="Universal Translator",
    instructions="Translate the given text to the target language with the specified formality.",
)

orchestrator = Agent(
    name="Coordinator",
    tools=[
        translator.as_tool(
            tool_name="translate",
            tool_description="Translate text to any language with formality control.",
            parameters=TranslationRequest,       # LLM sees these fields instead of generic "input"
            include_input_schema=True,            # Send full JSON schema to sub-agent for clarity
        ),
    ],
)
```

**How `parameters` changes what the LLM sees:**
- Without `parameters`: LLM sees `{ "input": "some text" }` — a single string field.
- With `parameters=TranslationRequest`: LLM sees `{ "text": "...", "target_language": "...", "formality": "..." }` — structured, typed fields with descriptions.

**What the sub-agent receives:** The SDK formats the structured data into a text prompt with the preamble: *"You are being called as a tool. The following is structured input data..."* followed by the JSON-serialized parameters and optionally the schema.

### Human-in-the-Loop Approval (`needs_approval`)

Require explicit approval before the sub-agent runs:

```python
from agents import Agent, RunContextWrapper

async def approve_if_expensive(
    ctx: RunContextWrapper, tool_args: dict, tool_name: str
) -> bool:
    """Only require approval for large data operations."""
    data = tool_args.get("input", "")
    return len(data) > 1000  # Approve small requests automatically

data_processor = Agent(
    name="Data Processor",
    instructions="Process and transform the given data.",
)

orchestrator = Agent(
    name="Coordinator",
    tools=[
        data_processor.as_tool(
            tool_name="process_data",
            tool_description="Process a data payload.",
            needs_approval=approve_if_expensive,  # Dynamic approval based on input size
        ),
    ],
)
```

### Execution Config Override (`run_config`, `max_turns`)

Control the sub-agent's model, settings, and turn limits:

```python
from agents import Agent
from agents.run import RunConfig
from agents.model_settings import ModelSettings

cheap_summarizer = Agent(
    name="Summarizer",
    instructions="Summarize the text concisely.",
    model="gpt-4o-mini",  # Agent-level default
)

orchestrator = Agent(
    name="Orchestrator",
    tools=[
        cheap_summarizer.as_tool(
            tool_name="summarize",
            tool_description="Summarize text in one sentence.",
            max_turns=3,  # Prevent runaway loops — ALWAYS set this
            run_config=RunConfig(
                model_settings=ModelSettings(temperature=0.2, max_tokens=500),
            ),
        ),
    ],
)
```

---

## Advanced: Runner Inside a `@function_tool`

For **maximum control** over sub-agent execution — custom error handling, retries, conditional logic, complex metadata — manually call `Runner.run()` inside a `@function_tool`:

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from agents.run import RunConfig
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: str

@function_tool
async def run_research_agent(
    wrapper: RunContextWrapper[AppContext],
    topic: str,
) -> str:
    """Research a topic in depth and return a detailed report."""
    research_agent = Agent(
        name="Researcher",
        instructions="Research the given topic thoroughly.",
        model="gpt-4o",
    )
    result = await Runner.run(
        research_agent,
        f"Research this topic: {topic}",
        max_turns=5,
        run_config=RunConfig(
            workflow_name="Research Sub-Task",
            trace_metadata={"user_id": wrapper.context.user_id},
        ),
    )
    return str(result.final_output)
```

### When to Use Runner-Inside-Tool vs `as_tool()`

| Use Case | `as_tool()` | Runner inside `@function_tool` |
|---|---|---|
| Simple delegation | Yes | Overkill |
| Custom error handling / retries | No | Yes |
| Conditional agent creation | No | Yes |
| Complex metadata / tracing | Limited (via `run_config`) | Full control |
| Access to `RunContextWrapper` | No (sub-agent gets clean input) | Yes (via `wrapper`) |
| Dynamic model selection | Via `run_config` | Full flexibility |

**Rule of thumb:** Use `as_tool()` by default. Use Runner-inside-tool only when you need logic that `as_tool()` parameters don't cover.

---

## RunConfig — Global Run Settings

```python
from agents.run import RunConfig
from agents.model_settings import ModelSettings

run_config = RunConfig(
    # Model override (applies to ALL agents in the run)
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.3, max_tokens=2048),

    # Safety
    input_guardrails=[my_input_guardrail],
    output_guardrails=[my_output_guardrail],

    # Handoff behavior
    handoff_input_filter=lambda inputs: inputs[-5:],  # last 5 items only
    nest_handoff_history=True,                         # collapse history on handoff

    # Tracing
    workflow_name="Customer Support Workflow",
    group_id=session_id,                  # links traces across turns
    trace_metadata={"user_id": user_id},
    tracing_disabled=False,
    trace_include_sensitive_data=False,   # hide inputs/outputs in traces
)

result = await Runner.run(agent, input, run_config=run_config, max_turns=20)
```

---

## Choosing a Pattern: Quick Guide

```
User message arrives
    │
    ├── "Route to one of N specialists"?
    │       └── Triage with handoffs
    │           Agent(handoffs=[a, b, c])
    │
    ├── "Call multiple specialists and combine"?
    │       └── Orchestrator with as_tool()
    │           Agent(tools=[a.as_tool(), b.as_tool()])
    │
    └── "Run sub-agent with full config control"?
            └── Runner.run() inside @function_tool
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Triage agent not handing off | Make instructions explicit: "You MUST hand off to X for Y questions" |
| Orchestrator calling wrong sub-agent | Provide clear `tool_description` on `.as_tool()` |
| History growing too large | Use `handoff_input_filter` to trim context |
| Missing `max_turns` in multi-agent | Always set — handoff chains can loop |
| Sub-agent models too expensive | Use `gpt-4o-mini` for specialists, `gpt-4o` for orchestrator |
