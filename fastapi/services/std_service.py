from fastapi import APIRouter

router = APIRouter(
    prefix="/students"
)

@router.get("/")
def get_students():
    return [{"id": 1, "name": "Ali"}]

@router.post("/")
def create_student(student: dict):
    return student
