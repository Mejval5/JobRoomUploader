import os
import json
import requests

from helpers import generate_job_hash, get_user_config

# Constants
JSON_FOLDER = "./prepared_jsons"
UPLOADED_FOLDER = "./uploaded_jsons"
ALL_UPLOADS_FILE = "./all_uploads.json"

# Create the output directory if it doesn't exist
if not os.path.exists(UPLOADED_FOLDER):
    os.makedirs(UPLOADED_FOLDER)

# Load the user configuration
user_config = get_user_config()
upload_url = f"https://www.job-room.ch/onlineform-service/api/npa/_action/add-work-effort?userId={user_config["user_id"]}&_ng=ZnI="
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


# Recursive function to strip whitespaces from all string values in the data
def trim_whitespace(data):
    if isinstance(data, dict):
        return {key: trim_whitespace(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [trim_whitespace(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    else:
        return data


# Iterate over each JSON file in the folder
for filename in os.listdir(JSON_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(JSON_FOLDER, filename)

        # Load JSON data from file and trim whitespaces
        with open(file_path, "r", encoding="utf-8") as file:
            payload = trim_whitespace(json.load(file))

        # Generate hash for the current payload
        job_hash = generate_job_hash(payload)

        # Skip if the hash already exists in all_uploads.json
        if job_hash in existing_hashes:
            print(f"Skipping {filename}; already uploaded.")
            continue

        # Perform the POST request
        response = requests.post(upload_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 201:
            print(f"Uploaded {filename} successfully.")

            # Find the matching work effort ID in the response (for confirmation)
            response_data = response.json()
            matched_work_effort = next(
                (
                    effort
                    for effort in response_data.get("workEfforts", [])
                    if generate_job_hash(effort) == job_hash
                ),
                None,
            )

            # Update payload with ID and save
            if matched_work_effort:
                payload["id"] = matched_work_effort["id"]
                saved_filename = os.path.join(UPLOADED_FOLDER, filename)

                # Save the modified JSON with ID
                with open(saved_filename, "w", encoding="utf-8") as saved_file:
                    json.dump(payload, saved_file, ensure_ascii=False, indent=4)
                print(
                    f"Saved {filename} with ID {payload['id']} to '{UPLOADED_FOLDER}'"
                )

                # Add the new hash to existing hashes and save to all_uploads.json
                existing_hashes.add(job_hash)
                with open(ALL_UPLOADS_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(existing_hashes), f, ensure_ascii=False, indent=4)

        else:
            print(
                f"Failed to upload {filename}. Status Code: {response.status_code}, Response: {response.text}"
            )
