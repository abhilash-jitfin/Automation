import requests
import time

from .abstract_task import BaseTask
from ..utils.api_calls import SimpleRequests


class PreRegisterFileProcessingTask(BaseTask):
    description = "Task to upload, process, and download a file for pre-registration"

    def __init__(self, token=None):
        self.base_url = "https://qa.appv2.kyss.ai/apis/accounts/pre-register/file"
        self.simple_requests = SimpleRequests(self.base_url, token)

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.file_path = input("\nEnter the file path: ")

    def execute(self) -> None:
        """Execute the task."""
        if self.simple_requests.headers.get('Authorization') is None:
            print("Token is missing. Please provide a valid token.")
            return

        file_id = self.upload_file()
        if file_id:
            processed_file_id = self.process_file(file_id)
            if processed_file_id:
                self.download_file(processed_file_id)

    def upload_file(self) -> str:
        """Upload the file."""
        try:
            response = self.simple_requests.post("/upload", files={"files": open(self.file_path, "rb")})
            file_id = response.get("file_id")
            if file_id:
                print("File uploaded successfully.")
                return file_id
            else:
                print("Failed to upload the file.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload the file. Error: {e}")

        return None

    def process_file(self, file_id: str) -> str:
        """Process the file."""
        try:
            response = self.simple_requests.post(f"/{file_id}/process")
            processed_file_id = response.get("processed_file_id")
            if processed_file_id:
                print("File processed successfully.")
                return processed_file_id
            else:
                print("Failed to process the file.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to process the file. Error: {e}")

        return None

    def download_file(self, file_id: str) -> None:
        """Download the processed file."""
        try:
            response = self.simple_requests.get(f"/{file_id}/result")
            if response:
                filename = f"processed_{file_id}.xlsx"
                with open(filename, "wb") as file:
                    file.write(response.content)
                print(f"Processed file downloaded successfully: {filename}")
            else:
                print("Failed to download the processed file.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the processed file. Error: {e}")
