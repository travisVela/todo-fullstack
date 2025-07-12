from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi import status
import pytest

from ..database import Base
from ..main import app
from ..routers.todos_router import get_db, get_current_user
from ..models.todos_model import Todos

load_dotenv()

engine = create_engine(
    getenv("SQLALCHEMY_DATABASE_URL"),
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestLocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
        db = TestLocalSession()
        try:
            yield db
        finally:
            db.close()

def override_get_current_user():
    return {'username': 'tvela', 'id': 1, 'user_role': 'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestLocalSession()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

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