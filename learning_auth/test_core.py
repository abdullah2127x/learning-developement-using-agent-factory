"""
Manual test script for learning_auth core modules.
Run: uv run python test_core.py
"""
from core.config import settings
from core.security import get_password_hash, verify_password
from core.jwt import create_access_token, verify_token
from core.database import create_db_and_tables, get_db, engine
from models.user import User, UserRead
from datetime import timedelta

print("=" * 50)
print("1. Password Hashing")
print("=" * 50)

plain = "mysecret123"
hashed = get_password_hash(plain)
print(f"Plain:    {plain}")
print(f"Hashed:   {hashed}")
print(f"Verify ✅: {verify_password(plain, hashed)}")
print(f"Verify ❌: {verify_password('wrongpass', hashed)}")
print()

# Different hashes for same password (salt)
h1 = get_password_hash(plain)
h2 = get_password_hash(plain)
print(f"Same password, different hashes: {h1 != h2}")
print()

print("=" * 50)
print("2. JWT Tokens")
print("=" * 50)

access = create_access_token(subject=42, expires_delta=timedelta(minutes=15))
print(f"Access token (first 50 chars): {access[:50]}...")

payload = verify_token(access)
print(f"Decoded payload: {payload}")
print(f"sub: {payload.get('sub')}")
print(f"type: {payload.get('type')}")
print()

try:
    verify_token("invalid.token.here")
except ValueError as e:
    print(f"Invalid token caught: {e}")
print()

print("=" * 50)
print("3. Database & User Model")
print("=" * 50)

create_db_and_tables()
print("Tables created ✅")

with next(get_db()) as db:
    print(f"DB engine: {engine.url}")

    # Create test user
    from sqlmodel import select
    existing = db.exec(select(User).where(User.email == "test@example.com")).first()
    if existing:
        print(f"User already exists: {existing.email}")
    else:
        user = User(email="test@example.com")
        user.set_password("password123")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: id={user.id}, email={user.email}")
        print(f"Has hashed_password: {bool(user.hashed_password)}")
        print(f"Password verify ✅: {user.verify_password('password123')}")
        print(f"Password verify ❌: {user.verify_password('wrong')}")

        # UserRead (excludes hashed_password)
        user_read = UserRead.model_validate(user)
        print(f"UserRead: {user_read.model_dump_json(indent=2)}")
print()

print("=" * 50)
print("4. Auth: get_current_user flow")
print("=" * 50)

with next(get_db()) as db:
    user = db.exec(select(User).where(User.email == "test@example.com")).first()
    if user:
        token = create_access_token(subject=user.id)
        print(f"Token created for user {user.id}")

        decoded = verify_token(token)
        uid = int(decoded["sub"])
        fetched = db.get(User, uid)
        print(f"Retrieved user: {fetched.email if fetched else 'None'}")
print()

print("All core tests passed ✅")
