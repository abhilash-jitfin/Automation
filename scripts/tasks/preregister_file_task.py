import os
from typing import Optional

import pandas as pd
import requests
from halo import Halo

from ..utils.api_calls import ApiService, SimpleRequests
from ..utils.files import create_directory_if_not_exists
from ..utils.settings import load_settings
from .abstract_task import BaseTask


class PreRegisterFileProcessingTask(BaseTask):
    description = "Task to upload, process, and download a file for pre-registration"

    def __init__(self, token: Optional[str] = None):
        self.simple_requests = SimpleRequests.get_instance(token)
        self.settings = load_settings()
        if self.simple_requests.headers.get('Authorization') is None:
            self.simple_requests.set_token(self.settings.get('token'))

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.file_path = input("\nEnter the file path: ").strip()
        print("\n")

    def execute(self) -> None:
        """Execute the task."""
        df, gstin_dups_df, phone_number_dups_df = self.clean_file()

        input_file_name = os.path.basename(self.file_path)
        name_without_extension, _ = os.path.splitext(input_file_name)
        output_dir = os.path.join(os.path.dirname(self.file_path), name_without_extension)
        create_directory_if_not_exists(output_dir)

        files = [
            (df, self.generate_file_name(input_file_name, "unique")),
            (gstin_dups_df, self.generate_file_name(input_file_name, "gstin_dups")),
            (phone_number_dups_df, self.generate_file_name(input_file_name, "phone_number_dups"))
        ]
        for df, file_name in files:
            output_file = os.path.join(output_dir, file_name)
            self.save_df_to_excel(df, output_file)

        self.file_path = os.path.join(output_dir, self.generate_file_name(input_file_name, "unique"))
        file_id = self.upload_file()
        if file_id:
            processed_file_id = self.process_file(file_id)
            if processed_file_id:
                self.download_file(processed_file_id)

    def generate_file_name(self, input_file_name: str, descriptor: str) -> str:
        """Generate an output file name based on the input file name and a descriptor."""
        return f"{os.path.splitext(input_file_name)[0]}_{descriptor}.xlsx"

    def save_df_to_excel(self, df: pd.DataFrame, file_path: str) -> None:
        """Save a DataFrame to an Excel file."""
        df['phone_number'] = df['phone_number'].astype('string')
        df['phone_number'] = df['phone_number'].apply(self.update_phone_number)
        df.to_excel(file_path, index=False)

    def update_phone_number(self, phone_number: str) -> str:
        """Ensure phone number starts with '+91'."""
        if phone_number.startswith('91') and len(phone_number) == 12:
            phone_number = '+' + phone_number
        elif not phone_number.startswith('+91') and len(phone_number) == 10:
            phone_number = '+91' + phone_number

        return phone_number

    def clean_file(self):
        df = pd.read_excel(self.file_path)

        gstin_duplicates_df = df[df.duplicated(subset=['gstin'], keep=False)]
        gstin_duplicates_df = gstin_duplicates_df[['gstin', 'phone_number', 'name', 'email']]

        phone_number_duplicates_df = df[df.duplicated(subset=['phone_number'], keep=False)]
        phone_number_duplicates_df = phone_number_duplicates_df[['gstin', 'phone_number', 'name', 'email']]

        gstin_dups_df = self.create_duplicate_dfs(gstin_duplicates_df, 'gstin')
        phone_number_dups_df = self.create_duplicate_dfs(phone_number_duplicates_df, 'phone_number')

        df = df.drop_duplicates(subset=['gstin'], keep=False)
        df = df.drop_duplicates(subset=['phone_number'], keep=False)
        return df, gstin_dups_df, phone_number_dups_df

    def create_duplicate_dfs(self, df, column):
        df = df.sort_values(by=column)
        previous = None
        result_df = pd.DataFrame(columns=['gstin', 'name', 'email', 'phone_number'])
        rows = []  # Initialize an empty list for rows

        for index, row in df.iterrows():
            if previous is not None and previous[column] != row[column]:
                rows.append(pd.DataFrame({
                        'gstin': ['---'], 'name': ['---'], 'email': ['---'], 'phone_number': ['---']
                    }
                ))
            rows.append(row.to_frame().T)
            previous = row

        if rows:  # Check if the rows list is not empty
            result_df = pd.concat(rows)

        return result_df

    def upload_file(self) -> str:
        """Upload the file."""
        spinner = Halo(text="Uploading File", spinner="dots")
        spinner.start()
        try:
            with open(self.file_path, "rb") as f:
                response = self.simple_requests.post(
                    ApiService.PRE_REGISTER_FILE_UPLOAD_ENDPOINT,
                    files={"files": f},
                    stream=True,
                )
            file_id = None
            try:
                file_id = int(response.json().get('data', '')[-2:])
            except ValueError:
                print("Failed to upload the file.")
                return
            if file_id:
                spinner.succeed("File uploaded successfully.")
                return file_id
        except requests.exceptions.RequestException as e:
            spinner.fail(f"Failed to upload the file. Error: {e}")

        return None

    def process_file(self, file_id: str) -> str:
        """Process the file."""
        spinner = Halo(text="Processing File", spinner="dots")
        spinner.start()
        try:
            response = self.simple_requests.post(f"accounts/pre-register/file/{file_id}/process", stream=True)
            if response.status_code == 200:
                spinner.succeed("File processed successfully.")
                return file_id
            else:
                print("Failed to process the file.")
        except requests.exceptions.RequestException as e:
            spinner.fail(f"Failed to process the file. Error: {e}")

        return None

    def download_file(self, file_id: str) -> None:
        """Download the processed file."""
        spinner = Halo(text="Downloading File", spinner="dots")
        spinner.start()
        try:
            response = self.simple_requests.get(f"accounts/pre-register/file/{file_id}/result", stream=True)
            if response:
                split = os.path.splitext(self.file_path)
                output_file_path = os.path.join(
                    os.path.dirname(self.file_path), f"{split[0]}_output{split[1]}"
                )
                with open(output_file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                spinner.succeed(f"Processed file downloaded successfully: {os.path.basename(output_file_path)}")
            else:
                spinner.fail("Failed to download the processed file.")
        except requests.exceptions.RequestException as e:
            spinner.fail(f"Failed to download the processed file. Error: {e}")
