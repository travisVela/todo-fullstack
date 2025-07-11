from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Boolean
from .base import Base
# from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(String)
    is_active = Column(Boolean, default=True)

class UserRequest(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    password: str
    role: str


