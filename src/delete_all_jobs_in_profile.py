import os
import json
import requests
from helpers import (
    get_base_api_url_of_work_efforts_for_month,
    get_month_guid,
    get_user_config,
)

# Constants
UPLOADED_FOLDER = "./uploaded_jsons"
ALL_UPLOADS_FILE = "./all_uploads.json"
SEARCH_URL_TEMPLATE = "https://www.job-room.ch/onlineform-service/api/npa/_search/by-owner-user-id?userId={}&page={}&_ng=ZnI="

# Load the user configuration
user_config = get_user_config()
bearer_token = user_config["bearer_token"]

# Headers for the request
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# Function to fetch all jobs from the profile
def fetch_all_jobs(user_id):
    page = 0
    jobs = []

    while True:
        search_url = SEARCH_URL_TEMPLATE.format(user_id, page)
        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for item in data["content"]:
                jobs.extend(item["workEfforts"])  # Add jobs from the current page
            if data["last"]:  # Check if this is the last page
                break
            page += 1
        else:
            print(
                f"Failed to fetch jobs on page {page}. Status Code: {response.status_code}"
            )
            break

    return jobs


# Function to delete a job by job ID and applyDate
def delete_job(job_id, apply_date):

    # Construct the DELETE URL with the correct GUID
    delete_url = (
        f"{get_base_api_url_of_work_efforts_for_month(apply_date)}/{job_id}?_ng=ZnI="
    )
    response = requests.delete(delete_url, headers=headers, timeout=30)
    return response.status_code == 204


# Clear all job records and files
def clear_all_jobs():
    # Fetch all jobs for the user
    user_id = user_config["user_id"]
    all_jobs = fetch_all_jobs(user_id)

    # Delete each job on the platform and local storage
    for job in all_jobs:
        job_id = job.get("id")
        apply_date = job.get("applyDate")
        if job_id and delete_job(job_id, apply_date):
            print(f"Deleted job {job_id} successfully.")
        else:
            print(f"Failed to delete job {job_id}.")

    # Clear the `uploaded_jsons` folder
    for filename in os.listdir(UPLOADED_FOLDER):
        file_path = os.path.join(UPLOADED_FOLDER, filename)
        os.remove(file_path)
        print(f"Removed local file: {filename}")

    # Clear the `all_uploads.json` file
    with open(ALL_UPLOADS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    print("Cleared all_uploads.json.")


# Execute the clearing process
clear_all_jobs()
