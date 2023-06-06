import os

import pandas as pd
import requests
from halo import Halo

from ..utils.api_calls import SimpleRequests, ApiConstants
from ..utils.settings import load_settings
from .abstract_task import BaseTask


class PreRegisterFileProcessingTask(BaseTask):
    description = "Task to upload, process, and download a file for pre-registration"

    def __init__(self, token=None):
        self.simple_requests = SimpleRequests.get_instance(token)
        self.settings = load_settings()
        if self.simple_requests.headers.get('Authorization') is None:
            self.simple_requests.set_token(self.settings.get('token'))

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.file_path = input("\nEnter the file path: ")
        print("\n")

    def execute(self) -> None:
        """Execute the task."""
        df, gstin_dups_df, phone_number_dups_df = self.clean_file()

        input_file_name = os.path.basename(self.file_path)
        output_dir = os.path.dirname(self.file_path)
        output_unique_file = os.path.join(output_dir, f"{os.path.splitext(input_file_name)[0]}_unique.xlsx")
        output_gstin_dups_file = os.path.join(output_dir, f"{os.path.splitext(input_file_name)[0]}_gstin_dups.xlsx")
        output_phone_number_dups_file = os.path.join(output_dir, f"{os.path.splitext(input_file_name)[0]}_phone_number_dups.xlsx")

        # Preserve leading plus sign in phone number column
        df['phone_number'] = df['phone_number'].astype('string')
        gstin_dups_df['phone_number'] = gstin_dups_df['phone_number'].astype('string')
        phone_number_dups_df['phone_number'] = phone_number_dups_df['phone_number'].astype('string')

        df.to_excel(output_unique_file, index=False)
        gstin_dups_df.to_excel(output_gstin_dups_file, index=False)
        phone_number_dups_df.to_excel(output_phone_number_dups_file, index=False)

        file_id = self.upload_file()
        if file_id:
            processed_file_id = self.process_file(file_id)
            if processed_file_id:
                self.download_file(processed_file_id)




    def clean_file(self):
        df = pd.read_excel(self.file_path)

        # Create a DataFrame to represent the separator row
        separator_df = pd.DataFrame({'gstin': ['---'], 'name': ['---'], 'email': ['---'], 'phone_number': ['---']})

        has_gstin_duplicates = not df['gstin'].is_unique
        gstin_duplicates_df = df[df.duplicated(subset=['gstin'], keep=False)]
        gstin_duplicates_df = gstin_duplicates_df[['gstin', 'phone_number', 'name', 'email']]

        has_phone_number_duplicates = not df['phone_number'].is_unique
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
                rows.append(pd.DataFrame({'gstin': ['---'], 'name': ['---'], 'email': ['---'], 'phone_number': ['---']}))
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
            response = self.simple_requests.post(
                ApiConstants.PRE_REGISTER_FILE_UPLOAD_ENDPOINT,
                files={"files": open(self.file_path, "rb")},
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
