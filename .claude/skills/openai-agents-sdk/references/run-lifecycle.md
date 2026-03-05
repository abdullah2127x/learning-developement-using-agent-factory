# OpenAI Agents SDK — Run Lifecycle (Complete Reference)

Source: openai/openai-agents-python SDK source code (`agents/run.py`, `agents/run_config.py`, `agents/result.py`, `agents/run_state.py`, `agents/run_error_handlers.py`, `agents/guardrails.py`)

---

## What Is a "Run"?

A run is one complete execution of `Runner.run()`. It takes an agent + user input and produces a `RunResult` with a final output. Internally, it runs a **while loop** that keeps calling the LLM until the agent produces a final text answer, hands off, or exceeds `max_turns`.

```python
result = await Runner.run(agent, "Hello", max_turns=10)
# result.final_output  → the agent's answer
# result.last_agent    → which agent produced the answer
# result.new_items     → all items generated during the run
```

---

## Runner Methods — Three Ways to Run

### `Runner.run()` — Async (preferred)

```python
result = await Runner.run(
    starting_agent,                    # The agent to start with
    input,                             # str, list of items, or RunState (for resuming)
    *,
    context=None,                      # Your custom context object (e.g., UserInfo)
    max_turns=10,                      # Max LLM invocations before error (default: 10)
    hooks=None,                        # RunHooks instance for lifecycle callbacks
    run_config=None,                   # RunConfig for global settings
    error_handlers=None,               # Custom handlers for MaxTurnsExceeded
    previous_response_id=None,         # OpenAI Responses API conversation continuity
    auto_previous_response_id=False,   # Auto-chain response IDs across turns
    conversation_id=None,              # OpenAI server-managed conversation ID
    session=None,                      # Session for automatic history management
)
```

### `Runner.run_sync()` — Synchronous wrapper

Same parameters as `Runner.run()`, but blocks until complete. Uses `asyncio.run_until_complete()` internally.

```python
result = Runner.run_sync(agent, "Hello", max_turns=10)
```

**IMPORTANT:** Cannot be called from inside an already-running async event loop. If you're inside `async def`, use `await Runner.run()` instead.

### `Runner.run_streamed()` — Streaming

Returns immediately with a `RunResultStreaming` object. The run continues in a background `asyncio.Task`.

```python
streamed = Runner.run_streamed(agent, "Hello", max_turns=10)

async for event in streamed.stream_events():
    if event.type == "raw_response_event":
        # Token-by-token streaming
        print(event.data, end="", flush=True)
    elif event.type == "agent_updated_stream_event":
        # Handoff happened
        print(f"Now talking to: {event.new_agent.name}")
```

**Key difference:** `run()` and `run_sync()` return `RunResult`. `run_streamed()` returns `RunResultStreaming`.

---

## The Run Loop — Complete Flow

Every `Runner.run()` call executes this loop internally:

```
Runner.run(agent, input, max_turns=N)
    │
    ▼
┌─── INITIALIZATION ──────────────────────────────────────────┐
│  1. Validate hooks (must be RunHooks, not AgentHooks)       │
│  2. Create RunContextWrapper from your context               │
│  3. Resolve RunConfig (model, settings, guardrails)          │
│  4. Detect if resuming from RunState                         │
│  5. Set up tracing span                                      │
│  6. Initialize: current_turn=0, generated_items=[]           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── MAIN LOOP: while True ──────────────────────────────────┐
│                                                              │
│  ┌─ STEP 1: Turn Counter ─────────────────────────────────┐ │
│  │  current_turn += 1                                      │ │
│  │  if current_turn > max_turns:                           │ │
│  │    → Call error_handlers["max_turns"] if exists          │ │
│  │    → Otherwise raise MaxTurnsExceeded                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─ STEP 2: Input Guardrails (FIRST TURN ONLY) ───────────┐ │
│  │  Sequential guardrails run first                        │ │
│  │  Parallel guardrails run alongside the LLM call         │ │
│  │  If tripwire triggered → cancel LLM, raise exception    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─ STEP 3: Single Turn Execution ────────────────────────┐ │
│  │  a) Run agent start hooks (if first turn or new agent)  │ │
│  │  b) Resolve system prompt (instructions → string)       │ │
│  │  c) Gather tools + handoffs + output schema             │ │
│  │  d) Run on_llm_start hooks                              │ │
│  │  e) Call LLM API                                        │ │
│  │  f) Run on_llm_end hooks                                │ │
│  │  g) Process response → SingleStepResult                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─ STEP 4: Route Based on NextStep ──────────────────────┐ │
│  │                                                          │ │
│  │  NextStepFinalOutput:                                    │ │
│  │    → Run OUTPUT GUARDRAILS                               │ │
│  │    → Run on_agent_end / on_end hooks                     │ │
│  │    → Build RunResult                                     │ │
│  │    → return ✅                                           │ │
│  │                                                          │ │
│  │  NextStepHandoff:                                        │ │
│  │    → Run on_handoff hooks                                │ │
│  │    → Switch current_agent to new agent                   │ │
│  │    → Set flag: run agent_start hooks next turn           │ │
│  │    → continue loop ↩                                     │ │
│  │                                                          │ │
│  │  NextStepRunAgain:                                       │ │
│  │    → Tool calls were made and executed                   │ │
│  │    → Tool results added to message history               │ │
│  │    → continue loop ↩ (LLM needs to see results)         │ │
│  │                                                          │ │
│  │  NextStepInterruption:                                   │ │
│  │    → Tool needs approval (needs_approval=True)           │ │
│  │    → Build RunResult with interruptions                  │ │
│  │    → return (caller must approve and resume) ✅          │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## What Is a "Turn"?

A turn = **one LLM invocation**. The turn counter increments at the START of each loop iteration, before the LLM is called.

**What counts as ONE turn:**
- LLM produces a text answer → 1 turn
- LLM calls 3 tools in parallel → 1 turn (tools execute, but it's still one LLM call)
- LLM decides to hand off → 1 turn (the handoff decision)

**What does NOT count as a separate turn:**
- Tool execution (part of the same turn as the LLM call that requested it)
- Running guardrails (happens alongside or after the turn)
- Running hooks (fires during the turn, doesn't add turns)

### Turn Counting Examples

**Simple question (no tools):**
```
Turn 1: LLM → "Hello! How can I help?" → final output
Total: 1 turn
```

**One tool call:**
```
Turn 1: LLM → calls get_weather("Lahore") → tool executes → NextStepRunAgain
Turn 2: LLM → sees "sunny 32°C" → "The weather in Lahore is sunny!" → final output
Total: 2 turns
```

**Dependent tool calls:**
```
Turn 1: LLM → calls get_user_city() → returns "Lahore" → NextStepRunAgain
Turn 2: LLM → calls get_weather("Lahore") → returns "sunny" → NextStepRunAgain
Turn 3: LLM → "The weather in your city Lahore is sunny!" → final output
Total: 3 turns
```

**Parallel tool calls:**
```
Turn 1: LLM → calls get_user_context() AND get_weather("Dubai") → both execute → NextStepRunAgain
Turn 2: LLM → combines results → final output
Total: 2 turns (parallel tools = same turn)
```

**Handoff:**
```
Turn 1: Triage LLM → decides to hand off to Billing → NextStepHandoff
Turn 2: Billing LLM → "Let me help with your invoice" → final output
Total: 2 turns
```

**Handoff + tool:**
```
Turn 1: Triage LLM → handoff to Billing → NextStepHandoff
Turn 2: Billing LLM → calls lookup_invoice() → NextStepRunAgain
Turn 3: Billing LLM → "Your invoice #123 shows..." → final output
Total: 3 turns
```

---

## `max_turns` — Preventing Infinite Loops

```python
from agents import Runner

# Default: 10 turns
result = await Runner.run(agent, "Hello")

# Custom limit
result = await Runner.run(agent, "Hello", max_turns=5)
```

**Default value: `10`** (defined as `DEFAULT_MAX_TURNS` in `run_config.py`).

### What Happens When Exceeded

When `current_turn > max_turns`:

1. SDK builds a `MaxTurnsExceeded` error
2. Checks if `error_handlers["max_turns"]` exists
3. If handler exists → calls it, uses returned `final_output`
4. If no handler → **raises** `MaxTurnsExceeded` exception

```python
from agents.exceptions import MaxTurnsExceeded

# Exception class:
class MaxTurnsExceeded(AgentsException):
    message: str  # e.g., "Max turns (5) exceeded"
```

### How to Choose max_turns

| Agent Type | Recommended | Why |
|---|---|---|
| Simple Q&A (no tools) | 2-3 | May need 1-2 turns at most |
| Agent with 1-2 tools | 3-5 | Tool call + result processing |
| Agent with dependent tools | 5-7 | Chain: tool A → tool B → answer |
| Triage → specialist | 5-7 | Handoff + specialist may use tools |
| Multi-hop handoff chain | 10-15 | A → B → C, each may use tools |
| Complex orchestrator | 10-20 | Many tool calls, multiple rounds |

### Handling MaxTurnsExceeded

**Option 1: Try/except**
```python
from agents.exceptions import MaxTurnsExceeded

try:
    result = await Runner.run(agent, input, max_turns=5)
except MaxTurnsExceeded:
    print("Agent couldn't finish in 5 turns")
```

**Option 2: Error handler (graceful fallback)**
```python
async def handle_max_turns(input):
    """Return a fallback instead of crashing."""
    return "I couldn't complete that request. Please try a simpler question."

result = await Runner.run(
    agent,
    user_input,
    max_turns=5,
    error_handlers={"max_turns": handle_max_turns},
)
# If max_turns hit: result.final_output = fallback string
# If completed normally: result.final_output = agent's actual response
```

---

## The Four NextStep Types

After each LLM call, the SDK determines what to do next:

### `NextStepFinalOutput`

The LLM produced a final text answer (no tool calls, no handoffs).

```python
@dataclass
class NextStepFinalOutput:
    output: Any  # The final output (string or structured via output_type)
```

**What happens:** Output guardrails run → hooks fire → `RunResult` returned → loop exits.

### `NextStepRunAgain`

The LLM called one or more tools. The SDK executed them, and now needs to send the results back to the LLM.

```python
@dataclass
class NextStepRunAgain:
    pass
```

**What happens:** Tool results are added to message history → loop continues → LLM sees tool results next turn.

### `NextStepHandoff`

The LLM decided to hand off to another agent.

```python
@dataclass
class NextStepHandoff:
    new_agent: Agent[Any]  # The agent receiving control
```

**What happens:** Handoff hooks fire → `current_agent` switches → loop continues with new agent → agent start hooks fire for new agent.

### `NextStepInterruption`

A tool requires human approval before executing (when `needs_approval=True` on a tool or MCP server).

```python
@dataclass
class NextStepInterruption:
    interruptions: list[ToolApprovalItem]  # Tools awaiting approval
```

**What happens:** Run pauses → `RunResult` returned with `interruptions` list → caller must approve/deny and resume via `RunState`.

---

## `RunResult` — What You Get Back

```python
result = await Runner.run(agent, "Hello")
```

### Key Fields

| Field | Type | What It Contains |
|---|---|---|
| `result.final_output` | `Any` | The agent's final answer (string or structured output) |
| `result.last_agent` | `Agent` | The agent that produced the final output (important after handoffs) |
| `result.new_items` | `list[RunItem]` | ALL items generated: messages, tool calls, tool outputs, handoff items |
| `result.raw_responses` | `list[ModelResponse]` | Raw LLM API responses (for debugging/logging) |
| `result.input` | `list` | The original input items |
| `result.input_guardrail_results` | `list` | Results from input guardrails |
| `result.output_guardrail_results` | `list` | Results from output guardrails |
| `result.context_wrapper` | `RunContextWrapper` | The context wrapper (access `.usage` for token counts) |
| `result.interruptions` | `list[ToolApprovalItem]` | Tools awaiting approval (empty if no interruptions) |

### Useful Properties

```python
# Who handled the request?
print(result.last_agent.name)  # "Billing Agent" (after handoff)

# Token usage
print(result.context_wrapper.usage.total_tokens)

# All generated items for conversation history
history = result.to_input_list()

# Convert to RunState for resuming
state = result.to_state()
```

---

## `RunConfig` — Global Run Settings

`RunConfig` sets defaults for the entire run. Individual agents can override some of these.

```python
from agents import RunConfig, ModelSettings

run_config = RunConfig(
    # --- Model Override ---
    model="gpt-4o",                    # Override all agents' models for this run
    model_settings=ModelSettings(       # Override model settings for this run
        temperature=0.5,
        max_tokens=1000,
    ),

    # --- Handoff Settings ---
    handoff_input_filter=my_filter,     # Global filter for all handoffs
    nest_handoff_history=False,         # Collapse history on handoff (default: False)

    # --- Guardrails ---
    input_guardrails=[my_input_guard],  # Additional input guardrails (added to agent's)
    output_guardrails=[my_output_guard],# Additional output guardrails

    # --- Tracing ---
    tracing_disabled=False,             # Disable all tracing
    workflow_name="Customer Support",   # Name shown in trace dashboard
    trace_id=None,                      # Custom trace ID
    group_id=None,                      # Group related runs
)

result = await Runner.run(agent, "Hello", run_config=run_config)
```

### Priority Order (RunConfig vs Agent)

| Setting | Agent-level | RunConfig-level | Who Wins? |
|---|---|---|---|
| `model` | `Agent(model=...)` | `RunConfig(model=...)` | **RunConfig** overrides agent |
| `model_settings` | `Agent(model_settings=...)` | `RunConfig(model_settings=...)` | **Merged** — RunConfig fields override agent's non-None fields |
| `input_guardrails` | `Agent(input_guardrails=...)` | `RunConfig(input_guardrails=...)` | **Combined** — both run |
| `output_guardrails` | `Agent(output_guardrails=...)` | `RunConfig(output_guardrails=...)` | **Combined** — both run |
| `handoff_input_filter` | Per-handoff `input_filter` | `RunConfig(handoff_input_filter=...)` | Per-handoff wins if set |

---

## Input Guardrails — When They Run

Input guardrails validate the **user's input** before the agent processes it. They run **ONLY on the first turn** of the run.

```
Turn 1:
  ┌─ Sequential guardrails run first ─────────┐
  │  guardrail_1(input) → OK                  │
  │  guardrail_2(input) → OK                  │
  └────────────────────────────────────────────┘
  ┌─ Parallel guardrails + LLM run together ──┐
  │  guardrail_3(input) ──┐                   │
  │  LLM call ────────────┼── run in parallel │
  │  guardrail_4(input) ──┘                   │
  │                                            │
  │  If guardrail trips → cancel LLM call     │
  └────────────────────────────────────────────┘

Turn 2+: No input guardrails (they already passed)
```

**Key behavior:**
- Sequential guardrails (`run_in_parallel=False`) run BEFORE the LLM call
- Parallel guardrails (`run_in_parallel=True`) run ALONGSIDE the LLM call
- If a tripwire fires during parallel execution, the LLM task is cancelled
- Input guardrails fire only on turn 1 — not on subsequent turns after tool calls

---

## Output Guardrails — When They Run

Output guardrails validate the **agent's final output** before returning to the caller. They run ONLY when `NextStepFinalOutput` is reached.

```
LLM produces final answer
    │
    ▼
┌─ Output Guardrails ──────────────────────────┐
│  All guardrails run in parallel               │
│  If any tripwire triggers:                    │
│    → Cancel remaining guardrails              │
│    → Raise OutputGuardrailTripwireTriggered   │
│  If all pass:                                 │
│    → Build RunResult with final_output        │
└───────────────────────────────────────────────┘
```

**Key behavior:**
- Output guardrails are from agent's `output_guardrails` + RunConfig's `output_guardrails` (combined)
- They do NOT run on tool call turns — only on the final output turn
- They do NOT run after handoffs — only when the final agent produces output

---

## `RunState` — Resuming Interrupted Runs

When a run is interrupted (tool needs approval), you can resume it:

```python
# Initial run — tool needs approval
result = await Runner.run(agent, "Delete file X", max_turns=10)

if result.interruptions:
    # Run paused — tool awaiting approval
    print(f"Tool needs approval: {result.interruptions[0]}")

    # Convert result to resumable state
    state = result.to_state()

    # Approve the tool call
    state.approve(result.interruptions[0])

    # Resume the run — pass RunState as input
    result = await Runner.run(agent, state)
    print(result.final_output)  # Now includes tool result
```

**RunState preserves:**
- Current turn count (resumes where it left off)
- Current agent (after handoffs)
- All generated items so far
- All model responses
- Guardrail results
- Conversation/response IDs

---

## `RunErrorHandlers` — Graceful Error Handling

Instead of crashing on `MaxTurnsExceeded`, provide a handler:

```python
from agents import Runner

# Handler receives error info and returns a fallback output
async def handle_max_turns(input):
    return "Sorry, I ran out of steps. Please try again with a simpler request."

result = await Runner.run(
    agent,
    "Complex multi-step task",
    max_turns=3,
    error_handlers={"max_turns": handle_max_turns},
)

# If max_turns exceeded: result.final_output = handler's return value
# If completed normally: result.final_output = agent's actual answer
```

**Currently supported error types:**
- `"max_turns"` — handles `MaxTurnsExceeded`

---

## Conversation History — `to_input_list()`

After a run completes, use `to_input_list()` to build input for the next run (multi-turn conversation):

```python
# First message
result1 = await Runner.run(agent, "Hello, my name is Abdullah")

# Build history from result
history = result1.to_input_list()

# Second message — agent remembers the first
result2 = await Runner.run(agent, history + [{"role": "user", "content": "What's my name?"}])
# → "Your name is Abdullah"
```

**`to_input_list()`** returns all items (input + generated) in a format the SDK can accept as input for the next run.

---

## Session — Automatic History Management

Instead of manually managing history with `to_input_list()`, use a `Session`:

```python
from agents import SQLiteSession

session = SQLiteSession("conversations.db")

# Each run automatically loads/saves history
result1 = await Runner.run(agent, "Hi, I'm Abdullah", session=session)
result2 = await Runner.run(agent, "What's my name?", session=session)
# → "Your name is Abdullah" (history auto-loaded)
```

See `references/sessions.md` for full details on sessions.

---

## Complete Lifecycle Timeline

For a run where the user asks a question, the agent calls a tool, then responds:

```
1.  Runner.run(agent, "What's the weather?", max_turns=5) called
2.  Initialize: context, hooks, config, tracing
3.  current_turn = 0

--- TURN 1 ---
4.  current_turn = 1 (≤ 5, OK)
5.  Input guardrails run (first turn only)
6.  Hook: on_agent_start(agent)
7.  Resolve instructions → system prompt
8.  Gather tools list
9.  Hook: on_llm_start(agent, system_prompt, messages)
10. LLM API call → response: tool_call(get_weather, "Lahore")
11. Hook: on_llm_end(agent, response)
12. Hook: on_tool_start(agent, get_weather)
13. Execute get_weather("Lahore") → "sunny, 32°C"
14. Hook: on_tool_end(agent, get_weather, "sunny, 32°C")
15. NextStep = NextStepRunAgain → continue loop

--- TURN 2 ---
16. current_turn = 2 (≤ 5, OK)
17. (No input guardrails — not first turn)
18. Hook: on_llm_start(agent, system_prompt, messages + tool_result)
19. LLM API call → response: "The weather in Lahore is sunny, 32°C!"
20. Hook: on_llm_end(agent, response)
21. NextStep = NextStepFinalOutput
22. Output guardrails run
23. Hook: on_agent_end(agent, "The weather in Lahore is sunny, 32°C!")
24. Build RunResult → return ✅

--- RESULT ---
25. result.final_output = "The weather in Lahore is sunny, 32°C!"
26. result.last_agent = agent
27. result.new_items = [tool_call, tool_result, assistant_message]
```

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| `max_turns=1` with tools | Agent calls tool but can't see result | Set `max_turns` ≥ 2 for agents with tools |
| Not setting `max_turns` at all | Default 10 may be too low for complex chains | Set explicitly based on your agent's needs |
| Calling `run_sync()` from async code | `RuntimeError: event loop already running` | Use `await Runner.run()` inside async functions |
| Ignoring `result.interruptions` | Tool approvals are silently lost | Check `result.interruptions` and resume with `RunState` |
| No `error_handlers` for `max_turns` | Unhandled exception crashes your app | Add error handler or try/except |
| Expecting input guardrails on every turn | They only run on turn 1 | Design guardrails knowing they validate initial input only |
| Expecting output guardrails after handoffs | They run only on final output | The final agent's output is validated, not intermediate ones |

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|---|---|---|
| Setting `max_turns=100` "to be safe" | A confused agent burns tokens looping | Set realistic limits; use error handlers for graceful fallback |
| Relying on `max_turns` as the only safety net | Doesn't prevent harmful tool calls | Combine with guardrails and `needs_approval` on sensitive tools |
| Using `run_sync()` everywhere | Blocks the thread, can't do concurrent work | Use `await Runner.run()` for production async code |
| Building manual conversation history | Error-prone, easy to corrupt format | Use `to_input_list()` or `Session` for automatic management |
| Running heavy guardrails sequentially | Adds latency to every request | Set `run_in_parallel=True` on guardrails that can run alongside LLM |
