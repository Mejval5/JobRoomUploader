import os
import pandas as pd
import json
import re

from helpers import DEFAULT_REJECTION_REASON, generate_job_hash

# Define constants
EXCLUDE_STATUSES = ["Opportunities & Job Sites"]
OUTPUT_FOLDER = "./prepared_jsons"

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Load the TSV file
df = pd.read_csv("JobSearch - All.tsv", sep="\t")


# Helper function to determine if WebOrEmail is a URL or email
def is_email(value):
    return re.match(r"[^@]+@[^@]+\.[^@]+", value) is not None


# Helper function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*\s]+', "_", name)


# Iterate through each row and create JSON files
for _, row in df.iterrows():
    if row["Status"] in EXCLUDE_STATUSES:
        continue

    # Initialize applyStatus based on Status
    apply_status = []
    if row["Status"] == "Dead Ends":
        apply_status.append("REJECTED")
    elif row["Status"] == "Offers":
        apply_status.append("EMPLOYED")
    else:
        apply_status.append("PENDING")

    # Add "INTERVIEW" if Extra contains "Interview"
    if pd.notna(row["Extra"]) and "Interview" in row["Extra"]:
        apply_status.append("INTERVIEW")

    # Prepare the JSON data
    json_data = {
        "id": None,
        "applyDate": pd.to_datetime(row["ApplyDate"]).strftime("%Y-%m-%d"),
        "ravAssigned": False,
        "applyChannel": {
            "contactPerson": "",
            "email": row["WebOrEmail"] if is_email(row["WebOrEmail"]) else "",
            "formUrl": row["WebOrEmail"] if not is_email(row["WebOrEmail"]) else "",
            "phone": "",
            "types": ["ELECTRONIC"],
            "address": {
                "name": row["Company"],
                "street": "",
                "houseNumber": "",
                "country": "",
                "poBox": "",
            },
        },
        "applyStatus": apply_status,
        "occupation": row["Title"],
        "fullTimeJob": True,
        "rejectionReason": (
            DEFAULT_REJECTION_REASON if "REJECTED" in apply_status else ""
        ),
        "jobAdvertisementId": None,
    }

    # Define the sanitized filename
    title_sanitized = sanitize_filename(row["Title"])
    company_sanitized = sanitize_filename(row["Company"])
    job_hash = generate_job_hash(json_data)
    filename = f"{OUTPUT_FOLDER}/{title_sanitized}_{company_sanitized}_{job_hash}.json"

    # Save JSON data to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

print(f"JSON files have been created in the '{OUTPUT_FOLDER}' directory.")
