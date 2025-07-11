from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from models import Todos
from database import localsession



router = APIRouter()

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency):
    return db.query(Todos).all()

@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, id: int = Path(gt=0)):

    todo = db.query(Todos).filter(Todos.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="No item found")
    return todo

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodoRequest):
    this_todo = Todos(**todo.model_dump())
    db.add(this_todo)
    db.commit()

@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo: TodoRequest, id: int = Path(gt=0) ):
    this_todo = db.query(Todos).filter(Todos.id == id).first()

    if not this_todo:
        raise HTTPException(status_code=404, detail="Item not found")

    this_todo.title = todo.title
    this_todo.description = todo.description
    this_todo.priority = todo.priority
    this_todo.complete = todo.complete

    db.add(this_todo)
    db.commit()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    this_todo = db.query(Todos).filter(Todos.id == id).first()
    if not this_todo:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(this_todo)
    db.commit()
