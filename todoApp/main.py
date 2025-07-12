from fastapi import FastAPI

from models.base import Base
from database import engine
from routers import auth_router, todos_router, admin_router, user_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(todos_router.router)
app.include_router(admin_router.router)
app.include_router(user_router.router)
