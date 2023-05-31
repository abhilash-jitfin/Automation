import os
import requests
import time

from .abstract_task import BaseTask
from ..utils.api_calls import SimpleRequests


class PreRegisterFileProcessingTask(BaseTask):
    description = "Task to upload, process, and download a file for pre-registration"

    def __init__(self, token=None):
        self.simple_requests = SimpleRequests.get_instance(token)

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.file_path = input("\nEnter the file path: ")
        print("\n")

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
            response = self.simple_requests.post(
                "/accounts/pre-register/file/upload", files={"files": open(self.file_path, "rb")}
            )
            file_id = None
            try:
                file_id = int(response.json().get('data', '')[-2:])
            except ValueError:
                print("Failed to upload the file.")
                return
            if file_id:
                print("File uploaded successfully.")
                return file_id
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload the file. Error: {e}")

        return None

    def process_file(self, file_id: str) -> str:
        """Process the file."""
        try:
            response = self.simple_requests.post(f"/accounts/pre-register/file/{file_id}/process")
            if response.status_code == 200:
                print("File processed successfully.")
                return file_id
            else:
                print("Failed to process the file.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to process the file. Error: {e}")

        return None

    def download_file(self, file_id: str) -> None:
        """Download the processed file."""
        try:
            response = self.simple_requests.get(f"/accounts/pre-register/file/{file_id}/result")
            if response:
                split = os.path.splitext(self.file_path)
                output_file_path = os.path.join(
                    os.path.dirname(self.file_path), f"{split[0]}_output{split[1]}"
                )
                # filename = f"processed_{file_id}.xlsx"
                with open(output_file_path, "wb") as file:
                    file.write(response.content)
                print(f"Processed file downloaded successfully: {os.path.basename(output_file_path)}")
            else:
                print("Failed to download the processed file.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the processed file. Error: {e}")
