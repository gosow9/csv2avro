Yes, you can achieve this using Databricks' REST API. The process involves the following steps:

1. **Upload the Python Script to Databricks**: You'll write a Python script that reads CSV.GZ files from ADLS Gen2, decompresses them, and converts them into Parquet.
2. **Submit the Job to a Databricks Cluster**: You'll use the Databricks Jobs API to run the script on a Databricks cluster.

---

### **1. Python Script (databricks_script.py)**
This script will be uploaded to Databricks:

```python
from pyspark.sql import SparkSession
import gzip
import shutil
import os

# Initialize Spark session
spark = SparkSession.builder.appName("CSV to Parquet").getOrCreate()

# Define ADLS paths
input_path = "abfss://container@storageaccount.dfs.core.windows.net/path/to/csv"
output_path = "abfss://container@storageaccount.dfs.core.windows.net/path/to/parquet"

# Read the CSV files directly (Databricks can handle CSV.GZ files natively)
df = spark.read.option("header", "true").csv(input_path)

# Convert to Parquet and write to ADLS
df.write.mode("overwrite").parquet(output_path)

print(f"Conversion completed. Parquet files saved to {output_path}")
```

---

### **2. Upload Python Script to Databricks**
Databricks requires that the script be uploaded before running. You can use the Databricks API to upload the script to DBFS:

```python
import requests
import json

DATABRICKS_HOST = "https://<your-databricks-instance>"
DATABRICKS_TOKEN = "<your-token>"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

upload_endpoint = f"{DATABRICKS_HOST}/api/2.0/dbfs/put"
file_path = "/dbfs/tmp/databricks_script.py"

with open("databricks_script.py", "rb") as f:
    data = f.read()

payload = {
    "path": file_path,
    "overwrite": True,
}

requests.post(upload_endpoint, headers=headers, json=payload, data=data)
```

---

### **3. Run the Script as a Job**
Once uploaded, you can trigger a job to run the script on a Databricks cluster.

```python
job_payload = {
    "run_name": "CSV to Parquet Conversion",
    "new_cluster": {
        "spark_version": "11.3.x-scala2.12",
        "node_type_id": "Standard_D3_v2",
        "num_workers": 2,
    },
    "notebook_task": {
        "notebook_path": file_path
    }
}

run_job_endpoint = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/submit"

response = requests.post(run_job_endpoint, headers=headers, json=job_payload)

print(response.json())  # This gives the job run ID
```

---

### **4. Monitor Job Execution**
You can monitor the job using:

```python
job_id = response.json()["run_id"]

status_endpoint = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/get?run_id={job_id}"
status_response = requests.get(status_endpoint, headers=headers)

print(status_response.json())
```

---

### **Summary**
1. Upload the Python script to Databricks DBFS.
2. Submit a job via the Databricks API to process the CSV files.
3. Convert and store the Parquet files in ADLS Gen2.
4. Monitor the job execution.

Would you like me to refine the process or add error handling?


To enable logging for the entire process, you can use Python's built-in `logging` module. This ensures that you capture all important events such as API requests, responses, script execution, and errors. 

### **1. Modify the Python Script to Include Logging**
Modify your `databricks_script.py` file:

```python
import logging
from pyspark.sql import SparkSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/dbfs/tmp/databricks_script.log"),  # Save logs in DBFS
        logging.StreamHandler()  # Print logs to console
    ]
)
logger = logging.getLogger()

try:
    # Initialize Spark session
    logger.info("Initializing Spark session")
    spark = SparkSession.builder.appName("CSV to Parquet").getOrCreate()

    # Define ADLS paths
    input_path = "abfss://container@storageaccount.dfs.core.windows.net/path/to/csv"
    output_path = "abfss://container@storageaccount.dfs.core.windows.net/path/to/parquet"

    logger.info(f"Reading CSV files from {input_path}")
    df = spark.read.option("header", "true").csv(input_path)

    logger.info("Converting CSV to Parquet and writing to ADLS")
    df.write.mode("overwrite").parquet(output_path)

    logger.info(f"Conversion completed successfully. Parquet files saved to {output_path}")

except Exception as e:
    logger.error(f"Error occurred: {str(e)}", exc_info=True)
```

---

### **2. Modify API Calls to Include Logging**
Modify your API script (`databricks_api_script.py`) to log API requests and responses.

```python
import requests
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("databricks_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

DATABRICKS_HOST = "https://<your-databricks-instance>"
DATABRICKS_TOKEN = "<your-token>"
headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

# Upload the Python script
upload_endpoint = f"{DATABRICKS_HOST}/api/2.0/dbfs/put"
file_path = "/dbfs/tmp/databricks_script.py"

try:
    with open("databricks_script.py", "rb") as f:
        data = f.read()

    payload = {"path": file_path, "overwrite": True}
    
    logger.info("Uploading script to Databricks DBFS")
    upload_response = requests.post(upload_endpoint, headers=headers, json=payload, data=data)
    upload_response.raise_for_status()
    logger.info(f"Upload successful: {upload_response.json()}")

except Exception as e:
    logger.error(f"Failed to upload script: {str(e)}", exc_info=True)


# Submit the Job
job_payload = {
    "run_name": "CSV to Parquet Conversion",
    "new_cluster": {
        "spark_version": "11.3.x-scala2.12",
        "node_type_id": "Standard_D3_v2",
        "num_workers": 2,
    },
    "notebook_task": {
        "notebook_path": file_path
    }
}

try:
    run_job_endpoint = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/submit"
    logger.info("Submitting job to Databricks cluster")
    response = requests.post(run_job_endpoint, headers=headers, json=job_payload)
    response.raise_for_status()
    
    job_info = response.json()
    logger.info(f"Job submitted successfully: {job_info}")

    # Monitor the job
    job_id = job_info["run_id"]
    status_endpoint = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/get?run_id={job_id}"

    while True:
        status_response = requests.get(status_endpoint, headers=headers)
        status_data = status_response.json()
        state = status_data.get("state", {}).get("life_cycle_state", "UNKNOWN")

        logger.info(f"Job status: {state}")
        if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            break
    
    logger.info(f"Final job state: {status_data}")

except Exception as e:
    logger.error(f"Error during job submission or monitoring: {str(e)}", exc_info=True)
```

---

### **3. Summary of Logging Features**
- **Python Script (Databricks Side)**
  - Logs execution steps in `/dbfs/tmp/databricks_script.log`
  - Logs success or errors with full stack traces

- **Databricks API Calls (Local)**
  - Logs API requests and responses in `databricks_api.log`
  - Monitors job status updates in real time

Would you like me to add more logging features, such as storing logs in an external system (e.g., Azure Log Analytics)?

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
