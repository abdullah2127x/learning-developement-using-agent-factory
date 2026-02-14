"""
FastAPI Hello World Example

This is the simplest FastAPI application. Great for learning and quick prototypes.

Run:
    fastapi dev hello-world.py

Or with uvicorn:
    uvicorn hello-world:app --reload

Visit:
    http://localhost:8000          - API endpoint
    http://localhost:8000/docs     - Interactive API documentation
    http://localhost:8000/redoc    - Alternative API documentation
"""

from fastapi import FastAPI

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI example",
    version="1.0.0"
)

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple greeting.
    """
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def hello_name(name: str):
    """
    Personalized greeting with path parameter.

    Args:
        name: The name to greet

    Returns:
        A personalized greeting message
    """
    return {"message": f"Hello {name}!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    """
    Example endpoint with path parameter and optional query parameter.

    Args:
        item_id: The ID of the item (automatically validated as integer)
        q: Optional query string parameter

    Returns:
        Item details with optional query parameter
    """
    result = {"item_id": item_id}
    if q:
        result["q"] = q
    return result

# To run this file:
# 1. Install FastAPI: pip install "fastapi[standard]"
# 2. Run: fastapi dev hello-world.py
# 3. Open browser: http://localhost:8000/docs
