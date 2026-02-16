from sqlmodel import SQLModel, Field


# Models
class StudentBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    grade: int = Field(ge=0, le=12)

class Student(StudentBase, table=True):
    __tablename__ = "students"
    id: int | None = Field(default=None, primary_key=True)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    grade: int | None = Field(None, ge=0, le=12)

 




# from sqlmodel import SQLModel, Field


# # Models
# class StudentBase(SQLModel):
#     name: str = Field(index=True)
#     email: str = Field(index=True, unique=True)
#     grade: int = Field(ge=0, le=12)

# class Student(StudentBase, table=True):
#     __tablename__ = "students"
#     id: int | None = Field(default=None, primary_key=True)

# class StudentCreate(StudentBase):
#     pass

# class StudentUpdate(SQLModel):
#     name: str | None = None
#     email: str | None = None
#     grade: int | None = Field(None, ge=0, le=12)

 
