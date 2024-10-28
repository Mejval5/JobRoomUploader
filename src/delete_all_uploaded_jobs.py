import os
import json
import requests

from helpers import generate_job_hash, get_user_config

# Constants
UPLOADED_FOLDER = "./uploaded_jsons"
ALL_UPLOADS_FILE = "./all_uploads.json"

# Load the user configuration
user_config = get_user_config()
delete_url_template = f"https://www.job-room.ch/onlineform-service/api/npa/{user_config["url_special_id"]}/work-efforts/{{}}?_ng=ZnI="
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

# Iterate over each JSON file in the uploaded_jsons folder
for filename in os.listdir(UPLOADED_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(UPLOADED_FOLDER, filename)

        # Load JSON data to extract the job ID and calculate its hash
        with open(file_path, "r", encoding="utf-8") as file:
            job_data = json.load(file)
            job_id = job_data.get("id")
            job_hash = generate_job_hash(job_data)

            if not job_id:
                print(f"No job ID found for {filename}; skipping deletion.")
                continue

        # Construct the DELETE URL
        delete_url = delete_url_template.format(job_id)

        # Perform the DELETE request
        response = requests.delete(delete_url, headers=headers)

        # Check if the deletion was successful
        if response.status_code == 204:
            print(f"Deleted job {job_id} for {filename} successfully.")

            # Remove the local JSON file after successful deletion
            os.remove(file_path)
            print(f"Removed local file: {filename}")

            # Remove the hash from all_uploads.json
            if job_hash in existing_hashes:
                existing_hashes.remove(job_hash)
                print(f"Removed hash for {filename} from all_uploads.json")

            # Update all_uploads.json with the modified hash list
            with open(ALL_UPLOADS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(existing_hashes), f, ensure_ascii=False, indent=4)

        else:
            print(
                f"Failed to delete job {job_id} for {filename}. Status Code: {response.status_code}, Response: {response.text}"
            )
