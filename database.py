from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

engine = create_engine(getenv("SQLITE_DB_URL"), connect_args={'check_same_thread': False})

localsession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

