from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    email: EmailStr
