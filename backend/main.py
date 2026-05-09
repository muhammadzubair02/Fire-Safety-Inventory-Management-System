from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
from models import Employee
from database import SessionLocal
from dotenv import load_dotenv
import os
load_dotenv()


app = FastAPI()