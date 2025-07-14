from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..database import localsession

from ..models.users_model import Users
from .auth_router import get_current_user


router = APIRouter(
    prefix="/user",
    tags=["/user"]
)

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()

brcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password: str
    newpassword: str = Field(min_length=6)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, uv: UserVerification):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    this_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not this_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not brcypt_context.verify(uv.password, this_user.hashed_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    this_user.hashed_password = brcypt_context.hash(uv.newpassword)

    db.add(this_user)
    db.commit()

@router.put("/change-phonenumber/{num}",status_code=status.HTTP_204_NO_CONTENT)
async def change_phonenumber(user: user_dependency, db: db_dependency, num: str):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    this_user = db.query(Users).filter(Users.id == user.get("id")).first()
    this_user.phone_number =num
    db.add(this_user)
    db.commit()