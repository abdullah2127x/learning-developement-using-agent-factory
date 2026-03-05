# OpenAI Agents SDK — Structured Output

Source: openai/openai-agents-python (Context7, benchmark 89.9, High reputation)

---

## Overview

Agents can return structured data (not just text) using Pydantic models. Enables:
- Type-safe responses
- Programmatic data extraction
- Validation of LLM output
- Integration with downstream systems

---

## Basic Structured Output

```python
from pydantic import BaseModel
from agents import Agent, Runner

class TodoItem(BaseModel):
    title: str
    description: str
    priority: int  # 1-5

agent = Agent(
    name="Todo Assistant",
    instructions="Create structured todo items.",
    output_type=TodoItem,  # Request structured output
    model="gpt-4o-mini",
)

result = await Runner.run(agent, "Create a high-priority bug fix task")

# final_output is now a TodoItem instance
todo: TodoItem = result.final_output
print(f"Task: {todo.title} (Priority: {todo.priority})")
```

---

## Complex Models

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    id: int
    title: str = Field(..., description="Task title")
    description: str
    priority: int = Field(ge=1, le=5)  # 1-5 range
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    completed: bool = False

class Project(BaseModel):
    name: str
    tasks: list[Task]  # Nested objects
    total_points: int
```

---

## Model Validation

Pydantic validates output automatically:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    age: int

    @field_validator("email")
    @classmethod
    def email_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v

    @field_validator("age")
    @classmethod
    def age_valid(cls, v):
        if v < 0 or v > 150:
            raise ValueError("Age must be 0-150")
        return v

# If LLM tries to return invalid data, Pydantic raises error
# Agent will retry with error feedback
```

---

## Union Types (Multiple Output Types)

```python
from typing import Union

class SuccessResponse(BaseModel):
    status: str = "success"
    data: dict

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str

# Agent can return either SuccessResponse or ErrorResponse
agent = Agent(
    name="Processor",
    instructions="Process data or explain error.",
    output_type=Union[SuccessResponse, ErrorResponse],
    model="gpt-4o-mini",
)
```

---

## Using Structured Output with Tools

Tools + structured output = powerful:

```python
from pydantic import BaseModel
from agents import Agent, Runner, function_tool

class SearchResult(BaseModel):
    query: str
    count: int
    results: list[str]

@function_tool
def search(query: str) -> str:
    """Search the knowledge base."""
    matches = ["result1", "result2", "result3"]
    return f"Found {len(matches)} results"

agent = Agent(
    name="Researcher",
    instructions="Search and return structured findings.",
    tools=[search],
    output_type=SearchResult,  # Final output is structured
    model="gpt-4o-mini",
)

result = await Runner.run(agent, "Find articles about machine learning")
findings: SearchResult = result.final_output
print(f"Query: {findings.query}, Results: {findings.results}")
```

---

## Streaming Structured Output

Stream structured output as it's generated:

```python
import json

# Stream with type checking
async for event in Runner.run_streamed(agent, user_input):
    if event.type == "text":
        # Intermediate text
        print(event.text, end="", flush=True)
    elif event.type == "structured_output":
        # Final structured output available
        data = event.output  # Pydantic instance
        print(f"\n✓ Got structured data: {data}")
```

---

## Common Models

### HTTP API Response

```python
class ApiResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: dict | None = None
```

### Content Classification

```python
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class TextAnalysis(BaseModel):
    text: str
    sentiment: Sentiment
    confidence: float  # 0-1
    keywords: list[str]
```

### Transaction Record

```python
from datetime import datetime
from decimal import Decimal

class Transaction(BaseModel):
    id: str
    amount: Decimal
    currency: str
    timestamp: datetime
    type: str  # "credit" or "debit"
    description: str
    status: str  # "pending" or "completed"
```

### Structured Extraction

```python
class DocumentExtraction(BaseModel):
    title: str
    author: str
    publication_date: str
    key_topics: list[str]
    summary: str
    word_count: int
```

---

## Best Practices

1. **Use Field descriptions**: Help LLM understand field purpose
   ```python
   class Item(BaseModel):
       name: str = Field(..., description="Item name")
       quantity: int = Field(ge=0, description="Quantity (non-negative)")
   ```

2. **Keep models focused**: One responsibility per model
   ```python
   # ❌ Too broad
   class Everything(BaseModel):
       user, product, order, payment...

   # ✅ Focused
   class Order(BaseModel):
       id, items, total
   ```

3. **Use enums for choices**: Constrains LLM output
   ```python
   class OrderStatus(str, Enum):
       PENDING = "pending"
       SHIPPED = "shipped"
       DELIVERED = "delivered"

   class Order(BaseModel):
       status: OrderStatus  # Only these 3 values allowed
   ```

4. **Validate with ranges**: For numeric constraints
   ```python
   class Rating(BaseModel):
       score: int = Field(ge=1, le=5)  # 1-5 only
   ```

5. **Provide examples**: In docstrings
   ```python
   class Task(BaseModel):
       """
       A todo item.

       Example:
           Task(title="Fix bug", priority=5, done=False)
       """
       title: str
       priority: int
       done: bool = False
   ```

---

## Error Handling with Structured Output

```python
from pydantic import ValidationError

try:
    result = await Runner.run(agent, user_input)
    data: MyModel = result.final_output
except ValidationError as e:
    # LLM output didn't match schema
    print(f"Output validation failed: {e}")
```

Agent will retry if validation fails (with feedback).

---

## Migration Path

Start simple (plain text), add structure as needed:

```
Stage 1: Plain string output
result = await Runner.run(agent, "Hello")  # str

Stage 2: Dict output
output_type=dict  # dict[str, Any]

Stage 3: Pydantic model
output_type=MyModel  # Validated structure
```
