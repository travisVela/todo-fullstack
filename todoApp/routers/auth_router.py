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

def get_db():
    db = localsession()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
brcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


'''
UTIL FUNCTIONS
'''
token = Token
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not brcypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_token(username: str, id: int, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username,  "id": id, 'exp':expires }
    return jwt.encode(encode, getenv("SECRET_KEY"), getenv("ALGORITHM"))

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        if not username or not id:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return {"username": username, "id": id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
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
async def login(ud: user_dependency, db: db_dependency):
   user = authenticate_user(ud.username, ud.password, db)
   if not user:
       raise HTTPException(status_code=401, detail="Could not validate credentials")

   token = create_token(user.username, user.id, timedelta(minutes=20))
   return {"token": token, "type": "bearer"}
