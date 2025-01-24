import requests

# URL of the API endpoint
url = "https://www.furgediak.hu/furgediak-backings/methods/jobAdvertisementControl/findJobAdvertisementByParameter"

# Headers (adjust as needed)
headers = {
    "Referer": "https://www.furgediak.hu/diakmunka"  # Include the originating page for context
}

# Data payload
data = {
    "countyId": 1,  # County ID
    "jobAreaId": [1, 2],  # Job area IDs as a list
    "keys": None,  # Null in JSON is represented as None in Python
    "newJobAdvertisement": False,  # Boolean value
    "settlementId": 2488,  # Settlement ID
    "staticJobAreaId": None,  # Null value
    "younger18": False  # Boolean value
}

# Send the POST request
response = requests.post(url, headers=headers, json=data)

# Print the response
if response.status_code == 200:
    print("Success!")
    print(response.json())  # Assuming the server responds with JSON
else:
    print(f"Failed with status code {response.status_code}")
    print(response.text)  # Print error messages for debugging
