import hashlib
import json

CONFIG_FILE = "user_config.json"

DEFAULT_REJECTION_REASON = (
    "Ils avaient de nombreux candidats et ont décidé de ne pas suivre avec mon profil."
)


def get_user_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


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
