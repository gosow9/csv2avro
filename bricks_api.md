Below is an example of how you might structure a small Python client library to interact with Databricks Jobs via their REST API. This example uses the `requests` library, and it assumes you have a custom function (or library) that retrieves your personal access token. Adjust the code to fit your internal authentication and environment.

---

## Example: DatabricksJobsClient

```python
import requests

class DatabricksJobsClient:
    """
    A small helper class to interact with the Databricks Jobs REST API.
    """

    def __init__(self, workspace_url: str, token_retriever):
        """
        :param workspace_url: The base URL of the Databricks workspace, e.g. https://<region>.azuredatabricks.net
        :param token_retriever: A callable (or custom object) that returns a valid Azure Databricks Personal Access Token when called.
        """
        self.workspace_url = workspace_url.rstrip("/")
        self.token_retriever = token_retriever
        self.api_version = "2.1"  # or specify version if you need a different version (some endpoints use 2.0 or 2.1)
    
    def _get_headers(self):
        """
        Retrieve headers, including the authorization token, for requests.
        """
        token = self.token_retriever()  # Retrieve your personal access token via your custom library
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_job(self, job_settings: dict) -> dict:
        """
        Creates a new job in Databricks.
        
        :param job_settings: The JSON payload describing the job configuration, e.g.:
            {
                "name": "My New Job",
                "new_cluster": {
                    "spark_version": "9.1.x-scala2.12",
                    "node_type_id": "Standard_DS3_v2",
                    "num_workers": 2,
                },
                "spark_jar_task": {
                    "main_class_name": "com.example.jobs.SampleJobMain"
                }
            }
        :return: The JSON response from the create job request.
        """
        url = f"{self.workspace_url}/api/{self.api_version}/jobs/create"
        response = requests.post(url, headers=self._get_headers(), json=job_settings)
        response.raise_for_status()
        return response.json()
    
    def run_now(self, job_id: int, extra_params: dict = None) -> dict:
        """
        Triggers a run of the specified job with optional job parameters.
        
        :param job_id: The integer Job ID of the job to run.
        :param extra_params: Optional dict of extra parameters for the run, e.g. jar_params, notebook_params, python_params
        :return: The JSON response from the run-now request.
        """
        url = f"{self.workspace_url}/api/{self.api_version}/jobs/run-now"
        payload = {"job_id": job_id}
        if extra_params:
            payload.update(extra_params)
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_run(self, run_id: int) -> dict:
        """
        Retrieves the metadata of a specific run, including status.
        
        :param run_id: The integer Run ID of the job run.
        :return: The JSON response containing run information, including status, start/end times, and cluster info.
        """
        url = f"{self.workspace_url}/api/{self.api_version}/jobs/runs/get?run_id={run_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_jobs(self) -> dict:
        """
        Lists all jobs in the workspace.
        
        :return: The JSON response containing the list of jobs.
        """
        url = f"{self.workspace_url}/api/{self.api_version}/jobs/list"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_job(self, job_id: int) -> dict:
        """
        Deletes the specified job.
        
        :param job_id: The integer Job ID to delete.
        :return: The JSON response from the delete request.
        """
        url = f"{self.workspace_url}/api/{self.api_version}/jobs/delete"
        payload = {"job_id": job_id}
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
```

### Usage Example

1. **Token retrieval**  
   Suppose you have a custom function `get_token()` in your own library that retrieves a valid Databricks PAT (Personal Access Token). For example:

   ```python
   from my_custom_auth_lib import get_databricks_token

   def get_token():
       return get_databricks_token()  # however your library fetches the token
   ```

2. **Instantiating the client**  
   ```python
   # Suppose your workspace URL is something like: "https://eastus2.azuredatabricks.net"
   # Make sure to replace it with your actual Databricks instance URL.
   dbx_client = DatabricksJobsClient(
       workspace_url="https://eastus2.azuredatabricks.net",
       token_retriever=get_token
   )
   ```

3. **Creating a job**  
   ```python
   job_settings = {
       "name": "My Example Job",
       "new_cluster": {
           "spark_version": "9.1.x-scala2.12",
           "node_type_id": "Standard_DS3_v2",
           "num_workers": 2
       },
       "spark_jar_task": {
           "main_class_name": "com.example.jobs.SampleJobMain",
           "parameters": ["--input", "data.csv", "--output", "results/"]
       }
   }

   create_job_response = dbx_client.create_job(job_settings)
   print("Create Job Response:", create_job_response)
   ```

4. **Listing jobs**  
   ```python
   jobs_list = dbx_client.list_jobs()
   print("Jobs:", jobs_list)
   ```

5. **Running a job**  
   ```python
   # Example: let's run the job we just created
   job_id = create_job_response["job_id"]
   run_response = dbx_client.run_now(job_id)
   print("Run Job Response:", run_response)
   ```

6. **Polling the run**  
   ```python
   from time import sleep

   run_id = run_response["run_id"]
   run_details = dbx_client.get_run(run_id)
   
   while run_details["state"]["life_cycle_state"] not in ["TERMINATED", "INTERNAL_ERROR", "SKIPPED"]:
       print("Job is still running...")
       sleep(10)  # Wait a few seconds between checks
       run_details = dbx_client.get_run(run_id)
   
   print("Final run details:", run_details)
   ```

7. **Deleting a job**  
   ```python
   dbx_client.delete_job(job_id)
   print(f"Job with ID {job_id} has been deleted.")
   ```

---

### Things to Note

- **API Versions**:  
  The Databricks Jobs API has multiple versions (v2.0, v2.1, etc.). Some endpoints are only available in certain API versions. Make sure you match the endpoint version to your code or adapt this abstraction layer to handle differences in endpoints.

- **Error Handling**:  
  This example uses `response.raise_for_status()`, which throws an exception if Databricks returns an HTTP error (e.g., 400, 401, 404, 500). You can wrap these calls in try-except blocks and handle them as needed in your production environment.

- **Security**:  
  Ensure that your custom token retrieval is secure (i.e., don’t log sensitive tokens, store them in plain text, etc.).

- **Workspace URL**:  
  Make sure your `workspace_url` is correct (e.g. `https://<region>.azuredatabricks.net` for Azure Databricks, or `https://<org-id>.cloud.databricks.com` for Databricks on AWS).

- **Additional Features**:  
  You can expand this class with more methods to handle advanced functionalities, such as getting run output, canceling runs, updating jobs, listing run history, etc.

---

Using this pattern, you can build a more robust abstraction layer, and keep your Python code neatly organized when dealing with the Databricks REST API for jobs.
