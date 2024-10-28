import os
import json
import requests

from helpers import generate_job_hash, get_user_config


# Constants
JSON_FOLDER = "./prepared_jsons"
UPLOADED_FOLDER = "./uploaded_jsons"
ALL_UPLOADS_FILE = "./all_uploads.json"

# Load the user configuration
user_config = get_user_config()
update_url = f"https://www.job-room.ch/onlineform-service/api/npa/{user_config["url_special_id"]}/work-efforts?userId={user_config["user_id"]}&_ng=ZnI="
bearer_token = user_config["bearer_token"]

# Headers for the request
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Load existing hashes from all_uploads.json
if os.path.exists(ALL_UPLOADS_FILE):
    with open(ALL_UPLOADS_FILE, "r", encoding="utf-8") as f:
        if os.stat(ALL_UPLOADS_FILE).st_size == 0:
            existing_hashes = set()
        else:
            existing_hashes = set(json.load(f))
else:
    existing_hashes = set()


# Iterate over each JSON file in the folder
for filename in os.listdir(JSON_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(JSON_FOLDER, filename)

        # Load JSON data from file
        with open(file_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        # Generate hash for the current payload
        job_hash = generate_job_hash(payload)

        # Process only if the job has been previously uploaded (hash exists)
        if job_hash not in existing_hashes:
            print(f"Skipping {filename}; not in existing uploaded jobs.")
            continue

        # Load the saved JSON from uploaded_jsons to get the workEffortId
        uploaded_file_path = os.path.join(UPLOADED_FOLDER, filename)
        with open(uploaded_file_path, "r", encoding="utf-8") as uploaded_file:
            uploaded_data = json.load(uploaded_file)
            work_effort_id = uploaded_data.get("id")

            if not work_effort_id:
                print(f"No workEffortId found for {filename}; skipping update.")
                continue

        # Determine new applyStatus and rejectionReason
        apply_status = payload["applyStatus"]
        rejection_reason = payload["rejectionReason"]

        # Check if an update is needed by comparing current with saved values
        if apply_status != uploaded_data.get(
            "applyStatus"
        ) or rejection_reason != uploaded_data.get("rejectionReason", ""):

            # Prepare the update payload
            update_payload = {
                "workEffortId": work_effort_id,
                "applyStatus": apply_status,
            }
            if "REJECTED" in apply_status:
                update_payload["rejectionReason"] = rejection_reason

            # Perform the update request
            response = requests.patch(
                update_url, headers=headers, json=update_payload, timeout=30
            )

            # Check if the update was successful
            if response.status_code == 200:
                print(f"Updated {filename} successfully.")

                # Update and overwrite the uploaded JSON with new applyStatus and rejectionReason
                uploaded_data["applyStatus"] = apply_status
                uploaded_data["rejectionReason"] = rejection_reason

                with open(uploaded_file_path, "w", encoding="utf-8") as saved_file:
                    json.dump(uploaded_data, saved_file, ensure_ascii=False, indent=4)
                print(f"Overwritten {UPLOADED_FOLDER}/{filename} with updated status.")

            else:
                print(
                    f"Failed to update {filename}. Status Code: {response.status_code}, Response: {response.text}"
                )

        else:
            print(f"Update skipped, no changes detected for {filename}.")
