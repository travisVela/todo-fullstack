from os import getenv

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from ..models.todos_model import Todos
from ..models.users_model import Users
from ..main import app
from ..models.base import Base
from ..routers.auth_router import brcypt_context

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

@pytest.fixture
def test_user():

    user = Users(
        username="tvela",
        email="t@t.com",
        firstname="Travis",
        lastname="Vela",
        hashed_password=brcypt_context.hash(getenv("PASSWORD")),
        role="admin",
        phone_number="123123"
    )
    db = TestLocalSession()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()