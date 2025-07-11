from fastapi import APIRouter
from models.users_model import Users, UserRequest

router = APIRouter()

@router.post("/auth")
async def create_user(ur: UserRequest):
    user = Users(
        email = ur.email,
        username=ur.username,
        firstname=ur.firstname,
        lastname=ur.lastname,
        role=ur.role,
        hashed_password=ur.password,
        is_active=True
    )
    return user