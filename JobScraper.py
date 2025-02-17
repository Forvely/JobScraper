import requests
import json
from tkinter import *
import customtkinter as ctk
import re
from slugify import slugify

# Create the GUI

root = ctk.CTk()
root.title("Job Searcher")
root.geometry("1400x800")


def create_table(frame, data):
    # Clear previous table
    for widget in frame.winfo_children():
        widget.destroy()

    frame.grid_columnconfigure(0, weight=1)  # Job Title column
    frame.grid_columnconfigure(1, weight=1)  # City column
    frame.grid_columnconfigure(2, weight=1)  # Payment column

    #  Create headers
    headers = ["Job Title", "City", "Payment"]
    for col, header in enumerate(headers):
        header_label = ctk.CTkLabel(frame, text=header, font=("Arial Bold", 14))
        header_label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
    # Create the rows for the data
    for row, job in enumerate(data, start=1):
        title_label = ctk.CTkLabel(frame, text=job["Job Title"], font=("Arial", 12))
        title_label.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")


        display_keys = ["City", "Payment"]
        for col, key in enumerate(display_keys, start=1):
            value = job.get(key, "N/A")
            label = ctk.CTkLabel(frame, text=value, font=("Arial", 12))
            label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

user_inputs = {"Region": "", "City": ""}
filters = [] # 0 = under 18 filter, 1 = summer job filter

def submit():
    user_inputs["Region"] = slugify(region_entry.get())
    user_inputs["City"] = slugify(city_entry.get())
    under18 = bool(check_var_under18.get())
    summer = bool(check_var_summer.get())
    filters.extend((under18,summer))
    fetch_jobs()
    create_table(job_frame, job_listings)

job_listings = []

# We need to get the ID of the city for it to work correctly we get this from a different api the site is using
def get_city_id(settlement_name, json_data):
    for settlement in json_data.get("settlement", []):
        slug_city = slugify(settlement.get("name", ""))
        if slug_city == settlement_name:
            return {
                "id": settlement.get("id"),
                "city": settlement.get("name")
            }
    return None

def fetch_jobs():
    job_listings.clear()
    # FurgeDiak
    fg_url = "https://www.furgediak.hu/furgediak-backings/methods/jobAdvertisementControl/findJobAdvertisementByParameter"
    
    # Getting the city ID
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

    print(user_inputs)
    settlement_return = None

    if settlement_response.status_code == 200 and user_inputs.get("City"):
        print("Success")
        settlement_data = settlement_response.json()
        settlement_return = get_city_id(user_inputs["City"], settlement_data)
    # -----------
    county_mapping = {"baranya": 1, "bekes": 2, "bacs-kiskun": 3, "borsod-abaauj-zemplen": 4, "budapest": 5, "csongrad": 6, "fejer": 7, "gyor-moson-sopron": 8, "hajdu-bihar": 9, "heves": 10, "jasz-nagykun-szolnok": 11, "komarom-esztergom": 12, "nograd": 13, "somogy": 14, "szabolcs-szatmar-bereg": 15, "tolna": 16, "vas": 17, "veszprem": 18, "zala": 19}
    mapped_county = county_mapping.get(user_inputs.get("Region"))
    
    job_payload = {
        "countyId": mapped_county,
        "jobAreaId": None,
        "keys": None,  
        "newJobAdvertisement": False,  
        "settlementId": settlement_return and settlement_return["id"],
        "staticJobAreaId": None,  
        "younger18": filters[0]
    }

    print(job_payload)

    fg_response = requests.post(fg_url, headers=headers, json=job_payload)

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
    else:
        print(f"Failed with status code {fg_response.status_code}")

    # PannonWork
    pw_url = "https://szovetkezet.pannonwork.hu/-/items/toborzas"

    available_location = False  
    under_18 = filters[0]
    summer_job = filters[1]

    pw_payload = {
        "statusz": {"_eq": "aktiv"},
        "kampanyok": {
            "kampany_tipus": {"_eq": "allasportal"},
            "statusz": {"_eq": "aktiv"}
        },
        "_and": [
            {},
            {},
            {},
            {"kampanyok": {"munka_tipusa": {"_in": ["diakmunka"]}}}
        ]
    }
    if user_inputs["Region"] or user_inputs["City"]:
        available_location = True

    county_slugmapping = {"baranya": "Baranya", "bekes": "Békés", "bacs-kiskun": "Bács-Kiskun", "borsod-abaauj-zemplen": "Borsod-Abaúj-Zemplén", "budapest": "Budapest", "csongrad": "Csongrád", "fejer": "Fejér", "gyor-moson-sopron": "Győr-Moson-Sopron", "hajdu-bihar": "Hajdú-Bihar", "heves": "Heves", "jasz-nagykun-szolnok": "Jász-Nagykun-Szolnok", "komarom-esztergom": "Komárom-Esztergom", "nograd": "Nógrád", "somogy": "Somogy", "szabolcs-szatmar-bereg": "Szabolcs-Szatmár-Bereg", "tolna": "Tolna", "vas": "Vas", "veszprem": "Veszprém", "zala": "Zala"}
    if available_location:
        if user_inputs["Region"] == "budapest" or user_inputs["City"] == "budapest":
            pw_payload["_and"].append({
                "lokacio": {"megye": {"_eq": "Budapest (főváros)"}}
            })
        elif user_inputs["City"]:
            pw_payload["_and"].append({
                "lokacio": {"telepules": {"_eq": settlement_return["city"]}}
            })
        elif user_inputs["Region"] and not user_inputs["City"]:
            pw_payload["_and"].append({
                "lokacio": {"megye": {"_eq": f"{county_slugmapping[user_inputs["Region"]]} (megye)"}}
            })
    filter_ids = []
    if under_18 and summer_job:
        filter_ids.extend(("1e62bd20-a494-4d24-a2fb-3f8754a58566", "bca3602c-7b71-47b9-a0e3-389262462a82"))
    elif under_18:
        filter_ids.append("bca3602c-7b71-47b9-a0e3-389262462a82")
    elif summer_job:
        filter_ids.append("1e62bd20-a494-4d24-a2fb-3f8754a58566")
        pw_payload["_and"].append({
            "cimkek": {"cimke_id": {"_in": filter_ids}}
        })

    pw_response = requests.get(pw_url, params={"filter": json.dumps(pw_payload)})

    if pw_response.status_code == 200:
        pw_data = pw_response.json()
        pw_jobs = pw_data.get("data", [])
        for job in pw_jobs:
            title = job.get("pozicio_neve", "N/A")
            city = job.get("telepules_szabad", "N/A")
            payment = job.get("berezes_megjeleno", "N/A")
            job_listings.append({
                "Job Title": title,
                "City": city,
                "Payment": payment,})
    else:
        print(f"Request failed with status code: {pw_response.status_code}")

    # MeloDiak
    md_url = "https://web-api.melodiak.hu/v1/job-advertisement"

    md_payload = {
        "page": 1,
        "sort": "-recent",
        "_": "1739657308023"
    }

    def add_filter(payload, region=None, city=None, label=None):
        if region:
            payload["filter[region]"] = region
        if city:
            payload["filter[city]"] = city
        if label:
            payload["filter[label]"] = label
        return payload

    region_filter = user_inputs.get("Region")
    city_filter = user_inputs.get("City")  # Set to None if no city filter is needed
    labels = []
    if filters[0]:
        labels.append("18-alatt-is-vegezheto-munkak")
    if filters[1]:
        labels.append("nyari-munkak")

    label_filter = "|".join(labels) if labels else None

    payload = add_filter(md_payload, region=region_filter, city=city_filter, label=label_filter)

    response = requests.get(md_url, params=payload)
        
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("data", {}).get("resource", [])

        for job in jobs:
            title = job.get("title", "N/A")
            city = job.get("city_name", "N/A")
            payment = job.get("payment", "N/A")
            job_listings.append({
                "Job Title": title,
                "City": city,
                "Payment": payment
            })
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# Finish GUI

region_label = ctk.CTkLabel(root, text="Region:")
region_label.pack(pady=(20, 5))
region_entry = ctk.CTkEntry(root, width=300)
region_entry.pack(pady=(5, 10))

city_label = ctk.CTkLabel(root, text="City:")
city_label.pack(pady=(10, 5))
city_entry = ctk.CTkEntry(root, width=300)
city_entry.pack(pady=(5, 20))

submit_button = ctk.CTkButton(root, text="Submit", command=submit)
submit_button.pack(pady=20)

check_var_under18 = ctk.StringVar(value="")
check_var_summer = ctk.StringVar(value="")

checkbox_frame = ctk.CTkFrame(root)
checkbox_frame.pack(pady=(10, 20))

checkbox_under18 = ctk.CTkCheckBox(checkbox_frame, text="Under 18", variable=check_var_under18, offvalue="", onvalue="True")
checkbox_under18.grid(row=0, column=1, padx=10)

checkbox_summer = ctk.CTkCheckBox(checkbox_frame, text="Summer job", variable=check_var_summer, offvalue="", onvalue="True")
checkbox_summer.grid(row=0, column=2, padx=10)

job_frame = ctk.CTkScrollableFrame(root, width=1300, height=400)
job_frame.pack(pady=40)

root.mainloop()