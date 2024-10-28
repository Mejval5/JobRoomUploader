import hashlib
import json
from datetime import datetime

CONFIG_FILE = "user_config.json"
MONTHS_CONFIG_FILE = "months.json"

DEFAULT_REJECTION_REASON = (
    "Ils avaient de nombreux candidats et ont décidé de ne pas suivre avec mon profil."
)

cached_month_guids = {}


# Function to select the appropriate GUID based on job applyDate
def get_month_guid(apply_date_str):
    if not cached_month_guids:
        with open(MONTHS_CONFIG_FILE, "r") as file:
            cached_month_guids.update(json.load(file))

    apply_date = datetime.strptime(apply_date_str, "%Y-%m-%d")
    month_key = apply_date.strftime("%Y-%m")  # Format as YYYY-MM
    return cached_month_guids.get(month_key)


def get_user_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def get_base_api_url():
    return "https://www.job-room.ch/onlineform-service/api/npa"


def get_base_api_url_of_work_efforts_for_month(apply_date_str):
    month_guid = get_month_guid(apply_date_str)
    if not month_guid:
        raise (f"No GUID found for month of {apply_date_str}")

    return get_base_api_url() + "/" + month_guid + "/work-efforts"


# Helper function to generate a unique hash for a job application
def generate_job_hash(job_data):
    # Concatenate relevant fields
    job_string = (
        f"{job_data['occupation']}_{job_data['applyDate']}_"
        f"{job_data['applyChannel']['formUrl']}_{job_data['applyChannel']['email']}_"
        f"{job_data['applyChannel']['address']['name']}"
    )
    # Generate MD5 hash of the concatenated string
    return hashlib.md5(job_string.encode()).hexdigest()
