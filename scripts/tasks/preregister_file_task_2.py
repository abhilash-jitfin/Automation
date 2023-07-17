import os
from os import listdir
from os.path import isfile, join
from typing import Optional, Tuple

import pandas as pd
import requests
from halo import Halo

from ..files.excel import ExcelFile
from ..utils.api_calls import ApiService
from ..utils.files import create_directory_if_not_exists, is_valid_directory_path, move_file_to_destination_dir
from ..utils.settings import load_settings
from ..utils.terminal import get_clean_input
from .abstract_task import BaseTask


class PreRegisterFileProcessingTask_V2(BaseTask):
    description = "V2 version of Task to upload, process, and download a file for pre-registration. (Beta version)"

    def __init__(self, token: Optional[str] = None):
        self.settings = load_settings()
        environment = self.settings.get("environment", "")
        token = self.settings.get(environment, {}).get("token")
        self.api_service = ApiService(token=token, environment=environment)
        self.simple_requests = self.api_service.requester

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        while True:
            self.input_path = get_clean_input("\nEnter the input file path: ")
            if os.path.isfile(self.input_path):
                break
            print(f"\nInvalid input file path '{self.input_path}'")
        self.basename = os.path.basename(self.input_path)
        self.input_dir = join(os.path.dirname(self.input_path), os.path.splitext(self.basename)[0])

    def execute(self) -> None:
        """Execute the task."""
        self.prepare_directories()
        print(f"\n- Processing {self.input_path}")
        self.create_temp_files()

    def prepare_directories(self) -> None:
        """Prepare directories for processed, failed and result files."""
        self.temp_dir = join(self.input_dir, "Temp")
        self.failed_dir = join(self.input_dir, "Failed")
        self.result_dir = join(self.input_dir, "Result")
        self.processed_dir = join(self.input_dir, "Processed")
        for dir_path in [self.temp_dir, self.processed_dir, self.failed_dir, self.result_dir]:
            create_directory_if_not_exists(dir_path)

    def create_temp_files(self) -> None:
        """Process a single file."""
        df, gstin_dups_df, phone_number_dups_df = self.clean_file()
        files = [
            (df, join(self.temp_dir, f"{base_name}_unique.xlsx")),
            (gstin_dups_df, join(self.temp_dir, f"{base_name}_gstin_dups.xlsx")),
            (phone_number_dups_df, join(self.temp_dir, f"{base_name}_phone_number_dups.xlsx")),
        ]
        for data_frame, output_path in files:
            self.save_df_to_excel(data_frame, output_path)

    def clean_file(self, ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Clean the input file and return DataFrames."""
        df = ExcelFile(self.input_path).read()
        return df, self.create_duplicate_dfs(df, "gstin"), self.create_duplicate_dfs(df, "phone_number")

    def process_input_files(self):
        input_files = [f for f in listdir(self.input_path) if isfile(join(self.input_path, f)) and f.endswith(".xlsx")]
        for file_name in input_files:
            self.file_path = files[0][1]
            file_id = self.upload_file()
            if file_id and self.process_file(file_id):
                output_file_path = self.download_file(file_id)
                if output_file_path:
                    move_file_to_destination_dir(file_path, self.processed_dir, can_overwrite=True)
                    move_file_to_destination_dir(output_file_path, self.result_dir, can_overwrite=True)
                    return

        move_file_to_destination_dir(file_path, self.failed_dir, can_overwrite=True)

    @staticmethod
    def save_df_to_excel(df: pd.DataFrame, file_path: str) -> None:
        """Save a DataFrame to an Excel file."""
        df["phone_number"] = (
            df["phone_number"].astype("string").apply(PreRegisterFileProcessingTask.update_phone_number)
        )
        ExcelFile(file_path).save(df)

    @staticmethod
    def update_phone_number(phone_number: str) -> str:
        """Ensure phone number starts with '+91'."""
        if phone_number.startswith("91") and len(phone_number) == 12:
            return "+" + phone_number
        if not phone_number.startswith("+91") and len(phone_number) == 10:
            return "+91" + phone_number
        return phone_number

    @staticmethod
    def create_duplicate_dfs(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Create DataFrames for duplicate entries."""
        duplicates_df = df[df.duplicated(subset=[column], keep=False)]
        duplicates_df = duplicates_df.sort_values(by=column)
        duplicates_df = duplicates_df[["gstin", "phone_number", "name", "email"]]

        return pd.concat(
            [
                duplicates_df,
                pd.DataFrame({"gstin": ["---"], "name": ["---"], "email": ["---"], "phone_number": ["---"]}),
            ]
        )

    def upload_file(self) -> Optional[str]:
        """Upload the file and return file_id."""
        spinner = Halo(text="Uploading File", spinner="dots")
        spinner.start()

        try:
            with open(self.file_path, "rb") as f:
                response = self.simple_requests.post(
                    ApiService.PRE_REGISTER_FILE_UPLOAD_ENDPOINT, files={"files": f}, stream=True
                )
            response_data = response.json().get("data", {})
            file_id = str(response_data.get("file_id"))

            if file_id:
                spinner.succeed("File uploaded successfully.")
                return file_id

        except (requests.exceptions.RequestException, ValueError, KeyError):
            spinner.fail("Failed to upload the file.")

        return None

    def process_file(self, file_id: str) -> bool:
        """Process the file and return success status."""
        spinner = Halo(text="Processing File", spinner="dots")
        spinner.start()

        try:
            response = self.simple_requests.post(f"accounts/pre-register/file/{file_id}/process", stream=True)
            if response.status_code == 200:
                spinner.succeed("File processed successfully.")
                return True
        except requests.exceptions.RequestException:
            pass

        spinner.fail("Failed to process the file.")
        return False

    def download_file(self, file_id: str) -> Optional[str]:
        """Download the processed file."""
        spinner = Halo(text="Downloading File", spinner="dots")
        spinner.start()

        try:
            response = self.simple_requests.get(f"accounts/pre-register/file/{file_id}/result", stream=True)
            if response:
                output_file_path = self.file_path.replace("unique", "output")
                with open(output_file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                spinner.succeed(f"Processed file downloaded successfully: {os.path.basename(output_file_path)}")
                return output_file_path
        except requests.exceptions.RequestException:
            pass

        spinner.fail("Failed to download the processed file.")
        return None
