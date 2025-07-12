from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from ..models.todos_model import TodoRequest
from sqlalchemy.orm import Session
from starlette import status

from ..database import localsession
from ..models.todos_model import Todos
from .auth_router import get_current_user


router = APIRouter()

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    print(user)
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not todo:
        raise HTTPException(status_code=404, detail="No item found")
    return todo

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    this_todo = Todos(**todo.model_dump(), owner_id=user.get("id"))
    db.add(this_todo)
    db.commit()

@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo: TodoRequest, id: int = Path(gt=0) ):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    this_todo = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()

    if not this_todo:
        raise HTTPException(status_code=404, detail="Item not found")

    this_todo.title = todo.title
    this_todo.description = todo.description
    this_todo.priority = todo.priority
    this_todo.complete = todo.complete

    db.add(this_todo)
    db.commit()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    this_todo = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not this_todo:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(this_todo)
    db.commit()
