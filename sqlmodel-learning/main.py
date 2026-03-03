from sqlmodel import Session, SQLModel, select

from src.database import engine
from src.models import User

# Create tables
SQLModel.metadata.create_all(engine)

# # Insert a user
# with Session(engine) as session:
#     new_user = User(name="Ali", email="ali@example.com", age=30)
#     session.add(new_user)
#     session.commit()

print("="*43)
# -------- FILTERING --------
with Session(engine) as session:
    statement = select(User).where(User.email == "ali@example.com")
    user = session.exec(statement).first()

    if user:
        session.delete(user)
        session.commit()
