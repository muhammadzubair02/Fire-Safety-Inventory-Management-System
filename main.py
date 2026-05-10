from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
from models import Employee
from database import SessionLocal
from models import Item
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "IMS@263262"
hashed_password = pwd_context.hash(password[:72])  # truncate if needed
print(hashed_password)


from dotenv import load_dotenv
import os
load_dotenv()
if not os.getenv("MAIL_USERNAME"):
    raise ValueError("MAIL_USERNAME not found in .env")

if not os.getenv("MAIL_PASSWORD"):
    raise ValueError("MAIL_PASSWORD not found in .env")

if not os.getenv("ADMIN_EMAIL"):
    raise ValueError("ADMIN_EMAIL not found in .env")
print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_FROM:", os.getenv("MAIL_FROM"))
print("ADMIN_EMAIL:", os.getenv("ADMIN_EMAIL"))

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()





app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmployeeSignupDetails(BaseModel):
    employee_name : str
    employee_gmail : str
    employee_code : int
    password : str

class EmployeeLoginDetail(BaseModel):
    employee_gmail : str
    password : str

class Items(BaseModel):
    item_id : int
    item_code : str
    item_name : str
    item_type : str
    item_quantity : int
    item_location : str

#Showing message to enter IMS succssfully
@app.get("/")
def home():
    return {"message": "Inventory Management System"}

def hash_password(password: str):
    return pwd_context.hash(password)

# Create Admin API (Run only once)
@app.post("/create-admin")
def create_admin():

    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(Employee).filter(
            Employee.employee_gmail == "plant02ehs@gmail.com"
        ).first()

        if existing_admin:
            return {"message": "Admin already exists"}

        # Create new admin
        admin = Employee(
            employee_name="Muhammad Zubair",
            employee_gmail="plant02ehs@gmail.com",
            employee_code=263262,
            password=hash_password("IMS@263262"),
            role="admin"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return {"message": "Admin created successfully"}

    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

    finally:
        db.close()

#Role checker Api
@app.post("/role_check")
def check_admin(role: str):
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

# Signup Api

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
# @app.post("/employee_info")
# def signup_info(employee: EmployeeSignupDetails):

#     db = SessionLocal()
#     existing_employee = db.query(Employee).filter(
#         (Employee.employee_code == employee.employee_code) |
#         (Employee.employee_gmail == employee.employee_gmail)
#     ).first()

#     if existing_employee:
#         return {"message": "Employee already registered"}
    
#     hashed_password = hash_password(employee.password)
#     try:
#         new_employee = Employee(
#             employee_name=employee.employee_name,
#             employee_gmail=employee.employee_gmail,
#             employee_code=employee.employee_code,
#             password=hashed_password,
#             role="employee"
#         )

#         db.add(new_employee)
#         db.commit()
#         db.refresh(new_employee)

#     except IntegrityError:
#         db.rollback()
#         return {"message": "Duplicate entry error"}

#     finally:
#         db.close()

#     return {"message": "Employee added successfully"}




from fastapi import Form

@app.post("/employee_info")
def signup_info(
    employee_name: str = Form(...),
    employee_gmail: str = Form(...),
    employee_code: int = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    existing_employee = db.query(Employee).filter(
        (Employee.employee_code == employee_code) |
        (Employee.employee_gmail == employee_gmail)
    ).first()

    if existing_employee:
        return {"message": "Employee already registered"}

    hashed_password = hash_password(password)

    new_employee = Employee(
        employee_name=employee_name,
        employee_gmail=employee_gmail,
        employee_code=employee_code,
        password=hashed_password,
        role="employee"
    )

    db.add(new_employee)
    db.commit()
    db.close()

    return {"message": "Employee added successfully"}





#Login Api
@app.post("/login")
def login_info(employee: EmployeeLoginDetail):

    db = SessionLocal()

    user = db.query(Employee).filter(
        Employee.employee_gmail == employee.employee_gmail
        ).first()
    
    if user and verify_password(employee.password, user.password):
        return {
        "message": "Employee login successfully",
        "role": user.role
    }
    db.close()
    return {"message": "You entered wrong email or password"}

#Add Item Api
@app.post("/items")
def item_add(item: Items, role: str = "employee"):
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can add items"
        )
    db = SessionLocal()
    existing_item = db.query(Item).filter(
        (Item.item_code == item.item_code) |
        (Item.item_name == item.item_name)
        ).first()
    if existing_item:
        return {"message": "This item is already exist"}
    try:
        new_item = Item(
            item_id=item.item_id,
            item_code=item.item_code,
            item_name=item.item_name,
            item_type=item.item_type,
            item_quantity=item.item_quantity,
            item_location=item.item_location
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    except IntegrityError:
        db.rollback()
        return {"message": "Duplicate entry error"}
  
    finally:
        db.close()
    
    return {"message": "Item added successfully"}
  

#Get all the Items Api
@app.get("/items")
def get_all_items():

    db = SessionLocal()
    items = db.query(Item).all()
    db.close()

    return items

#Get specific Item Api
@app.get("/items/name/{item_name}")
def find_item(item_name: str):

    db = SessionLocal()
    item = db.query(Item).filter(
        Item.item_name == item_name).first()

    db.close()

    if item:
        return item
    else:
        return {"message": "Item not found"}

class IssueItem(BaseModel):
    item_name : str
    item_code: str
    quantity: int

#APi for issue the item
LOW_STOCK_THRESHOLD = 10
@app.post("/items/issue")
async def issue_item(data: IssueItem):
    db = SessionLocal()
    item = db.query(Item).filter(Item.item_code == data.item_code).first()

    if not item:
        db.close()
        return {"message": "Item not found"}

    if item.item_quantity >= data.quantity:
        item.item_quantity -= data.quantity
        db.commit()

        if item.item_quantity <= LOW_STOCK_THRESHOLD:
            try:
                message = MessageSchema(
                    subject=f"Low Stock Alert: {item.item_name}",
                    recipients=[os.getenv("ADMIN_EMAIL")],
                    body=f"The stock of {item.item_name} (code: {item.item_code}) is low. Remaining quantity: {item.item_quantity}",
                    subtype="plain"
                )
                fm = FastMail(conf)
                await fm.send_message(message)
            except Exception as e:
                print(f"Email failed: {str(e)}")

        db.close()
        return {"message": "Item issued successfully"}

    db.close()
    return {"message": "Not enough stock"}

#APi for update the item
@app.put("/items/{item_code}")
def update_item(item_code: str, quantity: int):

    db = SessionLocal()
    item = db.query(Item).filter(Item.item_code == item_code).first()

    if item:
        item.item_quantity = quantity
        db.commit()
        db.close()
        return {"message": "Item updated successfully"}

    db.close()
    return {"message": "Item not found"}

#APi for update the item quantity
@app.patch("/items/{item_code}")
def update_item_quantity(item_code: str, quantity: int):

    db = SessionLocal()
    item = db.query(Item).filter(Item.item_code == item_code).first()

    if item:
        item.item_quantity = quantity
        db.commit()
        db.close()
        return {"message": "Item updated successfully"}

    db.close()
    return {"message": "Item not found"}

@app.get("/items/low-stock")
def low_stock():

    db = SessionLocal()
    low_items = db.query(Item).filter(
        Item.item_quantity <= LOW_STOCK_THRESHOLD
    ).all()
    db.close()

    return low_items


#------Delete Item---------
@app.delete("/delete_item/{item_id}")
def deleted_item(item_id: int, db:Session=Depends(get_db)):
    deleted_item= db.query(Item).filter(Item.item_id == item_id).first()
    if not deleted_item:
        raise HTTPException(status_code=404, detail= "Item not found.")
    db.delete(deleted_item)
    db.commit()
    return {"Message": "Item Deleted Successfully"}