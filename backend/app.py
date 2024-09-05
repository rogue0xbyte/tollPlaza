from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Request, Form
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import secrets
from modules.data_odin import DB
from typing import Optional
from modules.anpr.main import ANPR
import shutil
import base64
from io import BytesIO
from PIL import Image
import os
import datetime
import pytz
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DB()
dbc = db.init()

def add_log(line, car_id='', event_type='', toll_booth=''):
    gmt_timezone = pytz.timezone('GMT')
    timestamp = datetime.datetime.now().astimezone(gmt_timezone).strftime("%Y-%m-%d %H:%M:%S")
    with open("action.log", "a") as f:
        f.write(f"[{timestamp}] {line}\n")
    dbc.execute('''INSERT INTO car_logs (car_id, event_type, event_description, event_timestamp, toll_booth) 
                   VALUES (?, ?, ?, ?, ?)''', (car_id, event_type, line, timestamp, toll_booth))
    db.commit()

class Car(BaseModel):
    plate_number: str
    owner_name: Optional[str] = None
    car_model: Optional[str] = None
    car_color: Optional[str] = None

class Admin(BaseModel):
    username: str
    password: str

class Transaction(BaseModel):
    plate_number: str
    amount: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class ImageData(BaseModel):
    image_data: str

class RFIDDetection(BaseModel):
    plate_number: str
    identity: str
    name: str
    type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Functions for authentication
def verify_token(token: str = Depends(oauth2_scheme)):
    dbc.execute("SELECT username FROM admins WHERE token=?", (token,))
    user = dbc.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenData(username=user[0])

def get_current_user(token_data: TokenData = Depends(verify_token)):
    return token_data.username

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    dbc.execute("SELECT * FROM admins WHERE username=? AND password=?", (form_data.username, form_data.password))
    user = dbc.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = secrets.token_hex(32)
    dbc.execute("UPDATE admins SET token=? WHERE username=?", (token, form_data.username))
    db.commit()
    return {"access_token": token, "token_type": "bearer"}

@app.post("/admin/add_car/")
async def add_car(car: Car, current_user: str = Depends(get_current_user)):
    try:
        dbc.execute("INSERT INTO cars (plate_number, owner_name, car_model, car_color) VALUES (?, ?, ?, ?)",
                    (car.plate_number, car.owner_name, car.car_model, car.car_color))
        db.commit()
        add_log(f"[Action Success] Added Plate {car.plate_number}.", car_id = car.plate_number, event_type="Success")
        return {"message": "Car added successfully"}
    except Exception as e:
        add_log(f"[Action Failed] Attempted to add car {car.plate_number}.", car_id = car.plate_number, event_type="Failed")
        raise HTTPException(status_code=400, detail=f"Car already exists, {e}")

@app.get("/admin/car_details/{plate_number}")
async def get_car_details(plate_number: str, current_user: str = Depends(get_current_user)):
    if plate_number!="all":
        query = "SELECT * FROM cars WHERE plate_number='%s'" % plate_number
        print(query)
        dbc.execute(query)
        car_details = dbc.fetchone()
        print(car_details)
        add_log(f"[Action Request] Attempted to identify plate {plate_number}.", car_id = plate_number, event_type="Request")
        if car_details is None:
            add_log(f"[Action Failed] Plate {plate_number} not found.", car_id = plate_number, event_type="Failed")
            raise HTTPException(status_code=404, detail="Car not found")
        add_log(f"[Action Success] Found plate {plate_number}.", car_id = plate_number, event_type="Success")
        return {
            "plate_number": car_details[1],
            "owner_name": car_details[2],
            "car_model": car_details[3],
            "car_color": car_details[4],
            "balance": car_details[5],
            "stolen": car_details[6],
            "exempted": bool(car_details[7])
        }
    else:
        dbc.execute("SELECT * FROM cars")
        cars = dbc.fetchall()
        add_log(f"[Action Success] Accessed entire cars DB.", car_id = '', event_type="Success")
        lst = [{
            "plate_number": car_details[1],
            "owner_name": car_details[2],
            "car_model": car_details[3],
            "car_color": car_details[4],
            "balance": car_details[5],
            "stolen": car_details[6],
            "exempted": bool(car_details[7])
        } for car_details in cars]

        return {"data": lst}

@app.get("/admin/balance/{plate_number}")
async def get_balance(plate_number: str, current_user: str = Depends(get_current_user)):
    dbc.execute("SELECT balance FROM cars WHERE plate_number=?", (plate_number,))
    balance = dbc.fetchone()
    add_log(f"[Action Success] Retrieved balance of plate {plate_number}.", car_id=plate_number, event_type="Success")
    if balance is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"balance": balance[0]}

@app.post("/admin/transaction/{toll_booth}")
async def add_transaction(transaction: Transaction, toll_booth: str = "", current_user: str = Depends(get_current_user)):
    dbc.execute("SELECT exempted FROM cars WHERE plate_number=?", (transaction.plate_number,))
    exempted = dbc.fetchone()
    print(exempted[0], bool(exempted[0]))
    if not bool(exempted[0]):
        dbc.execute("UPDATE cars SET balance = balance + ? WHERE plate_number=?", (transaction.amount, transaction.plate_number))
        db.commit()
        add_log(f"[Action Success] Added transaction of {transaction.amount} to plate {transaction.plate_number}.", car_id=transaction.plate_number, event_type="Success", toll_booth=toll_booth)
        return {"message": "Transaction completed successfully"}
    add_log(f"[Action Failure] Attempted to add transaction of {transaction.amount} to plate {transaction.plate_number}. Vehicle is exempted.", car_id=transaction.plate_number, event_type="Failure", toll_booth=toll_booth)
    return {"message": "Transaction not completed. Vehicle is exempted."}

@app.put("/admin/stolen/{plate_number}")
async def flag_stolen(plate_number: str, stolen: bool = True, current_user: str = Depends(get_current_user)):
    dbc.execute("SELECT * FROM cars WHERE plate_number=?", (plate_number,))
    car_details = dbc.fetchone()
    if car_details is None:
        raise HTTPException(status_code=404, detail="Car not found")
    car_details = {
        "plate_number": car_details[1],
        "owner_name": car_details[2],
        "car_model": car_details[3],
        "car_color": car_details[4],
        "balance": car_details[5],
        "stolen": car_details[6],
        "exempted": car_details[7]
    }
    stolen = bool(not bool(car_details["stolen"]))
    stolen_string = "stolen"
    if not stolen:
        stolen_string = "not stolen"
    dbc.execute("UPDATE cars SET stolen = ? WHERE plate_number=?", (stolen, plate_number))
    db.commit()
    add_log(f"[Action Success] Marked plate {plate_number} {stolen_string}.", car_id=plate_number, event_type="Success")
    return {"message": "Stolen status updated"}

@app.put("/admin/exempted/{plate_number}")
async def flag_exempted(plate_number: str, exempted: bool = True, current_user: str = Depends(get_current_user)):
    dbc.execute("SELECT * FROM cars WHERE plate_number=?", (plate_number,))
    car_details = dbc.fetchone()
    if car_details is None:
        raise HTTPException(status_code=404, detail="Car not found")
    car_details = {
        "plate_number": car_details[1],
        "owner_name": car_details[2],
        "car_model": car_details[3],
        "car_color": car_details[4],
        "balance": car_details[5],
        "stolen": car_details[6],
        "exempted": car_details[7]
    }
    exempted = bool(not bool(car_details["exempted"]))
    exempted_string = "exempted"
    if not exempted:
        exempted_string = "not exempted"
    dbc.execute("UPDATE cars SET exempted = ? WHERE plate_number=?", (exempted, plate_number))
    db.commit()
    add_log(f"[Action Success] Marked plate {plate_number} {exempted_string}.", car_id=plate_number, event_type="Success")
    return {"message": "Exempted status updated"}

@app.put("/admin/update_car/{plate_number}")
async def update_car_details(plate_number: str, owner_name: Optional[str] = None, car_model: Optional[str] = None,
                             car_color: Optional[str]= None, current_user: str = Depends(get_current_user)):
    # Constructing the update query dynamically based on provided parameters
    update_query = "UPDATE cars"
    update_query += " SET "
    update_values = []

    if owner_name is not None:
        update_query += "owner_name=? "
        update_values.append(owner_name)

    if car_model is not None:
        if owner_name is not None:
            update_query += ", "
        update_query += "car_model=? "
        update_values.append(car_model)

    if car_color is not None:
        if (owner_name is not None) or (car_model is not None):
            update_query += ", "
        update_query += "car_color=? "
        update_values.append(car_color)

    # Adding the WHERE clause for the specific plate number
    update_query += " WHERE plate_number=?"

    # Adding the plate number to the update values list
    update_values.append(plate_number)

    # Executing the update query
    dbc.execute(update_query, update_values)
    db.commit()

    add_log(f"[Action Success] Updated car details for {plate_number}.", car_id=plate_number, event_type="Success")

    return {"message": "Car details updated successfully"}

@app.delete("/admin/delete_car/{plate_number}")
async def delete_car(plate_number: str, current_user: str = Depends(get_current_user)):
    dbc.execute("DELETE FROM cars WHERE plate_number=?", (plate_number,))
    db.commit()
    add_log(f"[Action Success] Deleted plate {plate_number}.", car_id=plate_number, event_type="Success")
    return {"message": "Car deleted successfully"}

@app.get("/admin/car_history/{plate_number}")
async def car_history(plate_number: str, current_user: str = Depends(get_current_user)):
    dbc.execute("SELECT * FROM car_logs WHERE car_id=?", (plate_number,))
    cars = dbc.fetchall()
    add_log(f"[Action Success] Accessed car history of {plate_number}.", car_id = plate_number, event_type="Success")
    lst = [{
        "car_id": car_details[1],
        "event_type": car_details[2],
        "event_description": car_details[3],
        "event_timestamp": car_details[4],
        "toll_booth": car_details[5]
    } for car_details in cars]

    return {"data": lst}

@app.delete("/admin/reset_db")
async def delete_car(current_user: str = Depends(get_current_user)):
    dbc.execute("DELETE FROM cars ")
    dbc.execute("DELETE FROM car_logs ")
    dbc.execute("DELETE FROM admins ")
    dbc.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  ("administrator", "adminPassword"))
    dbc.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  ("DARB", "DARB-plaza"))
    dbc.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  ("SALIK", "SALIK-plaza"))
    db.commit()
    add_log(f"[Action Success] Database Reset.", car_id=None, event_type="Success")
    return {"message": "Database Reset successfully."}

# CRUD operations for admin users
'''
@app.post("/admin/add_user/")
async def add_user(admin: Admin): #, current_user: str = Depends(get_current_user)):
    try:
        dbc.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  (admin.username, admin.password))
        db.commit()
        add_log(f"[Action Success] Added admin user {admin.username}.", car_id=None, event_type="Success")
        return {"message": "Admin user added successfully"}
    except sqlite3.IntegrityError:
        add_log(f"[Action Failed] Attempted to add admin user {admin.username}, username already exists.", car_id=None, event_type="Failed")
        raise HTTPException(status_code=400, detail="Admin user with this username already exists")
'''
@app.delete("/admin/delete_user/{username}")
async def delete_user(username: str, current_user: str = Depends(get_current_user)):
    dbc.execute("DELETE FROM admins WHERE username=?", (username,))
    db.commit()
    add_log(f"[Action Success] Deleted admin user {username}.", car_id=None, event_type="Success")
    return {"message": "Admin user deleted successfully"}

@app.post("/admin/anpr/")
async def process_anpr_image(image: ImageData, current_user: str = Depends(get_current_user)):
    try:
        base64_image = image.image_data
        image_data = base64.b64decode(base64_image)

        image = Image.open(BytesIO(image_data))
        image.save("uploaded_image.png")

        plate_number = ANPR("uploaded_image.png")

        if plate_number == 0:
            raise HTTPException(status_code=400, detail="No vehicles found")

        os.remove("uploaded_image.png")

        add_log(f"[Action Success] Performed ANPR for plate {plate_number}.", car_id=plate_number, event_type="Success")
        return {"license_plate_number": plate_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lookup")#, response_class=HTMLResponse)
async def lookup_car(plate_number: str = Form(...)):
    query = "SELECT * FROM cars WHERE plate_number='%s';" % plate_number
    dbc.executescript(query)
    car_details = dbc.fetchall()
    if car_details:
        car_details = {
            "plate_number": car_details[1],
            "owner_name": car_details[2],
            "car_model": car_details[3],
            "car_color": car_details[4],
            "balance": car_details[5],
            "stolen": car_details[6],
            "exempted": car_details[7]
        }
        return {"data": car_details}
    else:
        dbc.execute(query)
        car_details = dbc.fetchone()
        car_details = {
            "plate_number": car_details[1],
            "owner_name": car_details[2],
            "car_model": car_details[3],
            "car_color": car_details[4],
            "balance": car_details[5],
            "stolen": car_details[6],
            "exempted": car_details[7]
        }
        return {"data": car_details}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)