from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import Base

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    employee_gmail = Column(String, unique=True)
    employee_code = Column(Integer, unique=True)
    password = Column(String)
    role = Column(String, default="employee")

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True)
    item_name = Column(String)
    item_type = Column(String)
    item_quantity = Column(Integer)
    item_location = Column(String)

