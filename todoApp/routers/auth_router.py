from datetime import timedelta, datetime, timezone
from os import getenv
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import localsession
from models.token_model import Token
from models.users_model import Users, UserRequest
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

load_dotenv()
brcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]




'''
UTIL FUNCTIONS
'''

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not brcypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_token(username: str, id: int, role: str,  expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username,  "id": id, "role": role, "exp": expires}
    now = expires.strftime("%H,%I,%M")
    print(now)
    return jwt.encode(encode, getenv("SECRET_KEY"), getenv("ALGORITHM"))

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    print(token)
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if not username or not user_id:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials!!")
'''
API ENDPOINTS
'''

# @router.get("/")
# async def get_users(db: db_dependency):
#     return db.query(Users).all()
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, ur: UserRequest):
    user = Users(
        email = ur.email,
        username=ur.username,
        firstname=ur.firstname,
        lastname=ur.lastname,
        role=ur.role,
        hashed_password=brcypt_context.hash(ur.password),
        is_active=True
    )
    db.add(user)
    db.commit()

@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
   user = authenticate_user(form_data.username, form_data.password, db)
   if not user:
       raise HTTPException(status_code=401, detail="Could not validate credentials")

   token = create_token(user.username, user.id, user.role, timedelta(minutes=20))
   return {"access_token": token, "token_type": "bearer"}
