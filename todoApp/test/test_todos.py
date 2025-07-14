from fastapi import status

from ..routers.todos_router import get_db, get_current_user
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



def test_get_todos(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title":"Learn to code",
        "description":"Need to learn everyday",
        "priority":5,
        "complete":False,
        "owner_id":1,
        "id": 1
    }]

def test_get_todo(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Learn to code",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
        "owner_id": 1,
        "id": 1
    }

def test_get_todo_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo!",
        "description": "New todo description",
        "priority": 5,
        "complete": False
    }
    response = client.post("/todo/", json=request_data)
    assert response.status_code == 201
    db = TestLocalSession()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")

def test_update_todo(test_todo):
    request_data = {
        "title": "New Title",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
    }
    response = client.put("/todo/1", json=request_data)
    assert response.status_code == 204
    db = TestLocalSession()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get("title")

def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "New Title",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
    }
    response = client.put("/todo/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == 204
    db = TestLocalSession()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert not model

def test_delete_todo_not_found(test_todo):
    response = client.delete("/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}
