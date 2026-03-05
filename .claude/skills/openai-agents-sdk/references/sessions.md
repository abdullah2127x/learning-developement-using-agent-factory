# OpenAI Agents SDK — Conversation History & Sessions

Source: openai/openai-agents-python SDK source code + official docs

---

## Overview

By default, each `Runner.run()` call is **stateless** — the agent has zero memory of previous messages. The SDK provides multiple approaches to enable multi-turn conversations:

| Approach | Persistence | Best For | Install | Complexity |
|----------|-------------|----------|---------|------------|
| **Manual: `to_input_list()`** | In-memory only (lost on restart) | Prototyping, scripts, full control | Built-in | Simple |
| **`SQLiteSession`** | SQLite file (sync) | Local dev, CLI apps | Built-in | Simple |
| **`AsyncSQLiteSession`** | SQLite file (async) | Async apps, FastAPI | Built-in | Simple |
| **`SQLAlchemySession`** | Any SQL DB (PostgreSQL/Neon, MySQL) | **Production** | `pip install openai-agents[sqlalchemy]` | Medium |
| **`RedisSession`** | Redis | Distributed, low-latency | `pip install openai-agents[redis]` | Medium |
| **`EncryptedSession`** | Wraps any session with encryption + TTL | Security-sensitive | `cryptography` | Medium |
| **`AdvancedSQLiteSession`** | SQLite + branching + usage tracking | Complex local apps | Built-in | Advanced |
| **`DaprSession`** | 30+ Dapr state stores | Cloud-native | Dapr SDK | Advanced |
| **`OpenAIConversationsSession`** | OpenAI Conversations API | Server-managed history | Built-in | Simple |
| **`OpenAIResponsesCompactionSession`** | OpenAI Responses API compaction | Token-optimized | Built-in | Simple |

---

## The Session Interface (What All Backends Implement)

All session backends implement the same contract. You must follow this interface if building a custom backend.

### `Session` Protocol (for third-party implementations)

```python
from agents.sessions import Session  # @runtime_checkable Protocol

class Session(Protocol):
    session_id: str
    session_settings: SessionSettings | None

    async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
        """Retrieve conversation history. If limit is set, return last N items."""
        ...

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        """Persist new conversation items (user input, assistant responses, tool calls)."""
        ...

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the most recent item."""
        ...

    async def clear_session(self) -> None:
        """Wipe all stored items for this session."""
        ...
```

### `SessionABC` (Abstract Base Class for subclassing)

```python
from agents.sessions import SessionABC
from abc import ABC, abstractmethod

class SessionABC(ABC):
    session_id: str
    session_settings: SessionSettings | None = None

    @abstractmethod
    async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]: ...

    @abstractmethod
    async def add_items(self, items: list[TResponseInputItem]) -> None: ...

    @abstractmethod
    async def pop_item(self) -> TResponseInputItem | None: ...

    @abstractmethod
    async def clear_session(self) -> None: ...
```

**All four methods are async.** `TResponseInputItem` is the serializable conversation item type from `agents.items`.

### How the Runner Uses Sessions

```
Runner.run(agent, input, session=session)
    │
    ├── 1. session.get_items()          ← Load history from storage
    │
    ├── 2. Merge history + new input    ← Customizable via session_input_callback
    │
    ├── 3. Run agent with full context  ← Agent sees entire conversation
    │
    └── 4. session.add_items(new_items) ← Persist all new items from this turn
```

**IMPORTANT:** Sessions are **incompatible** with `conversation_id`, `previous_response_id`, or `auto_previous_response_id` parameters on the Runner. Use one or the other, not both.

---

## Database Architecture (Two-Table Schema)

All SQL-based session backends (SQLite, SQLAlchemy) use a **two-table** pattern — NOT a single table with a JSON column.

### Schema

```sql
-- Table 1: Sessions (one row per conversation)
CREATE TABLE agent_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Messages (one row per conversation item)
CREATE TABLE agent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    message_data TEXT NOT NULL,          -- JSON-serialized conversation item
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_sessions (session_id) ON DELETE CASCADE
);

-- Index for fast lookups
CREATE INDEX idx_agent_messages_session_id ON agent_messages (session_id, id);
```

### How Messages Are Stored

- **Each message = one row** in `agent_messages`, with JSON in `message_data`
- **Serialization** (write): `json.dumps(item, separators=(",", ":"))` — compact JSON per item
- **Deserialization** (read): `json.loads(message_data)` — parsed back to Python dicts. Invalid JSON is **silently skipped**.
- **Ordering**: By auto-increment `id` (chronological insertion order)
- **Concurrency**: In-memory DBs use shared connection with mutex locks; file DBs use `PRAGMA journal_mode=WAL` for concurrent reads

---

## Approach 1: Manual — `result.to_input_list()` (In-Memory)

You manage conversation history yourself by passing the full message list back each run.

### How It Works

`result.to_input_list()` returns the **entire conversation** — user messages, agent responses, and tool call results — as a list of message dicts. You pass that list (plus the new user message) as input to the next run.

### Basic Example

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Reply very concisely.")

async def main():
    input_list = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break

        # Append new user message to history
        input_list.append({"role": "user", "content": user_input})

        # Run with full history
        result = await Runner.run(agent, input_list)
        print(f"Agent: {result.final_output}\n")

        # Replace input_list with full history (includes agent response + tool calls)
        input_list = result.to_input_list()
```

### What `to_input_list()` Returns

After a conversation like:
1. User: "What city is the Golden Gate Bridge in?"
2. Agent: "San Francisco"
3. User: "What state is it in?"

`result.to_input_list()` returns:
```python
[
    {"role": "user", "content": "What city is the Golden Gate Bridge in?"},
    {"role": "assistant", "content": "San Francisco"},
    {"role": "user", "content": "What state is it in?"},
    {"role": "assistant", "content": "California"},
]
```

When tools are called, it also includes `tool_calls` and `tool` role messages in the list.

### Pros & Cons

**Pros:**
- No extra dependencies
- Full control over what's in the history
- Can filter/truncate history before passing it

**Cons:**
- Lost on restart — in-memory only
- History grows unbounded (can hit context limits)
- You must manage the list yourself

### Truncating History (Prevent Context Overflow)

```python
MAX_HISTORY = 50  # Keep last 50 messages

input_list = result.to_input_list()

# Truncate if too long
if len(input_list) > MAX_HISTORY:
    input_list = input_list[-MAX_HISTORY:]
```

---

## Approach 2: `SQLiteSession` (Persistent Local Storage)

The SDK provides `SQLiteSession` which automatically saves/loads conversation history to a SQLite file. No manual list management needed.

### How It Works

1. Create a `SQLiteSession` with a session ID and optional DB file path.
2. Pass it to `Runner.run()` via the `session=` parameter.
3. The SDK automatically loads previous history before the run and saves new messages after.

### Basic Example

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant", instructions="Reply very concisely.")

# Create session — persists to SQLite file
session = SQLiteSession("conversation_123", "chat_history.db")

# First run
result = await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
print(result.final_output)  # "San Francisco"

# Second run — agent automatically remembers previous context
result = await Runner.run(agent, "What state is it in?", session=session)
print(result.final_output)  # "California"
```

### Full Conversation Loop Example

```python
import asyncio
from agents import Agent, Runner, SQLiteSession

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Remember context from previous messages.",
)

async def main():
    # Session persists across the entire conversation
    session = SQLiteSession("my_chat", "chat_history.db")

    print("Agent ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        result = await Runner.run(agent, user_input, session=session)
        print(f"Agent: {result.final_output}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

### SQLiteSession Parameters

```python
SQLiteSession(
    session_id,  # Unique string ID for this conversation
    db_path,     # Path to SQLite file (default: "agent_sessions.db")
)
```

- **session_id**: Unique per conversation. Same ID = same conversation history.
- **db_path**: Where to store the SQLite database file. Created automatically if it doesn't exist.

### Resuming a Previous Conversation

Because the session is stored in a file, you can resume it after restarting:

```python
# First run of the app
session = SQLiteSession("user_alice_chat", "chat_history.db")
result = await Runner.run(agent, "My name is Alice", session=session)
# App exits...

# Later — same session_id picks up where it left off
session = SQLiteSession("user_alice_chat", "chat_history.db")
result = await Runner.run(agent, "What's my name?", session=session)
# Agent: "Your name is Alice"
```

### Pros & Cons

**Pros:**
- Automatic — no manual history management
- Persists across restarts
- Simple API — just pass `session=`

**Cons:**
- SQLite file on disk (not suitable for distributed systems)
- Less control over what's stored
- Session grows over time (no built-in truncation)

---

## Which Approach to Use?

| Scenario | Use |
|----------|-----|
| Quick prototype, testing | `to_input_list()` |
| CLI agent that needs memory across restarts | `SQLiteSession` |
| Full control over history (filtering, summarizing) | `to_input_list()` |
| Multiple users / conversations | `SQLiteSession` with unique IDs per user |
| Async app (FastAPI, etc.) | `AsyncSQLiteSession` |
| **Production with PostgreSQL/Neon** | **`SQLAlchemySession`** |
| Distributed / multi-server | `RedisSession` |
| Sensitive data / compliance | `EncryptedSession` wrapping any backend |
| Branching conversations / token tracking | `AdvancedSQLiteSession` |
| Cloud-native (Kubernetes, etc.) | `DaprSession` |

---

## Approach 3: `SQLAlchemySession` — Production (PostgreSQL, Neon, MySQL)

The **production-ready** path for real databases. Works with any SQLAlchemy-compatible DB.

### Install

```bash
pip install "openai-agents[sqlalchemy]" asyncpg  # asyncpg for PostgreSQL/Neon
```

### Basic Usage

```python
from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession

agent = Agent(name="Assistant", instructions="You are a helpful assistant.", model=model)

# Method 1: From URL (simplest)
session = SQLAlchemySession.from_url(
    "user-session-123",
    url="postgresql+asyncpg://user:pass@localhost:5432/mydb",
    create_tables=True,  # Auto-creates agent_sessions + agent_messages tables
)

# Method 2: From existing engine (share connection pool)
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost:5432/mydb")
session = SQLAlchemySession(
    "user-session-123",
    engine=engine,
    create_tables=True,
)

# Run — history automatically stored and retrieved
result = await Runner.run(agent, "What is Neon DB?", session=session)
print(result.final_output)

# Second turn — context automatically included
result = await Runner.run(agent, "How does branching work?", session=session)
print(result.final_output)
```

### With Neon (Serverless PostgreSQL)

**Neon** is a serverless PostgreSQL platform — auto-scales to zero, database branching, built-in connection pooling, SSL required.

```python
from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession

# Neon connection string (from Neon dashboard → Connection Details)
NEON_URL = "postgresql+asyncpg://user:pass@ep-cool-rain-123.us-east-2.aws.neon.tech/neondb?ssl=true"

session = SQLAlchemySession.from_url(
    "user-alice",
    url=NEON_URL,
    create_tables=True,
)

agent = Agent(name="Assistant", instructions="Be helpful.", model=model)

# Works exactly the same as SQLite — but stored in Neon PostgreSQL
result = await Runner.run(agent, "Remember my name is Alice", session=session)
result = await Runner.run(agent, "What's my name?", session=session)
# Agent: "Your name is Alice"
```

**Neon connection tips:**
- Use the **direct (non-pooled)** connection string with `?ssl=true` for asyncpg
- For pooled connections, use `?sslmode=require` with psycopg2
- Free tier supports up to ~1K users — paid plans start at $10-25/mo

### With Custom Provider (Gemini/OpenRouter + Neon)

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents.extensions.memory import SQLAlchemySession
from agents.run import RunConfig

# Gemini provider
client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)

agent = Agent(name="Assistant", instructions="Be helpful.", model=model)

# Neon session
session = SQLAlchemySession.from_url(
    "user-alice",
    url="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb?ssl=true",
    create_tables=True,
)

result = await Runner.run(agent, "Hello!", run_config=run_config, session=session)
```

---

## Using Sessions with RunConfig

Both approaches work alongside `RunConfig`:

### to_input_list() + RunConfig

```python
run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)

input_list = []
input_list.append({"role": "user", "content": user_input})

result = await Runner.run(agent, input_list, run_config=run_config)
input_list = result.to_input_list()
```

### SQLiteSession + RunConfig

```python
run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)
session = SQLiteSession("my_chat", "chat_history.db")

result = await Runner.run(agent, user_input, run_config=run_config, session=session)
```

---

## Using Sessions with Custom Providers (Gemini, OpenRouter)

Sessions work identically regardless of provider. The session stores conversation messages, not provider config:

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, SQLiteSession
from agents.run import RunConfig

# Gemini provider
client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)

agent = Agent(name="Assistant", instructions="Be helpful.", model=model)

# Session works the same as with OpenAI
session = SQLiteSession("my_chat", "chat_history.db")

result = await Runner.run(agent, "Hello!", run_config=run_config, session=session)
```

---

## Common Patterns

### Pattern 1: User-Per-Session (Multi-User)

```python
from agents import SQLiteSession

def get_session(user_id: str) -> SQLiteSession:
    return SQLiteSession(f"user_{user_id}", "chat_history.db")

# Each user gets their own conversation history
session = get_session("alice")
result = await Runner.run(agent, user_input, session=session)
```

### Pattern 2: New Conversation Each Run

```python
import uuid
from agents import SQLiteSession

# Unique session per app launch — no carryover from previous runs
session = SQLiteSession(str(uuid.uuid4()), "chat_history.db")
```

### Pattern 3: Conversation Chains (Multi-Agent)

```python
# Both agents share the same session — agent2 sees agent1's conversation
session = SQLiteSession("chain_workflow", "chat_history.db")

result1 = await Runner.run(agent1, user_input, session=session)
result2 = await Runner.run(agent2, result1.final_output, session=session)
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| No session or history | Agent has no memory between runs | Use `to_input_list()` or `SQLiteSession` |
| Unbounded `to_input_list()` | Context window overflow after many turns | Truncate to last N messages |
| Hardcoded session_id for all users | All users share one conversation | Use unique ID per user/conversation |
| Storing sensitive data in session | SQLite file is unencrypted on disk | Don't put passwords/tokens in chat |
| Creating new session_id each run | Agent never remembers anything | Reuse same ID for same conversation |

---

## Session Integration with Other SDK Features

### Sessions + Guardrails

Guardrails process NEW input/output only — they don't see session history:

```python
from agents import Agent, Runner, SQLiteSession, guardrails

@guardrails.input_guardrail
def check_input(context, input_text):
    """Runs on NEW user input, not entire session history."""
    if len(input_text) > 500:
        raise guardrails.GuardrailTriggered("Input too long")
    return input_text

@guardrails.output_guardrail
def check_output(context, output):
    """Runs on NEW agent output, not entire session."""
    if "harmful" in output.lower():
        return "I can't respond to that."
    return output

session = SQLiteSession("user_alice", "chat.db")
agent = Agent(
    name="SafeAgent",
    instructions="Be helpful and safe.",
    input_guardrails=[check_input],
    output_guardrails=[check_output],
    model=model,
)

# Guardrails run on THIS turn only, not past turns
result = await Runner.run(agent, "What's my name?", session=session)
```

**Key point**: Guardrails validate the NEW turn's input/output, not the entire session. Session history is loaded automatically before guardrails run.

### Sessions + Handoffs

When handoffs occur, session history is shared:

```python
session = SQLiteSession("support_ticket_123", "chat.db")

# First agent (triage) adds to session
result1 = await Runner.run(triage_agent, "I need billing help", session=session)

# Second agent (billing) sees FULL session including triage conversation
result2 = await Runner.run(billing_agent, "Can you help?", session=session)
# billing_agent sees:
#   - Original "I need billing help" message
#   - Triage agent's response
#   - All tool calls from triage
#   - New message "Can you help?"
```

### Sessions + Streaming

Session history is available during streamed responses:

```python
session = SQLiteSession("stream_test", "chat.db")

# Stream with session — agent has access to full history
async for event in Runner.run_streamed(agent, "Summarize our conversation", session=session):
    if event.type == "text":
        print(event.text, end="", flush=True)  # Agent outputs while remembering history
```

### Sessions + RunConfig

Sessions and RunConfig don't conflict — use together:

```python
from agents.run import RunConfig

run_config = RunConfig(
    model=my_model,
    model_provider=my_client,
    tracing_disabled=True,
)

session = SQLiteSession("multi_turn", "chat.db")

# Both work together
result = await Runner.run(
    agent,
    "Hi",
    session=session,
    run_config=run_config,
)
```

**Priority**: Agent-level config < RunConfig-level config. RunConfig overrides agent's model if both are set.

### Sessions + Lifecycle Hooks

Hooks can observe session state changes:

```python
from agents import RunHooks, AgentHooks
import time

class SessionTracker(RunHooks):
    async def on_agent_start(self, context, agent):
        # Session history exists at this point
        print(f"[SESSION] Agent {agent.name} starting with {len(context.turn_input)} items in turn")

    async def on_agent_end(self, context, agent, output):
        # Final output will be saved to session after this hook
        print(f"[SESSION] Agent {agent.name} produced output — will be saved to session")

session = SQLiteSession("tracked", "chat.db")
result = await Runner.run(
    agent,
    "New message",
    session=session,
    hooks=SessionTracker(),
)
```

---

## SDK Runtime Session Methods

Instead of raw SQL, use the session object's methods directly:

```python
from agents import SQLiteSession

session = SQLiteSession("user_alice", "chat.db")

# Get all items (SDK method)
all_items = await session.get_items()
print(f"Total items: {len(all_items)}")

# Get last 10 items only
recent = await session.get_items(limit=10)

# Remove last item
last = await session.pop_item()
print(f"Popped: {last}")

# Clear entire session
await session.clear_session()
```

**Prefer SDK methods** for runtime operations. Use raw SQL only for analytics, export, or admin tasks.

### Clearing Session History

```python
from agents import SQLiteSession

# Option 1: SDK method (preferred)
session = SQLiteSession("old_session", "chat.db")
await session.clear_session()  # Removes all messages, keeps session record

# Option 2: New session_id (keep old history intact)
import uuid
session = SQLiteSession(str(uuid.uuid4()), "chat.db")
```

### Session Truncation (Prevent Unbounded Growth)

Keep only the most recent N messages:

```python
import sqlite3

def truncate_session(session_id: str, db_path: str, max_messages: int = 50):
    """Keep only the most recent N messages for a session."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM agent_messages WHERE session_id = ?",
        (session_id,)
    )
    count = cursor.fetchone()[0]

    if count > max_messages:
        to_delete = count - max_messages
        cursor.execute("""
            DELETE FROM agent_messages
            WHERE session_id = ?
            AND id IN (
                SELECT id FROM agent_messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
            )
        """, (session_id, session_id, to_delete))
        conn.commit()

    conn.close()

# Usage
truncate_session("user_alice", "chat.db", max_messages=100)
```

---

## Troubleshooting Sessions

### Issue: Session Not Persisting

```python
# Wrong: Creates new session each time
async def chat():
    result = await Runner.run(agent, user_input, session=SQLiteSession(str(uuid.uuid4()), "chat.db"))
    # Each run gets a new session_id — no history!

# Correct: Reuse same session_id
session = SQLiteSession("alice_chat", "chat.db")

async def chat():
    result = await Runner.run(agent, user_input, session=session)
    # Same session_id each call — history is maintained
```

### Issue: Context Overflow After Many Turns

**Symptom**: Agent slows down or fails with "context window exceeded"

**Solution**: Truncate or summarize:

```python
# After each run, keep only recent history
input_list = result.to_input_list()

if len(input_list) > 100:
    # Keep last 50 messages + first 10 (for context)
    input_list = input_list[:10] + input_list[-50:]

# Next run uses truncated history
result = await Runner.run(agent, new_input, input_list=input_list)
```

### Issue: Large `.db` File Size

**Symptom**: Database grows unbounded

**Solution**: Use the truncation function above or periodically clear old sessions via `session.clear_session()`.

---

## Best Practices

1. **Choose early**: Decide between `to_input_list()` and `SQLiteSession`/`SQLAlchemySession` at the start — switching later requires refactoring the conversation loop.
2. **Unique session IDs**: Use `user_id` or `uuid` to avoid conversations bleeding into each other.
3. **Add `.db` files to `.gitignore`**: Session databases contain conversation data — don't commit them.
4. **Test with multi-turn**: Always test that the agent remembers context from 2-3 turns back.
5. **Watch context size**: Long conversations can hit the model's context limit. Consider truncation or summarization for very long sessions.
6. **Session isolation**: In multi-tenant systems, use separate DB files or tenant-prefixed session IDs.
7. **Backup sessions**: Session data is valuable — consider backing up databases periodically.
8. **Monitor session growth**: Track DB size and implement cleanup for stale sessions.
9. **Encrypt sensitive data**: If storing user conversations, consider encrypted storage backends.
10. **Document session ID strategy**: Clearly document how you generate session IDs so future developers can maintain it correctly.
