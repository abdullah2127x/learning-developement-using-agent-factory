from typing import Optional
from fastapi import FastAPI, Path, Query
from typing_extensions import Annotated

app = FastAPI()

@app.get("/items")
def read_items(limit: Annotated[Optional[int], Query(..., ge=1, le=100)] = None) -> dict: return {"limit": limit}

app.get("/items/{item_id}") 

def get_item(item_id: Annotated[int, Path(gt=0)]):return {"item_id": item_id}
# Annotated  In Python 
# use to set the metadata of the function parameters, first arg  type and second arg is metadata

# we can manage the optional at int no need to say in the Query(None)D
# here we have ser ... but still that is optional defined by Annotated

# If limit = 10
# 10 → the actual data
# “must be between 1 and 100” → metadata about that data