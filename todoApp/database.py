from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# SQLITE CONNECTION WITH ARGS
# engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"), connect_args={'check_same_thread': False})

engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"))


localsession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

