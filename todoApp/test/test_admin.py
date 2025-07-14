from fastapi import status

from .utils import *
from ..routers.admin_router import get_db, get_current_user
from ..models.todos_model import Todos
from ..models.users_model import Users

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_get_all_todos(test_todo):
    response = client.get("/admin/todo")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title":"Learn to code",
        "description":"Need to learn everyday",
        "priority":5,
        "complete":False,
        "owner_id":1,
        "id": 1
    }]

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204
    db = TestLocalSession()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert not model

def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_admin_delete_user(test_user):
    response = client.delete("/admin/user/1")
    assert response.status_code == 204
    db = TestLocalSession()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model is None

def test_admin_delete_user_not_found(test_user):
    res = client.delete("/admin/user/999")
    assert res.status_code == 404
    assert res.json() == {"detail": "User not found"}
