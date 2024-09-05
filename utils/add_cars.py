import requests
import random

# Function to generate random owner names
def generate_owner_name():
    first_names = ['John', 'Emma', 'Michael', 'Sophia', 'James', 'Olivia', 'William', 'Ava', 'Benjamin', 'Isabella']
    last_names = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate random car models
def generate_car_model():
    car_models = ['Toyota Camry', 'Honda Civic', 'Ford F-150', 'Chevrolet Silverado', 'Tesla Model 3', 'BMW 3 Series', 'Mercedes-Benz C-Class', 'Audi A4', 'Subaru Outback', 'Jeep Wrangler']
    return random.choice(car_models)

# Function to generate random car colors
def generate_car_color():
    car_colors = ['Red', 'Blue', 'Black', 'White', 'Silver', 'Gray', 'Green', 'Yellow', 'Orange', 'Purple']
    return random.choice(car_colors)



# Generate access token
def get_access_token(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{API_URL}/token", data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Could not authenticate")
    return response.json()["access_token"]

def addPlates(numbers:list, TOKEN:str):
    # Updated script
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    for number_plate in numbers:
        payload = {'plate_number': number_plate, 'owner_name': generate_owner_name(), 'car_model': generate_car_model(), 'car_color': generate_car_color()}
        response = requests.post(f"{API_URL}/admin/add_car/", json=payload, headers=headers)

if __name__ == '__main__':


    # API URL and credentials
    API_URL = 'http://localhost:8000'
    USERNAME = f"administrator"
    PASSWORD = f"adminPassword"

    TOKEN = get_access_token(USERNAME, PASSWORD)

    addPlates([
        "AD916",
        "DU327",
        "AD467",
        "DU932",
        "AD886",
        "DU054",
        "AD548",
        "DU873"
        ],
        TOKEN)