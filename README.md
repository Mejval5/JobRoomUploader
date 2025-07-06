# Job Room Uploader

This project automates the process of managing job applications by converting a TSV list of job entries into a JSON database, allowing updates, uploads, and deletions through the ORP job search platform API. The project also helps track job application statuses using a structured job search database, making it easier to organize and manage job applications as they progress.

## Usage
Designed for this website: https://www.job-room.ch/work-efforts
Designed to be usable with GitHub Projects' default export -> My example projects with all fields: https://github.com/users/Mejval5/projects/4/views/1

## Overview

This tool can do:

1. **Convert a TSV List of Jobs**: Parse a TSV file containing job details into JSON files ready for upload.
2. **Upload Job Applications**: Uploads each job JSON file as a new job search entry to the ORP job search platform. Caches the upload result to remember the job Id and what has been uploaded.
3. **Update Job Applications**: Goes through prepared JSON files and updates any job search results on the ORP website if they have been previously uploaded.
4. **Delete Uploaded Job Applications**: Clear out previously uploaded job entries from both the ORP website and the local JSON storage.

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure Python 3.x is installed.
- **Create Virtual Environment**: `python -m venv venv`
- **Activate Virtual Environment**: `.\.venv\Scripts\activate`
- **Setup repo**: `pip install -e .`
- **Install Dependencies**: `pip install -r requirements.txt`
- **User Config**: An API token, user Id, and unique URL Id stored in `user_config.json` for authentication with the ORP platform. 
   - `user_id` is the user id of the user who is posting the job. This one you can only see if you create/edit any job application and check the request payload in the network tab of the browser.
   - `bearer_token` is the token that you can get by inspecting the network tab of the browser when you are logged in and posting a job application. It is the `Authorization` header in the request payload. (don't forget to remove the `Bearer ` part of the token)
- **Months Config**: Each month in the API calls needs to be resolved into a special kind of GUID. I have created `months.json` which is tracked and contains mapping for the GUIDs. You can get the GUIDs for months either by looking into the network tab of the browser when you open the job application page and look for the response payload. Each months' applications are sorted inside an object with the key as the GUID of the month. You can also get the GUIDs by editing any job application and looking at the URL of the page. The GUID is just after the `edit/` part of the URL. Don't copy the item GUID, it is separated by `/`.

### Folder Structure

- **prepared_jsons/**: Contains JSON files prepared from the TSV file to be uploaded.
- **uploaded_jsons/**: Stores uploaded JSON files with job application IDs after successful upload.
- **all_uploads.json**: Logs hashes of each uploaded job to prevent duplicate processing.

### Fields and Possible Values

Each job entry in the TSV file contains the following fields:

| Field         | Description                                     | Possible Values                              |
|---------------|-------------------------------------------------|----------------------------------------------|
| **Title**     | Job title                                       | e.g., `Backend Developer`, `Unity Engineer` |
| **Status**    | Current application status                      | `In Progress`, `Waiting`, `Dead Ends`, `Offers`, `Opportunities & Job Sites` or other statuses   |
| **ApplyDate** | Date of application submission                  | e.g., `Oct 14, 2024`                          |
| **WebOrEmail**| Application submission URL or contact email     | URL of the job application or contact email                                |
| **Company**   | Company name                                    | e.g., `Swissquote`, `Microsoft`                |
| **Extra**     | Additional status info (e.g., Interview stage)  | Can only contain `"Interview"` or be empty for now.        |

### Usage

1. **Convert TSV to JSON**:
   - Jobs with the status `Opportunities & Job Sites` are ignored.
   - Run the script to parse the TSV and save each job entry as a JSON in `prepared_jsons/`.
   - JSON files are created in the following format:
     ```json
     {
         "id": null,
         "applyDate": "YYYY-MM-DD",
         "ravAssigned": false,
         "applyChannel": {
             "contactPerson": "",
             "email": "example@example.com",
             "formUrl": "https://example.com/job",
             "types": ["ELECTRONIC"],
             "address": {
                 "name": "Company Name",
             }
         },
         "applyStatus": ["REJECTED", "INTERVIEW"],
         "occupation": "Job Title",
         "fullTimeJob": true,
         "rejectionReason": "Ils avaient de nombreux candidats et ont décidé de ne pas suivre avec mon profil."
     }
     ```

2. **Upload Job Applications**:
   - The upload script checks `all_uploads.json` for existing hashes to avoid duplicate uploads.
   - Each job JSON is uploaded to the ORP platform with the appropriate `applyStatus`:
       - `"Dead Ends"` → `["REJECTED"]`
       - `"Offers"` → `["EMPLOYED"]`
       - Other statuses → `["PENDING"]`
   - If `"Interview"` is present in the `Extra` column, it appends `"INTERVIEW"` to `applyStatus`.

3. **Update Job Applications**:
   - If job statuses or rejection reasons change, the update script modifies existing entries on the ORP platform.
   - It only updates if there is a difference between the prepared JSON and the uploaded JSON entry, and after a successful update, it overwrites the local JSON file in `uploaded_jsons/` to match the new state.

4. **Delete Job Applications**:
   - The delete script removes each job entry from the ORP platform and deletes the corresponding JSON file and hash from `all_uploads.json`.
   - This ensures the job search database remains clean and up-to-date.

### Tracking Job Applications with GitHub Project

To track and organize job applications effectively, this project integrates well with a GitHub Projects board.
The board can be used to monitor the progress of each job application and keep track of the current status of each job.

1. **Create appropriate columns**:
   - Add following fields to the github project board:
      * `Status` - Single select with `In Progress`, `Waiting`, `Dead Ends`, `Offers`, `Opportunities & Job Sites`
      * `ApplyDate` - Date
      * `WebOrEmail` - Text
      * `Company` - Text
      * `Extra` - Single select with `Interview`
2. **Add job entries**:
   - Create a new card for each job application with the relevant details.
   - Use the `Status` column to track the current status of each job application.
   - Fill in the `ApplyDate`, `WebOrEmail`, `Company`, and `Extra` columns with the corresponding information.
3. **Update job statuses**:
   - As job statuses change, update the `Status` column in the GitHub project board.
   - Use the update script to keep the ORP job search database in sync with the GitHub project board.

### Example Workflow

#### Upload new jobs
1. **Get Data**: Export from github project or create TSV file in the project directory and adjust entries as needed.
2. **Prepare**: Run the `prepare_job_payloads.py` and verify the JSON files in `prepared_jsons/`.
3. **Upload**: Run the `upload_jobs.py` script to upload job applications to the ORP platform.

#### Update previously uploaded jobs (can be done after uploading new jobs)
1. **Get Data**: Export from github project or create TSV file in the project directory and adjust entries as needed.
2. **Prepare**: Run the `prepare_job_payloads.py` and verify the JSON files in `prepared_jsons/`.
3. **Update**: Run the `update_jobs.py` script to update job applications on the ORP platform.

#### Delete all previously uploaded jobs
1. **Delete**: Run the `delete_jobs.py` script to delete all job applications from the ORP platform.

### Notes

- Ensure `token.txt` contains a valid API token to authenticate API requests.
- The scripts use `all_uploads.json` to track uploaded job applications, so deleting `all_uploads.json` will reset tracking.

## License

This project is open-source and may be used and modified according to the terms of the MIT license.
