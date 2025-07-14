from os import getenv
from fastapi import status

from .utils import *
from ..routers.admin_router import get_db, get_current_user
from ..models.todos_model import Todos
from ..models.users_model import Users

load_dotenv()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user(test_user):
    db = TestLocalSession()
    model = db.query(Users).filter(Users.id == 1).first()
    pw = model.hashed_password

    res = client.get("/user")

    assert res.status_code == status.HTTP_200_OK
    assert res.json()["username"] == "tvela"
    assert res.json()["email"] == "t@t.com"
    assert res.json()["firstname"] == "Travis"
    assert res.json()["lastname"] == "Vela"
    assert res.json()["role"] == "admin"
    assert res.json()["phone_number"] == "123123"
    assert brcypt_context.verify(getenv("PASSWORD"), res.json()["hashed_password"])

def test_change_password_success(test_user):
    res = client.put("/user/change-password", json={"password": getenv("PASSWORD"), "newpassword": "newnewnew"})

    assert res.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_user):
    res = client.put("/user/change-password", json={"password": "nope", "newpassword": "newnew"})

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json() == {"detail": "Unauthorized"}

def test_change_phonenumber_success(test_user):
    res = client.put("/user/change-phonenumber/222222")
    assert res.status_code == status.HTTP_204_NO_CONTENT


