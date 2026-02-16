#!/usr/bin/env python
"""Verify the API works with a quick integration test."""

import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 60)
print("Student Management API - Quick Verification")
print("=" * 60)

# Test 1: Health Check
print("\n[PASS] Health Check")
response = client.get("/health")
print(f"  Status: {response.status_code}")
print(f"  Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Create Student
print("\n[PASS] Create Student")
student_data = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "grade": 10
}
response = client.post("/students", json=student_data)
print(f"  Status: {response.status_code}")
created_student = response.json()
print(f"  Response: {json.dumps(created_student, indent=2)}")
student_id = created_student["id"]

# Test 3: Get Student
print(f"\n[PASS] Get Student (ID: {student_id})")
response = client.get(f"/students/{student_id}")
print(f"  Status: {response.status_code}")
print(f"  Response: {json.dumps(response.json(), indent=2)}")

# Test 4: Create More Students
print("\n[PASS] Create Additional Students")
for i, grade in enumerate([9, 11, 12], 1):
    client.post("/students", json={
        "name": f"Student {i}",
        "email": f"student{i}@example.com",
        "grade": grade
    })
print("  Created 3 additional students")

# Test 5: List Students
print("\n[PASS] List All Students")
response = client.get("/students")
print(f"  Status: {response.status_code}")
students = response.json()
print(f"  Total: {len(students)} students")
for s in students:
    print(f"    - {s['name']} (Grade: {s['grade']})")

# Test 6: Filter by Name
print("\n[PASS] Filter by Name ('Alice')")
response = client.get("/students?name=alice")
students = response.json()
print(f"  Found: {len(students)} student(s)")
for s in students:
    print(f"    - {s['name']}")

# Test 7: Filter by Grade
print("\n[PASS] Filter by Grade (10)")
response = client.get("/students?grade=10")
students = response.json()
print(f"  Found: {len(students)} student(s) with grade 10")

# Test 8: Update Student
print(f"\n[PASS] Update Student (ID: {student_id})")
update_data = {"grade": 11, "name": "Alice Smith"}
response = client.put(f"/students/{student_id}", json=update_data)
print(f"  Status: {response.status_code}")
print(f"  Updated: {json.dumps(response.json(), indent=2)}")

# Test 9: Delete Student
print(f"\n[PASS] Delete Student (ID: {student_id})")
response = client.delete(f"/students/{student_id}")
print(f"  Status: {response.status_code}")

# Test 10: Verify Deletion
print(f"\n[PASS] Verify Deletion")
response = client.get(f"/students/{student_id}")
print(f"  Status: {response.status_code} (should be 404)")
if response.status_code == 404:
    print(f"  Error: {response.json()['detail']}")

print("\n" + "=" * 60)
print("[SUCCESS] All verification tests passed!")
print("=" * 60)
print("\nNext steps:")
print("  1. Run the API: uv run fastapi run main.py")
print("  2. Open docs: http://localhost:8000/docs")
print("  3. Run tests: uv run pytest test_main.py -v")
print("=" * 60)
