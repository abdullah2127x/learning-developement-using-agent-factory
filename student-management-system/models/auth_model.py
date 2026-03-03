from tokenize import NUMBER
from typing import Optional

from pydantic import EmailStr
from sqlmodel import ARRAY, Column, Field, Integer, SQLModel, String

class Login(SQLModel):
    email: EmailStr = Field(sa_column=Column(String(100), nullable=False))
    password: str = Field(sa_column=Column(String(100), nullable=False))
