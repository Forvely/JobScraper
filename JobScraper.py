import requests
import json
from tkinter import *
import customtkinter as ctk
import re
from slugify import slugify

# FurgeDiak

fg_url = "https://www.furgediak.hu/furgediak-backings/methods/jobAdvertisementControl/findJobAdvertisementByParameter"
settlement_url = "https://www.furgediak.hu/furgediak-backings/methods/employeeUserControl/getComboData"

settlement_payload = {
    "comboNames": {
        "types": [
            "staticJobArea", "jobArea", "country", "county", "settlement","office", "typesOfRoad", "specialization", "language", "skill","countryCode", "serviceProviderNumber", "mekiSettlement","mekiCounty", "mekiOffice"
        ]
    }
}

headers = {
    "Referer": "https://www.furgediak.hu/diakmunka"
}

settlement_response = requests.post(settlement_url, headers=headers, json=settlement_payload)

if settlement_response.status_code == 200:
    print("Success")
    settlement_data = settlement_response.json()
    
    def get_city_id(settlement_name, json_data):
        for settlement in json_data.get("settlement", []):
            slug_city = slugify(settlement.get("name", ""))
            if slug_city == slugify(settlement_name):
                return {
                    "id": settlement.get("id"),
                    "city": settlement.get("name")
                }
        return None
    user_city = input("Enter the city name: ")
    settlement_return = get_city_id(user_city, settlement_data)

job_payload = {
    "countyId": None,
    "jobAreaId": None,
    "keys": None,  
    "newJobAdvertisement": False,  
    "settlementId": settlement_return["id"],  
    "staticJobAreaId": None,  
    "younger18": False
}

fg_response = requests.post(fg_url, headers=headers, json=job_payload)

job_listings = []

if fg_response.status_code == 200:
    print("Success!")
    job_data = fg_response.json()
    for job in job_data:
        title = job.get("positionName", "N/A")
        city = job.get("settlementName", "N/A")
        payment = job.get("grossSalaryPay", "N/A")
        job_listings.append({
            "Job Title": title,
            "City": city,
            "Payment": payment,})

    print(job_listings)
else:
    print(f"Failed with status code {fg_response.status_code}")

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

pw_response = requests.get(pw_url, params={"filter": json.dumps(pw_payload)})
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

print("-----------------------------------------------")
# MeloDiak
md_url = "https://web-api.melodiak.hu/v1/job-advertisement"

md_payload = {
    "page": 1,
    "sort": "-recent",
    "_": "1739657308023"
}

def add_filter(payload, city=None, label=None):
    if city:
        payload["filter[city]"] = city
    if label:
        payload["filter[label]"] = label
    return payload

city_filter = "budapest"  # Set to None if no city filter is needed
label_filter = "nyari-munkak|18-alatt-is-vegezheto-munkak"  # Set to None if no label filter is needed

payload = add_filter(md_payload, city=city_filter, label=label_filter)

response = requests.get(md_url, params=payload)

md_job_listings = []
    
if response.status_code == 200:
    data = response.json()
    job_listings = data.get("data", {}).get("resource", [])

    for job in job_listings:
        title = job.get("title", "N/A")
        city = job.get("city_name", "N/A")
        payment = job.get("payment", "N/A")
        md_job_listings.append({
            "Job Title": title,
            "City": city,
            "Payment": payment
        })
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

print(md_job_listings)

print("-----------------------------------------------")
# ProDiak

