from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated

from sqlalchemy.orm import Session
from starlette import status

from database import localsession
from models.users_model import Users
from models.todos_model import Todos
from .auth_router import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["/admin"]
)

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return  db.query(Todos).all()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(Todos).filter(Todos.id == id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()

@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(user: user_dependency, db: db_dependency, id: int):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Nope")
    user_to_delete = db.query(Users).filter(Users.id == id).first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_to_delete)
    db.commit()