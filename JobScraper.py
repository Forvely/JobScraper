import requests
import json
from tkinter import *
import customtkinter as ctk
import re
from slugify import slugify

# FurgeDiak

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
            slug_city = slugify(settlement.get("name", ""))
            if slug_city == slugify(settlement_name):
                return {
                    "id": settlement.get("id"),
                    "city": settlement.get("name")
                }  # Return the ID if the city name matches
        return None  # Return None if no match is found

    user_city = input("Enter the city name: ")
    settlement_return = get_city_id(user_city, settlement_data)

# Data payload
job_payload = {
    "countyId": None,  # County ID
    "jobAreaId": None,  # Job area IDs as a list
    "keys": None,  # Null in JSON is represented as None in Python
    "newJobAdvertisement": False,  # Boolean value
    "settlementId": settlement_return["id"],  # Settlement ID
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

print("-----------------------------------------------")
# PannonWork

pw_url = "https://szovetkezet.pannonwork.hu/-/items/toborzas"

apply_filters = True  
under_18 = True
summer_job = True


pw_payload = {
    "statusz": {"_eq": "aktiv"},
    "kampanyok": {
        "kampany_tipus": {"_eq": "allasportal"},
        "statusz": {"_eq": "aktiv"}
    },
    "_and": [
        {"lokacio": {"megye": {"_eq": "Budapest (főváros)"}}},
        {},
        {},
        {"kampanyok": {"munka_tipusa": {"_in": ["diakmunka"]}}}
    ]
}

if apply_filters:
    filter_ids = []
    if under_18 and summer_job:
        filter_ids.extend(("1e62bd20-a494-4d24-a2fb-3f8754a58566", "bca3602c-7b71-47b9-a0e3-389262462a82"))
    elif under_18:
        filter_ids.append("bca3602c-7b71-47b9-a0e3-389262462a82")
    else:
        filter_ids.append("1e62bd20-a494-4d24-a2fb-3f8754a58566")
    pw_payload["_and"].append({
        "cimkek": {"cimke_id": {"_in": filter_ids}}
    })

pw_headers = {
    "Content-Type": "application/json"
}

pw_response = requests.get(pw_url, headers=headers, params={"filter": json.dumps(pw_payload)})
pw_job_listings = []

if pw_response.status_code == 200:
    pw_data = pw_response.json()
    pw_jobs = pw_data.get("data", [])
    for job in pw_jobs:
        title = job.get("pozicio_neve", "N/A")
        city = job.get("telepules_szabad", "N/A")
        payment = job.get("berezes_megjeleno", "N/A")
        pw_job_listings.append({
            "Job Title": title,
            "City": city,
            "Payment": payment,})
    print(pw_job_listings)
else:
    print(f"Request failed with status code: {pw_response.status_code}")


# MeloDiak
'''
labels = ["18-alatt-is-vegezheto-munkak", "hetvegi-munkak", "delutanos-munkak", "ejszakas-munkak"]
def_url = "https://web-api.melodiak.hu/v1/job-advertisement?filter%5Bregion%5D=rregion&filter%5Bcity%5D=ccity&filter%5Blabel%5D=llabel&filter%5Bpage=1&sort=-recent&_=1734547653732"

def on_submit_actions(user_inputs, job_types):
    
    # Slugify the region and city from user_inputs
    job_region_slug = slugify(user_inputs["Region"])
    job_city_slug = slugify(user_inputs["City"])
    
    # Replace the placeholders in def_url with the slugified values
    mod_def_url = def_url.replace("rregion", job_region_slug)
    mod_def_url = mod_def_url.replace("ccity", job_city_slug)
    
    # Create the job type query string from selected job_types
    job_type_query = "%7C".join(filter(None, job_types))
    
    if job_types == ["", "", "", ""]:
        mod_def_url = re.sub(r"filter%5Blabel%5D=[^&]*&", "", mod_def_url)
    else:
        mod_def_url = mod_def_url.replace("llabel", job_type_query)
    print(mod_def_url)
    # Make the GET request to the API
    response = requests.get(mod_def_url)
    formatted_job_listings = []
    
    if response.status_code == 200:
        data = response.json()
        job_listings = data.get("data", {}).get("resource", [])
    
        for job in job_listings:
            title = job.get("title", "N/A")
            city = job.get("city_name", "N/A")
            payment = job.get("payment", "N/A")
            formatted_job_listings.append({
                "Job Title": title,
                "City": city,
                "Payment": payment
            })
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    
    return formatted_job_listings

# Sample user inputs 
user_inputs = {"Region": "", "City": "Budapest"}
# Simulate selected job types.
job_types = ["18-alatt-is-vegezheto-munkak", "hetvegi-munkak", "", ""]

results = on_submit_actions(user_inputs, job_types)
print(results)
'''
