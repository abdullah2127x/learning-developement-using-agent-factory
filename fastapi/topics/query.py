from typing import Optional
from fastapi import FastAPI, Query

app = FastAPI()

# Query() -> undefined so it is requeired by default
# Query(...) -> explicity says required
# Query(None/"default value") -> set default value

@app.get("/items")
def read_items(limit: int = Query(..., ge=1, le=100)):  # ...=>required
    return {"limit": limit}


@app.get("/search")
def search(query: Optional[str] = Query(None)):  # Optional
    return {"query": query if query else "NO query provided"}
    

@app.exception_handler(NotFoundError)
def handle_not_found(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})