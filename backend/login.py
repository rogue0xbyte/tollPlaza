import requests

# Endpoint URL
endpoint_url = "http://localhost:8000/token"

# User credentials
username = "administrator"
password = "adminPassword"

# Create form data with user credentials
form_data = {
    "username": username,
    "password": password
}

# Encode form data as query string
encoded_form_data = '&'.join([f"{key}={value}" for key, value in form_data.items()])

# Set headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Send a POST request to get the token
response = requests.post(endpoint_url, data=encoded_form_data, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Extract the token from the response
    token = response.json()["access_token"]
    print("Token:", token)
else:
    print("Failed to get token. Status code:", response.status_code)