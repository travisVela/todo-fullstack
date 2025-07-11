from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import localsession
from models.users_model import Users, UserRequest
from passlib.context import CryptContext

router = APIRouter()

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
brcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get("/auth")
async def get_users(db: db_dependency):
    return db.query(Users).all()
@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, ur: UserRequest):
    user = Users(
        email = ur.email,
        username=ur.username,
        firstname=ur.firstname,
        lastname=ur.lastname,
        role=ur.role,
        hashed_password=brcypt_context.hash(ur.password),
        is_active=True
    )
    db.add(user)
    db.commit()