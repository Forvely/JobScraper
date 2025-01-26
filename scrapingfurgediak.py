import requests
from slugify import slugify

# URL of the API endpoint
job_url = "https://www.furgediak.hu/furgediak-backings/methods/jobAdvertisementControl/findJobAdvertisementByParameter"
settlement_url = "https://www.furgediak.hu/furgediak-backings/methods/employeeUserControl/getComboData"

settlement_payload = {
    "comboNames": {
        "types": [
            "staticJobArea", "jobArea", "country", "county", "settlement","office", "typesOfRoad", "specialization", "language", "skill","countryCode", "serviceProviderNumber", "mekiSettlement","mekiCounty", "mekiOffice"
        ]
    }
}

# Headers (adjust as needed)
headers = {
    "Referer": "https://www.furgediak.hu/diakmunka"  # Include the originating page for context
}

settlement_response = requests.post(settlement_url, headers=headers, json=settlement_payload)

if settlement_response.status_code == 200:
    print("Success")
    settlement_data = settlement_response.json()
    
    def get_city_id(settlement_name, json_data):
        for settlement in json_data.get("settlement", []):  # Assuming "settlement" key contains the data
            if slugify(settlement.get("name", "")) == slugify(settlement_name):
                return settlement.get("id")  # Return the ID if the city name matches
        return None  # Return None if no match is found
   
    user_settlement = input("Enter the city name: ")
    settlement_id = get_city_id(user_settlement, settlement_data)

# Data payload
job_payload = {
    "countyId": None,  # County ID
    "jobAreaId": None,  # Job area IDs as a list
    "keys": None,  # Null in JSON is represented as None in Python
    "newJobAdvertisement": False,  # Boolean value
    "settlementId": settlement_id,  # Settlement ID
    "staticJobAreaId": None,  # Null value
    "younger18": False  # Boolean value
}

# Send the POST request
job_response = requests.post(job_url, headers=headers, json=job_payload)

job_listings = []

# Print the response
if job_response.status_code == 200:
    print("Success!")
    job_data = job_response.json()
    for job in job_data:
        title = job.get("positionName", "N/A")
        city = job.get("settlementName", "N/A")
        payment = job.get("grossSalaryPay", "N/A")
        job_listings.append({
            "Job Title": title,
            "City": city,
            "Payment": payment,})

    print(job_listings)  # Assuming the server responds with JSON
else:
    print(f"Failed with status code {job_response.status_code}")
    print(job_response.text)  # Print error messages for debugging
