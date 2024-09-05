from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from starlette.responses import FileResponse 
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import cv2
import base64
import requests
import asyncio
from datetime import datetime, timedelta
import time
import httpx
import paho.mqtt.client as mqtt

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()

# API URL and credentials
API_URL = 'http://localhost:8000'
SELF_NAME = 'DARB' # can only be DARB or SALIK (all-caps). Others will error out.
USERNAME = f"{SELF_NAME}"
PASSWORD = f"{SELF_NAME}-plaza"
MQTT_BROKER = "test.mosquitto.org"
MQTT_START_TOPIC = "toll-start"
MQTT_STOP_TOPIC = "toll-stop"



NUMBER_PLATE = ''
CAR_DETAILS = None
LAST_CAR_DETAILS_TIMESTAMP = 0
LAST_DETECT_TIMESTAMP = 1000
DET_NOW = False

FRAME_NO = 0

# Generate access token
def get_access_token(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{API_URL}/token", data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Could not authenticate")
    return response.json()["access_token"]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to control topics
    client.subscribe([(MQTT_START_TOPIC, 0), (MQTT_STOP_TOPIC, 0)])

def on_message(client, userdata, msg):
    print("Received message: "+str(msg.payload))
    # Check message type
    if "START" in str(msg.payload):
        print("Received acknowledgment for START")
    elif "STOP" in str(msg.payload):
        print("Received acknowledgment for STOP")

def publish_control(message, topic="toll-start"):
    client.publish(topic, message)
    print("Published control message: "+message)

try:
    # Create MQTT client instance
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    # Set callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    client.connect(MQTT_BROKER, 1883, 60)

    # Start the MQTT loop
    client.loop_start()

    time.sleep(2)  # Wait for some time
    publish_control("START", MQTT_START_TOPIC)
except Exception as e:
    print("MQTT Publishing Failed.", e)

TOKEN = get_access_token(USERNAME, PASSWORD)

async def reduce_balance(number_plate: str, reduce_amount: int = -5):
    global CAR_DETAILS
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
            response = await client.get(f"{API_URL}/admin/car_details/{number_plate}", headers=headers)
            # if response.status_code == 404:
            #     payload = {'plate_number': number_plate, 'owner_name': '', 'car_model':'', 'car_color': ''}
            #     response = await client.post(f"{API_URL}/admin/add_car/", json=payload, headers=headers)
    except:
        return None
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        response = await client.get(f"{API_URL}/admin/car_details/{number_plate}", headers=headers)
        CAR_DETAILS = response.json()
        payload = {'plate_number': number_plate, 'amount': reduce_amount}
        response = await client.post(f"{API_URL}/admin/transaction/{SELF_NAME}", json=payload, headers=headers)
        if response.status_code == 200:
            return {"message": "Balance reduced successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to reduce balance")

async def detect_number_plate(frame):
    global LAST_DETECT_TIMESTAMP, LAST_CAR_DETAILS_TIMESTAMP, CAR_DETAILS, NUMBER_PLATE
    
    # Get the current timestamp
    current_timestamp = time.time()
    
    # Check if the cooldown period has passed (2 seconds)
    print("TD:", current_timestamp - LAST_DETECT_TIMESTAMP)
    if current_timestamp - LAST_DETECT_TIMESTAMP < 2:
        return None
    
    # Update the last call timestamp
    LAST_DETECT_TIMESTAMP = current_timestamp
    
    _, encoded_image = cv2.imencode('.jpg', frame)
    encoded_string = base64.b64encode(encoded_image).decode()
    payload = {'image_data': encoded_string}
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/admin/anpr/", json=payload, headers=headers)
        print("RESPONSE",response.json())
        if response.status_code == 200:
            plate_number = response.json().get("license_plate_number")
            if plate_number:
                headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
                response = await client.get(f"{API_URL}/admin/car_details/{plate_number}", headers=headers)
                NUMBER_PLATE = plate_number
                CAR_DETAILS = response.json()
                LAST_CAR_DETAILS_TIMESTAMP = time.time()
                return plate_number
    return None

async def det_and_reduce(frame):
    global NUMBER_PLATE, DET_NOW, detected_cars
    DET_NOW = True
    print("deting and reducing")
    try:
        plate_number = await detect_number_plate(frame)
    except Exception as e:
        print("nothing det", e)
        DET_NOW = False
        return None
    if plate_number:
        print("deted", plate_number)
        NUMBER_PLATE = plate_number
        now = datetime.now()
        last_detection_time = detected_cars.get(plate_number)
        DET_NOW = False
        if last_detection_time is None or (now - last_detection_time) > timedelta(seconds=5):
            detected_cars[plate_number] = now
            try:
                await reduce_balance(plate_number)
                DET_NOW = False
            except:
                pass
    DET_NOW = False


# Frame Image
def process_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text.decode('utf-8')

# WebSocket endpoint for camera feed
@app.websocket("/ws/camera")
async def websocket_camera_feed(websocket: WebSocket):
    global FRAME_NO, DET_NOW, detected_cars
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    detected_cars = {}
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if (not DET_NOW) and (FRAME_NO % 10 == 0):
                print("running d&r")
                detection_task = asyncio.create_task(det_and_reduce(frame))
            FRAME_NO += 1
            await websocket.send_text(process_frame(frame))
    except WebSocketDisconnect:
        cap.release()

@app.get("/api/car/details")
async def get_car_details():
    global LAST_CAR_DETAILS_TIMESTAMP, CAR_DETAILS
    current_timestamp = time.time()
    if current_timestamp - LAST_CAR_DETAILS_TIMESTAMP >= 3:
        CAR_DETAILS = None
    return CAR_DETAILS

@app.get("/car-lookup")
async def car_lookup():
    return FileResponse('lookup.html')

@app.get("/api/stop-mqtt")
async def stop_mqtt():
    publish_control("STOP", MQTT_STOP_TOPIC)
    return True

@app.get("/api/start-mqtt")
async def start_mqtt():
    publish_control("START", MQTT_STOP_TOPIC)
    return True

if __name__ == "__main__":
    import uvicorn
    print("Initializing..")
    uvicorn.run(app, host="0.0.0.0", port=8081)