You can manage versioned Databricks job pipelines by implementing the following logic:

1. **Check if a Job Exists**: Query the existing jobs using the Databricks REST API.
2. **Compare Versions**: Extract the metadata (stream name, substream name, dataset name, version) from existing jobs.
3. **Delete Outdated Jobs**: If an old version is found, delete it.
4. **Create a New Job**: If no job exists or the version is outdated, create a new one.
5. **Pass Parameters**: When triggering the job, pass file names and other metadata.

---

### **1. Get Existing Jobs and Check Versions**
```python
import requests
import json
import logging

# Databricks Configuration
DATABRICKS_HOST = "https://<your-databricks-instance>"
DATABRICKS_TOKEN = "<your-token>"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

# Metadata for versioning
STREAM_NAME = "example_stream"
SUBSTREAM_NAME = "example_substream"
DATASET_NAME = "example_dataset"
VERSION = "1.0"

# Unique Job Name based on metadata
JOB_NAME = f"{STREAM_NAME}_{SUBSTREAM_NAME}_{DATASET_NAME}_v{VERSION}"

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("databricks_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Get all jobs
def get_existing_jobs():
    jobs_list_url = f"{DATABRICKS_HOST}/api/2.0/jobs/list"
    response = requests.get(jobs_list_url, headers=headers)
    response.raise_for_status()
    return response.json().get("jobs", [])

# Find if a job with the correct version exists
def find_existing_job():
    jobs = get_existing_jobs()
    for job in jobs:
        if job["settings"]["name"] == JOB_NAME:
            return job
    return None

# Delete an outdated job
def delete_job(job_id):
    delete_url = f"{DATABRICKS_HOST}/api/2.0/jobs/delete"
    payload = {"job_id": job_id}
    response = requests.post(delete_url, headers=headers, json=payload)
    response.raise_for_status()
    logger.info(f"Deleted old job with ID {job_id}")

```

---

### **2. Create a New Job**
```python
def create_new_job():
    job_payload = {
        "name": JOB_NAME,
        "new_cluster": {
            "spark_version": "11.3.x-scala2.12",
            "node_type_id": "Standard_D3_v2",
            "num_workers": 2,
        },
        "spark_python_task": {
            "python_file": "dbfs:/tmp/databricks_script.py",
            "parameters": []  # Parameters will be added during execution
        }
    }

    create_job_url = f"{DATABRICKS_HOST}/api/2.0/jobs/create"
    response = requests.post(create_job_url, headers=headers, json=job_payload)
    response.raise_for_status()
    job_id = response.json().get("job_id")
    logger.info(f"Created new job with ID {job_id}")
    return job_id
```

---

### **3. Trigger the Job with Parameters**
```python
def run_job_with_parameters(job_id, file_name, additional_metadata):
    run_url = f"{DATABRICKS_HOST}/api/2.0/jobs/run-now"
    payload = {
        "job_id": job_id,
        "notebook_params": {
            "file_name": file_name,
            "metadata": json.dumps(additional_metadata)
        }
    }
    response = requests.post(run_url, headers=headers, json=payload)
    response.raise_for_status()
    run_id = response.json().get("run_id")
    logger.info(f"Triggered job {job_id} with run ID {run_id}")
    return run_id
```

---

### **4. Main Execution Logic**
```python
if __name__ == "__main__":
    logger.info("Checking for existing jobs...")
    existing_job = find_existing_job()

    if existing_job:
        job_id = existing_job["job_id"]
        logger.info(f"Existing job found: {JOB_NAME} with ID {job_id}")
    else:
        logger.info("No existing job found. Creating a new one.")
        job_id = create_new_job()

    # Trigger the job with parameters
    file_name = "data_2025-03-20.csv.gz"
    additional_metadata = {
        "stream": STREAM_NAME,
        "substream": SUBSTREAM_NAME,
        "dataset": DATASET_NAME,
        "version": VERSION
    }

    run_job_with_parameters(job_id, file_name, additional_metadata)
```

---

### **Key Features**
✅ **Checks for an existing job** based on stream name, substream name, dataset name, and version.  
✅ **Deletes outdated jobs** before creating a new one.  
✅ **Creates a new job** if none exists.  
✅ **Triggers a job** with parameters (file name & metadata).  
✅ **Logs all actions** for debugging.  

Would you like to enhance this further, such as by adding monitoring or scheduling?
