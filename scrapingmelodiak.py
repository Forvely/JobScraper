import requests
from tkinter import *
import customtkinter as ctk
import re
from slugify import slugify

root = ctk.CTk()
root.title("Job Searcher")
root.geometry("1400x800")


user_inputs = {"Region": "", "City": ""}
checkbox_states = [False] * 4

def update_user_inputs():
    global user_inputs
    user_inputs["Region"] = region_entry.get()
    user_inputs["City"] = city_entry.get()

def update_checkbox_states():
    global checkbox_states
    checkbox_states = [var.get() for var in checkbox_vars]

def submit():
    update_user_inputs()
    update_checkbox_states()
    on_submit_actions()

# Mapping checkbox texts to corresponding URL query strings
checkbox_mapping = {"Under 18 Jobs": "18-alatt-is-vegezheto-munkak", "Weekend Jobs": "hetvegi-munkak", 
                    "Afternoon Jobs": "delutanos-munkak", "Night Jobs": "ejszakas-munkak"}
weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

def get_selected_job_types():
    """
    Get a list where each index corresponds to a checkbox's query string.
    Selected checkboxes return their mapped string; unselected return an empty string.
    Returns:
        list: List of query strings or empty strings for each checkbox.
    """
    return [
        checkbox_mapping[text] if var.get() else ""
        for text, var in zip(checkbox_texts, checkbox_vars)
    ]

labels = ["18-alatt-is-vegezheto-munkak", "hetvegi-munkak", "delutanos-munkak", "ejszakas-munkak"]
def_url = "https://web-api.melodiak.hu/v1/job-advertisement?filter%5Bregion%5D=rregion&filter%5Bcity%5D=ccity&filter%5Blabel%5D=llabel&filter%5Bpage=1&sort=-recent&_=1734547653732"

def create_table(frame, data):
    # Clear previous table content
    for widget in frame.winfo_children():
        widget.destroy()

    headers = ["Job Title", "City", "Payment", "Work Days"]
    for col, header in enumerate(headers):
        label = ctk.CTkLabel(frame, text=header, font=("Arial", 12, "bold"))
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    for row, job in enumerate(data, start=1):
        for col, (key, value) in enumerate(job.items()):
            label = ctk.CTkLabel(frame, text=value, font=("Arial", 12))
            label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

def on_submit_actions():
    update_user_inputs()
    update_checkbox_states()

    job_region_slug = slugify(user_inputs["Region"])
    job_city_slug = slugify(user_inputs["City"])

    job_types = get_selected_job_types()

    mod_def_url = def_url.replace("rregion", job_region_slug)
    mod_def_url = mod_def_url.replace("ccity", job_city_slug)

    job_type_query = "%7C".join(filter(None, job_types))

    if job_types == ["", "", "", ""]:
        mod_def_url = re.sub(r"filter%5Blabel%5D=[^&]*&", "", mod_def_url)
    else:
        mod_def_url = mod_def_url.replace("llabel", job_type_query)

    response = requests.get(mod_def_url)

    if response.status_code == 200:
        data = response.json()
        job_listings = data.get("data", {}).get("resource", [])

        formatted_job_listings = []
        for job in job_listings:
            title = job.get("title", "N/A")
            city = job.get("city_name", "N/A")
            payment = job.get("payment", "N/A")
            work_days = job.get("work_days", [])
            work_days = ", ".join([weekdays[i] for i in work_days])
            formatted_job_listings.append({
                "Job Title": title,
                "City": city,
                "Payment": payment,
                "Work Days": work_days
            })
        if not formatted_job_listings:
            for widget in root.winfo_children():
                widget.grid_forget()
                error_label.configure(text="No jobs found :/")
        else:
            error_label.configure(text="")
            create_table(scrollable_frame, formatted_job_listings)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    remind_checkbox_state = checkbox_variant.get()
    # Store URLs in a file
    if remind_checkbox_state == "True":
        with open('scraping_urls.txt', 'a+') as f:
            f.seek(0)
            lines = f.readlines()
            if mod_def_url in [line.strip() for line in lines]:
                error_label.configure(text="Entry already exists in the file.")
            else:
                f.write(f'{mod_def_url}\n')
                error_label.configure(text="")
    
region_label = ctk.CTkLabel(root, text="Region:")
region_label.pack(pady=(20, 5))
region_entry = ctk.CTkEntry(root, width=300)
region_entry.pack(pady=(5, 10))

city_label = ctk.CTkLabel(root, text="City:")
city_label.pack(pady=(10, 5))
city_entry = ctk.CTkEntry(root, width=300)
city_entry.pack(pady=(5, 20))

checkbox_frame = ctk.CTkFrame(root)
checkbox_frame.pack(pady=(10, 20))

checkbox_texts = ["Under 18 Jobs", "Weekend Jobs", "Afternoon Jobs", "Night Jobs"]
checkbox_vars = [ctk.BooleanVar() for _ in range(4)]

for i, text in enumerate(checkbox_texts):
    checkbox = ctk.CTkCheckBox(
        checkbox_frame,
        text=text,
        variable=checkbox_vars[i],
        onvalue=True,
        offvalue=False
    )
    checkbox.grid(row=0, column=i, padx=10)

checkbox_variant = ctk.StringVar(value='False')

remind_checkbox = ctk.CTkCheckBox(
    root,
    text="Do you want to be reminded?",
    variable=checkbox_variant,
    onvalue='True',
    offvalue='False',
)

remind_checkbox.pack(pady=20)

submit_button = ctk.CTkButton(root, text="Submit", command=submit)
submit_button.pack(pady=20)

error_label = ctk.CTkLabel(root, text="", text_color="red")
error_label.pack(pady=10)

scrollable_frame = ctk.CTkScrollableFrame(root, width=1350, height=400)
scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

root.mainloop()
