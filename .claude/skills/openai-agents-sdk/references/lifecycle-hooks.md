# OpenAI Agents SDK — Lifecycle Hooks (Complete Reference)

Source: openai/openai-agents-python SDK source code (`agents/lifecycle.py`, `agents/run.py`, `agents/run_internal/`)

---

## What Are Lifecycle Hooks?

Lifecycle hooks let you **tap into events** that happen during an agent run — when an agent starts, when a tool is called, when the LLM responds, when a handoff occurs, when the agent finishes.

**Two separate hook systems exist:**

| System | Class | Attached To | Scope |
|--------|-------|-------------|-------|
| **Run Hooks** | `RunHooks` | `Runner.run(hooks=...)` | Fires for **every agent** in the run |
| **Agent Hooks** | `AgentHooks` | `Agent(hooks=...)` | Fires only for **that specific agent** |

Both systems fire **concurrently** (via `asyncio.gather`) when both are set. They don't block each other.

**Use hooks for:** logging, timing, token counting, analytics, debugging, audit trails, custom telemetry.

**Do NOT use hooks for:** modifying agent behavior, changing tool results, altering LLM input. Hooks are **observers**, not interceptors.

---

## The Agent Run Loop (What Triggers Hooks)

Every `Runner.run()` call executes this loop:

```
Runner.run(agent, input, max_turns=N)
    │
    ▼
┌─── LOOP (repeats up to max_turns) ──────────────────────────┐
│                                                              │
│  1. 🟢 on_agent_start / on_start                            │
│     (fires when agent becomes the active agent)              │
│                                                              │
│  2. 🔵 on_llm_start                                         │
│     (fires just before sending messages to the LLM)         │
│                                                              │
│  3. ── LLM processes and responds ──                        │
│                                                              │
│  4. 🔵 on_llm_end                                           │
│     (fires right after LLM response arrives)                │
│                                                              │
│  5. LLM response is one of:                                 │
│     │                                                        │
│     ├── Tool call(s) ──────────────────────────────────┐    │
│     │   For each tool:                                  │    │
│     │     🟡 on_tool_start                              │    │
│     │     ── tool executes ──                           │    │
│     │     🟡 on_tool_end                                │    │
│     │   → LOOP AGAIN (NextStepRunAgain)                 │    │
│     │                                                   │    │
│     ├── Handoff ───────────────────────────────────────┐│    │
│     │   🟠 on_handoff                                  ││    │
│     │   Switch to new agent                            ││    │
│     │   → LOOP AGAIN with new agent                    ││    │
│     │     (on_agent_start fires for new agent)         ││    │
│     │                                                  ││    │
│     └── Final text output ─────────────────────────────┘│    │
│         🔴 on_agent_end / on_end                         │    │
│         → EXIT LOOP, return result                       │    │
│                                                          │    │
└──────────────────────────────────────────────────────────┘
```

---

## RunHooks — Global Hooks (Observe All Agents)

`RunHooks` fires for **every agent** in the run. Pass it to `Runner.run()`.

### Full Class Definition

```python
from agents import RunHooks, RunContextWrapper, Agent
from agents.lifecycle import AgentHookContext
from agents.models.interface import ModelResponse
from agents.tool import Tool
from typing import Any, Optional

class MyRunHooks(RunHooks):

    async def on_agent_start(
        self,
        context: AgentHookContext,
        agent: Agent,
    ) -> None:
        """Called when an agent becomes the active agent.
        Fires at the start of a run, and again after each handoff.

        Args:
            context: AgentHookContext (extends RunContextWrapper with turn_input)
            agent: The agent that is about to run.
        """
        pass

    async def on_agent_end(
        self,
        context: AgentHookContext,
        agent: Agent,
        output: Any,
    ) -> None:
        """Called when an agent produces a final output (the run ends).

        Args:
            context: AgentHookContext
            agent: The agent that produced the output.
            output: The final output value (string or structured).
        """
        pass

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[str],
        input_items: list,
    ) -> None:
        """Called just before the LLM is invoked.

        Args:
            context: RunContextWrapper with shared state.
            agent: The agent making the LLM call.
            system_prompt: The resolved system prompt string (from instructions).
            input_items: The messages being sent to the LLM.
        """
        pass

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: ModelResponse,
    ) -> None:
        """Called immediately after the LLM response arrives.

        Args:
            context: RunContextWrapper
            agent: The agent that made the LLM call.
            response: The raw model response object.
        """
        pass

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
    ) -> None:
        """Called immediately before a tool is executed.

        Args:
            context: RunContextWrapper
            agent: The agent whose tool is being called.
            tool: The Tool instance being invoked.
        """
        pass

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called immediately after a tool finishes executing.

        Args:
            context: RunContextWrapper
            agent: The agent whose tool was called.
            tool: The Tool instance that was invoked.
            result: The string result returned by the tool.
        """
        pass

    async def on_handoff(
        self,
        context: RunContextWrapper,
        from_agent: Agent,
        to_agent: Agent,
    ) -> None:
        """Called when a handoff occurs between agents.

        Args:
            context: RunContextWrapper
            from_agent: The agent that is handing off (the current agent).
            to_agent: The agent that is receiving control.
        """
        pass
```

### Usage

```python
from agents import Agent, Runner, RunContextWrapper
from agents.lifecycle import RunHooks, AgentHookContext

class LoggingHooks(RunHooks):
    async def on_agent_start(self, context: AgentHookContext, agent):
        print(f"[START] {agent.name}")

    async def on_agent_end(self, context: AgentHookContext, agent, output):
        print(f"[END] {agent.name} → {output[:50]}")

    async def on_tool_start(self, context, agent, tool):
        print(f"[TOOL] {agent.name} calling {tool.name}")

    async def on_tool_end(self, context, agent, tool, result):
        print(f"[TOOL] {tool.name} returned: {result[:50]}")

    async def on_handoff(self, context, from_agent, to_agent):
        print(f"[HANDOFF] {from_agent.name} → {to_agent.name}")

# Pass to Runner.run()
result = await Runner.run(
    agent,
    "Hello",
    hooks=LoggingHooks(),   # ← fires for ALL agents in this run
    max_turns=5,
)
```

---

## AgentHooks — Per-Agent Hooks (Observe One Agent)

`AgentHooks` fires **only for the specific agent** it's attached to. Set it on the agent instance.

### Full Class Definition

```python
from agents import Agent, RunContextWrapper
from agents.lifecycle import AgentHooks, AgentHookContext
from agents.models.interface import ModelResponse
from agents.tool import Tool
from typing import Any, Optional

class MyAgentHooks(AgentHooks):

    async def on_start(
        self,
        context: AgentHookContext,
        agent: Agent,
    ) -> None:
        """Called when THIS agent becomes active.
        Fires at run start (if this is the starting agent) or after a handoff TO this agent.
        """
        pass

    async def on_end(
        self,
        context: AgentHookContext,
        agent: Agent,
        output: Any,
    ) -> None:
        """Called when THIS agent produces a final output."""
        pass

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[str],
        input_items: list,
    ) -> None:
        """Called just before THIS agent invokes the LLM."""
        pass

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: ModelResponse,
    ) -> None:
        """Called right after THIS agent receives LLM response."""
        pass

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
    ) -> None:
        """Called before THIS agent's tool executes."""
        pass

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after THIS agent's tool executes."""
        pass

    async def on_handoff(
        self,
        context: RunContextWrapper,
        agent: Agent,
        source: Agent,
    ) -> None:
        """Called when THIS agent receives a handoff FROM another agent.

        NOTE: This fires on the TARGET agent (the one being handed TO).
              The `source` is the agent that initiated the handoff.
        """
        pass
```

### Usage

```python
from agents import Agent
from agents.lifecycle import AgentHooks, AgentHookContext

class BillingLogger(AgentHooks):
    async def on_start(self, context: AgentHookContext, agent):
        print(f"[BILLING] Agent activated")

    async def on_end(self, context: AgentHookContext, agent, output):
        print(f"[BILLING] Responded: {output[:80]}")

    async def on_tool_start(self, context, agent, tool):
        print(f"[BILLING] Calling tool: {tool.name}")

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing questions.",
    hooks=BillingLogger(),   # ← fires ONLY for this agent
    model=model,
)
```

---

## RunHooks vs AgentHooks — Key Differences

| Aspect | RunHooks | AgentHooks |
|--------|----------|------------|
| **Attached to** | `Runner.run(hooks=...)` | `Agent(hooks=...)` |
| **Scope** | Fires for ALL agents in the run | Fires for ONLY that agent |
| **Agent start method** | `on_agent_start(ctx, agent)` | `on_start(ctx, agent)` |
| **Agent end method** | `on_agent_end(ctx, agent, output)` | `on_end(ctx, agent, output)` |
| **Handoff method** | `on_handoff(ctx, from_agent, to_agent)` | `on_handoff(ctx, agent, source)` |
| **Handoff perspective** | Sees both sides (from → to) | Sees only the target agent's side |
| **Use case** | Global logging, timing, analytics | Agent-specific monitoring |
| **Validation** | Must be `RunHooks` instance | Must be `AgentHooks` instance |

**IMPORTANT:** Do NOT pass `AgentHooks` to `Runner.run(hooks=...)` — the SDK validates and raises a `TypeError`:
```
TypeError: Run hooks must be instances of RunHooks.
Received agent-scoped hooks (MyAgentHooks).
Attach AgentHooks to an Agent via Agent(..., hooks=...).
```

---

## Both Hooks Fire Concurrently

When both `RunHooks` and `AgentHooks` are set, they fire at the **same time** via `asyncio.gather()`:

```python
# SDK internal code (simplified):
await asyncio.gather(
    run_hooks.on_agent_start(context, agent),       # RunHooks fires
    agent.hooks.on_start(context, agent),            # AgentHooks fires simultaneously
)
```

This means:
- Neither blocks the other
- Both see the same event at the same time
- If one raises an exception, it may cancel the other (standard asyncio.gather behavior)

---

## Complete Example: Timing + Logging

```python
import time
from agents import Agent, Runner, RunContextWrapper
from agents.lifecycle import RunHooks, AgentHooks, AgentHookContext

# ── Run-Level Hooks (fires for all agents) ───────────────────

class TimingHooks(RunHooks):
    def __init__(self):
        self.turn_start = None

    async def on_agent_start(self, context: AgentHookContext, agent):
        self.turn_start = time.time()
        print(f"\n{'='*50}")
        print(f"[RUN] Agent started: {agent.name}")

    async def on_agent_end(self, context: AgentHookContext, agent, output):
        elapsed = time.time() - self.turn_start if self.turn_start else 0
        print(f"[RUN] Agent finished: {agent.name} ({elapsed:.2f}s)")
        print(f"[RUN] Output: {str(output)[:100]}")
        print(f"{'='*50}\n")

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print(f"[RUN] LLM call starting for {agent.name}...")

    async def on_llm_end(self, context, agent, response):
        print(f"[RUN] LLM responded for {agent.name}")

    async def on_tool_start(self, context, agent, tool):
        print(f"[RUN] Tool {tool.name} starting...")

    async def on_tool_end(self, context, agent, tool, result):
        print(f"[RUN] Tool {tool.name} → {result[:60]}")

    async def on_handoff(self, context, from_agent, to_agent):
        print(f"[RUN] Handoff: {from_agent.name} → {to_agent.name}")


# ── Agent-Level Hooks (fires only for billing agent) ─────────

class BillingMetrics(AgentHooks):
    async def on_start(self, context: AgentHookContext, agent):
        print(f"  [BILLING] Activated — ready to handle billing query")

    async def on_tool_end(self, context, agent, tool, result):
        print(f"  [BILLING] Tool {tool.name} completed")

    async def on_end(self, context: AgentHookContext, agent, output):
        print(f"  [BILLING] Final response delivered")


# ── Agents ────────────────────────────────────────────────────

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing questions.",
    hooks=BillingMetrics(),    # ← per-agent hooks
    model=model,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route billing to Billing Agent.",
    handoffs=[billing_agent],
    model=model,
)

# ── Run ───────────────────────────────────────────────────────

result = await Runner.run(
    triage_agent,
    "My invoice is wrong",
    hooks=TimingHooks(),       # ← run-level hooks
    max_turns=10,
)
```

**Output would look like:**
```
==================================================
[RUN] Agent started: Triage Agent
[RUN] LLM call starting for Triage Agent...
[RUN] LLM responded for Triage Agent
[RUN] Handoff: Triage Agent → Billing Agent

==================================================
[RUN] Agent started: Billing Agent
  [BILLING] Activated — ready to handle billing query
[RUN] LLM call starting for Billing Agent...
[RUN] LLM responded for Billing Agent
[RUN] Agent finished: Billing Agent (1.23s)
[RUN] Output: I'm sorry to hear about the invoice issue. Could you share...
  [BILLING] Final response delivered
==================================================
```

Notice: `TimingHooks` (RunHooks) fires for BOTH agents. `BillingMetrics` (AgentHooks) fires ONLY for the billing agent.

---

## Hook Execution Order (Complete Timeline)

For a run where Triage hands off to Billing, and Billing calls a tool:

```
1.  RunHooks.on_agent_start(triage)         ← Triage becomes active
    AgentHooks(triage).on_start(triage)     ← if triage has hooks

2.  RunHooks.on_llm_start(triage, ...)      ← LLM called for triage
    AgentHooks(triage).on_llm_start(...)

3.  RunHooks.on_llm_end(triage, response)   ← LLM responds (handoff decision)
    AgentHooks(triage).on_llm_end(...)

4.  RunHooks.on_handoff(triage → billing)   ← Handoff occurs
    AgentHooks(billing).on_handoff(source=triage)

5.  RunHooks.on_agent_start(billing)        ← Billing becomes active
    AgentHooks(billing).on_start(billing)

6.  RunHooks.on_llm_start(billing, ...)     ← LLM called for billing
    AgentHooks(billing).on_llm_start(...)

7.  RunHooks.on_llm_end(billing, response)  ← LLM responds (tool call)
    AgentHooks(billing).on_llm_end(...)

8.  RunHooks.on_tool_start(billing, tool)   ← Tool about to execute
    AgentHooks(billing).on_tool_start(...)

9.  RunHooks.on_tool_end(billing, tool, result) ← Tool finished
    AgentHooks(billing).on_tool_end(...)

10. RunHooks.on_llm_start(billing, ...)     ← LLM called again (with tool result)
    AgentHooks(billing).on_llm_start(...)

11. RunHooks.on_llm_end(billing, response)  ← LLM responds (final text)
    AgentHooks(billing).on_llm_end(...)

12. RunHooks.on_agent_end(billing, output)  ← Run complete
    AgentHooks(billing).on_end(billing, output)
```

---

## Context Types in Hooks

### AgentHookContext (for on_start / on_end / on_agent_start / on_agent_end)

`AgentHookContext` extends `RunContextWrapper` and adds `turn_input`:

```python
class AgentHookContext(RunContextWrapper[TContext]):
    """Passed to agent start/end hooks."""
    # Inherits from RunContextWrapper:
    #   .context → your TContext object (e.g., UserInfo)
    #   .usage   → token usage so far
    # Adds:
    #   .turn_input → the input items for the current turn
```

### RunContextWrapper (for on_llm_start / on_llm_end / on_tool_start / on_tool_end / on_handoff)

```python
class RunContextWrapper(Generic[TContext]):
    """Wraps the context object you passed to Runner.run()."""
    # .context → your TContext object
    # .usage   → token usage so far
```

**Key point:** `context.context` gives you your custom context object (e.g., `UserInfo`). The double `.context` is because `RunContextWrapper.context` returns the inner TContext.

---

## Common Patterns

### Token Usage Tracking

```python
class UsageTracker(RunHooks):
    async def on_agent_end(self, context: AgentHookContext, agent, output):
        usage = context.usage
        print(f"Total tokens: {usage.total_tokens}")
        print(f"Input tokens: {usage.input_tokens}")
        print(f"Output tokens: {usage.output_tokens}")
```

### Tool Call Auditing

```python
class AuditHooks(RunHooks):
    def __init__(self):
        self.tool_calls = []

    async def on_tool_start(self, context, agent, tool):
        self.tool_calls.append({
            "agent": agent.name,
            "tool": tool.name,
            "timestamp": time.time(),
        })

    async def on_tool_end(self, context, agent, tool, result):
        self.tool_calls[-1]["result"] = result[:200]
        self.tool_calls[-1]["duration"] = time.time() - self.tool_calls[-1]["timestamp"]
```

### Handoff Tracking

```python
class HandoffTracker(RunHooks):
    def __init__(self):
        self.handoff_chain = []

    async def on_handoff(self, context, from_agent, to_agent):
        self.handoff_chain.append(f"{from_agent.name} → {to_agent.name}")

    async def on_agent_end(self, context, agent, output):
        if self.handoff_chain:
            print(f"Handoff chain: {' → '.join(self.handoff_chain)}")
```

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Passing `AgentHooks` to `Runner.run(hooks=...)` | `TypeError` raised | Use `Agent(hooks=...)` for AgentHooks, `Runner.run(hooks=...)` for RunHooks |
| Sync hook methods | Hooks must be `async` | Always use `async def` for all hook methods |
| Heavy work in hooks | Blocks the agent loop | Keep hooks lightweight; offload heavy work to background tasks |
| Raising exceptions in hooks | Can crash the run | Add try/except inside hooks if doing I/O |
| Expecting hooks to modify behavior | Hooks are observers only | Use guardrails or input_filter to modify behavior |
| Not subclassing `RunHooks`/`AgentHooks` | `TypeError` on validation | Always subclass from `RunHooks` or `AgentHooks` |

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|---|---|---|
| Using hooks to modify LLM input | Hooks can't change input | Use dynamic `instructions=` callable or guardrails |
| Using hooks to change tool results | Hooks see results but can't alter them | Modify the tool function itself |
| Blocking I/O in hooks (file writes, HTTP calls) | Slows down every turn | Use `asyncio.create_task()` for non-blocking side effects |
| One massive hook class that does everything | Hard to maintain | Separate concerns: `TimingHooks`, `AuditHooks`, etc. |
