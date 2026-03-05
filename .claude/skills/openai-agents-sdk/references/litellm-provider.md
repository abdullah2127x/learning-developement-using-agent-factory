# OpenAI Agents SDK — LiteLLM Provider Integration

Source: learning-openai project analysis (2026-02-11)

---

## Overview

**LiteLLM** is a unified interface for calling any LLM provider (OpenAI, Anthropic, Google, Cohere, Azure, etc.) with a single standardized API. The OpenAI Agents SDK integrates with LiteLLM via `LitellmModel` wrapper, allowing you to:

- **Switch providers** without changing agent code
- **Support 100+ models** from 20+ providers
- **Standardize API calls** across heterogeneous environments
- **Use model aliases** for cost/performance optimization

| Use Case | Recommendation |
|----------|---|
| **Single provider, predictable costs** | Use Gemini or OpenRouter (Pattern 1/2) |
| **Multiple providers, flexibility needed** | Use LiteLLM (this pattern) |
| **Enterprise multi-cloud setup** | LiteLLM + RunConfig per-request override |
| **Fallback chains required** | LiteLLM with custom routing logic |

---

## Installation

```bash
# Install LiteLLM
pip install litellm

# Or with OpenAI Agents SDK (may already be included)
pip install openai[agents] litellm
```

---

## Basic Setup: Single Provider

### Step 1: Configure Environment

```bash
# For Gemini
GEMINI_API_KEY=your_gemini_api_key_here
LITELLM_MODEL=gemini/gemini-2.5-flash

# Or for OpenAI
OPENAI_API_KEY=sk-proj-...
LITELLM_MODEL=openai/gpt-4o-mini

# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-...
LITELLM_MODEL=anthropic/claude-3-5-sonnet
```

### Step 2: Create Agent

```python
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner, function_tool
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key (LiteLLM auto-detects from env based on model prefix)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini/gemini-2.5-flash"

# Create model wrapper
model = LitellmModel(
    model=MODEL,
    api_key=GEMINI_API_KEY,  # Optional if env var set
)

# Define tool (optional)
@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. You only respond in haikus.",
    model=model,
)
```

### Step 3: Run Agent

```python
# Synchronous execution (blocking)
result = Runner.run_sync(agent, "What's the weather in Tokyo?")
print(result.final_output)

# Async execution (recommended for production)
import asyncio

async def main():
    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)

asyncio.run(main())
```

---

## Supported Providers & Models

LiteLLM supports 20+ providers. Here are the most common:

### Google Gemini

```python
# Format: "gemini/model-id"
models = {
    "gemini/gemini-2.5-flash": "Latest, fastest, cheapest",
    "gemini/gemini-2.0-flash": "Stable, proven",
    "gemini/gemini-1.5-pro": "Most capable, slower",
}

model = LitellmModel(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)
```

### OpenAI

```python
# Format: "openai/model-id"
models = {
    "openai/gpt-4o": "Most capable",
    "openai/gpt-4o-mini": "Fast and cheap",
    "openai/gpt-4-turbo": "Older version",
}

model = LitellmModel(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

### Anthropic Claude

```python
# Format: "anthropic/model-id"
models = {
    "anthropic/claude-3-5-sonnet": "Best general purpose",
    "anthropic/claude-3-opus": "Most capable",
    "anthropic/claude-3-haiku": "Fastest, cheapest",
}

model = LitellmModel(
    model="anthropic/claude-3-5-sonnet",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
```

### Cohere

```python
# Format: "cohere/model-id"
models = {
    "cohere/command-r-plus": "Advanced reasoning",
    "cohere/command-r": "General purpose",
}

model = LitellmModel(
    model="cohere/command-r-plus",
    api_key=os.getenv("COHERE_API_KEY"),
)
```

### Azure OpenAI (Managed Service)

```python
# Format: "azure/deployment-name"
model = LitellmModel(
    model="azure/my-deployment",
    api_key=os.getenv("AZURE_API_KEY"),
)

# Requires: AZURE_API_VERSION, AZURE_API_BASE
```

### Local LLMs (via Ollama)

```python
# Format: "ollama/model-name"
model = LitellmModel(
    model="ollama/llama2",
    api_key="None",  # Local, no key needed
)
```

**For complete provider list:** https://docs.litellm.ai/docs/providers

---

## Advanced: Multi-Provider Configuration

### Setup Multiple Models

```python
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os
from dotenv import load_dotenv

load_dotenv()

# Define multiple provider configurations
providers = {
    "gemini": LitellmModel(
        model="gemini/gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    "openai": LitellmModel(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    "anthropic": LitellmModel(
        model="anthropic/claude-3-5-sonnet",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    ),
}

# Create base agent with default provider
agent = Agent(
    name="MultiProviderAssistant",
    instructions="You are a helpful assistant.",
    model=providers["gemini"],  # Default
)
```

### Switch Providers Per Request

```python
from agents.run import RunConfig

# Run with Gemini (default)
result1 = await Runner.run(agent, "Explain quantum computing")
print(f"Gemini: {result1.final_output}")

# Switch to OpenAI for second request
result2 = await Runner.run(
    agent,
    "Explain quantum computing",
    run_config=RunConfig(model=providers["openai"])
)
print(f"OpenAI: {result2.final_output}")

# Switch to Anthropic for third request
result3 = await Runner.run(
    agent,
    "Explain quantum computing",
    run_config=RunConfig(model=providers["anthropic"])
)
print(f"Anthropic: {result3.final_output}")
```

---

## Production Pattern: Cost Optimization

Use LiteLLM to automatically fallback to cheaper models:

```python
from agents.extensions.models.litellm_model import LitellmModel
from agents.run import RunConfig

# Define model tiers by cost
models_by_cost = {
    "cheap": LitellmModel(
        model="gemini/gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    "balanced": LitellmModel(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    "premium": LitellmModel(
        model="anthropic/claude-3-5-sonnet",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    ),
}

agent = Agent(
    name="CostOptimized",
    instructions="You are a helpful assistant.",
    model=models_by_cost["cheap"],  # Default to cheapest
)

async def run_with_fallback(prompt: str):
    """Try cheap model first, fallback to premium if needed."""
    for tier in ["cheap", "balanced", "premium"]:
        try:
            result = await Runner.run(
                agent,
                prompt,
                run_config=RunConfig(model=models_by_cost[tier])
            )
            print(f"✓ Success with {tier} model")
            return result
        except Exception as e:
            print(f"✗ {tier} failed: {e}")
            continue
    raise Exception("All models failed")
```

---

## Real-World Example: Weather Assistant

From `litellm_model.py`:

```python
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner, function_tool
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------- Model Configuration -------------------
MODEL = 'gemini/gemini-2.5-flash'  # Change to any supported model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ------------------- Tool Definition -------------------
@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city (demo function)."""
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."

# ------------------- Agent Setup -------------------
agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
    model=LitellmModel(model=MODEL, api_key=GEMINI_API_KEY),
)

# ------------------- Agent Execution -------------------
result = Runner.run_sync(agent, "What's the weather in Tokyo?")
print(result.final_output)
```

**Output example:**
```
Cherry blossoms bloom
Sunny skies over Tokyo
Spring brings warmth and light
```

---

## Logging & Debugging

### Enable LiteLLM Debug Logs

```python
import litellm

litellm.set_verbose = True  # Print all API calls

# Now run your agent
result = Runner.run_sync(agent, "Hello!")
```

**Output:**
```
Making async call to gemini with params...
Request url: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
Response received...
```

### Check Token Usage

```python
result = Runner.run_sync(agent, "Hello!")

# LiteLLM includes usage info in response metadata
if hasattr(result, 'usage'):
    print(f"Tokens used: {result.usage.total_tokens}")
```

---

## Best Practices

| Practice | Why | Example |
|----------|-----|---------|
| **Always load env vars first** | API keys available before agent creation | `load_dotenv()` before `LitellmModel()` |
| **Never hardcode API keys** | Security risk, harder to rotate | `api_key=os.getenv("KEY")` not `api_key="abc123"` |
| **Use model IDs correctly** | LiteLLM requires "provider/model" format | `"gemini/gemini-2.5-flash"` not `"gemini-2.5-flash"` |
| **Test with cheap model first** | Develop faster, spend less | `gemini-2.5-flash` or `gpt-4o-mini` |
| **Set timeout for reliability** | Network glitches happen | Can be set in `LitellmModel()` params |
| **Log provider changes in production** | Track which model handled each request | Store in database/logs when switching providers |
| **Use RunConfig for per-request override** | Flexible cost/quality tradeoffs | `RunConfig(model=...)` |
| **Cache responses when possible** | External API calls are slow | Use FastAPI caching decorators |

---

## Environment Setup Template

Create `.env` file in your project root:

```bash
# =============== GOOGLE GEMINI ===============
GEMINI_API_KEY=your_gemini_api_key_here

# =============== OPENAI ===============
OPENAI_API_KEY=sk-proj-your_openai_key_here

# =============== ANTHROPIC ===============
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# =============== COHERE ===============
COHERE_API_KEY=your_cohere_key_here

# =============== AZURE ===============
AZURE_API_KEY=your_azure_key_here
AZURE_API_BASE=https://your-instance.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview

# =============== LITELLM CONFIG ===============
LITELLM_MODEL=gemini/gemini-2.5-flash  # Default model to use
```

Load in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LITELLM_MODEL = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash")
```

---

## Common Issues & Solutions

### "Module not found: agents.extensions.models.litellm_model"

**Cause:** LiteLLM extension not available in your OpenAI SDK version.

**Solution:**
```bash
pip install --upgrade openai litellm
```

Or use direct import:
```python
from litellm import completion

# Use LiteLLM directly instead of wrapper
response = await completion(
    model="gemini/gemini-2.5-flash",
    messages=[{"role": "user", "content": "Hello"}],
    api_key=GEMINI_API_KEY,
)
```

### "Invalid API key for provider 'gemini'"

**Cause:** API key not found or incorrect.

**Checklist:**
- [ ] `.env` file exists in project root
- [ ] `load_dotenv()` called before creating agent
- [ ] API key is not wrapped in quotes in `.env`
- [ ] API key is valid at provider portal

```bash
# ✓ Correct
GEMINI_API_KEY=abc123xyz

# ✗ Wrong (extra quotes)
GEMINI_API_KEY="abc123xyz"
```

### "Model not found: gemini/gemini-2.5-flash"

**Cause:** Model name incorrect or deprecated.

**Solution:** Check available models at:
- Gemini: https://ai.google.dev/models
- OpenAI: https://platform.openai.com/docs/models
- Anthropic: https://docs.anthropic.com/en/docs/about-claude/models/latest
- LiteLLM provider docs: https://docs.litellm.ai/docs/providers

### "Timeout: Request to <provider> took too long"

**Cause:** Network latency or provider slowness.

**Solution:**
```python
# Increase timeout (in seconds)
model = LitellmModel(
    model="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY,
    # Additional timeout config if supported by LiteLLM
)

# Or add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def run_with_retry(agent, prompt):
    return await Runner.run(agent, prompt)
```

---

## Migration Guide: Switch from Other Patterns

### From Direct OpenAI to LiteLLM

**Before:**
```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
model = OpenAIChatCompletionsModel(model="gpt-4o-mini", openai_client=client)
agent = Agent(name="Assistant", model=model)
```

**After:**
```python
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner

model = LitellmModel(model="openai/gpt-4o-mini", api_key=OPENAI_API_KEY)
agent = Agent(name="Assistant", model=model)
```

### From Gemini to LiteLLM

**Before:**
```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url="...")
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
agent = Agent(name="Assistant", model=model)
```

**After:**
```python
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner

model = LitellmModel(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY)
agent = Agent(name="Assistant", model=model)
```

---

## Next Steps

1. **Create `.env` file** with your API keys
2. **Test with single provider** (start with Gemini)
3. **Add tools** to your agent with `@function_tool`
4. **Implement per-request switching** with `RunConfig`
5. **Add monitoring/logging** for production
6. **Consider fallback chains** for reliability

See also:
- [core-agents.md](./core-agents.md) for agent basics
- [custom-llm-providers.md](./custom-llm-providers.md) for pattern comparison
- [LiteLLM Official Docs](https://docs.litellm.ai/)
