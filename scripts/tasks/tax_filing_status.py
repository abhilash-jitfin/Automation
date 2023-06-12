import os
import time
from typing import Dict, List, Optional, Union

import pandas as pd
from halo import Halo
from requests.exceptions import HTTPError

from ..exceptions import ValidationError
from ..files.base import BaseFile
from ..files.csv import CsvFile
from ..files.excel import ExcelFile
from ..utils.api_calls import ApiService, SimpleRequests
from ..utils.date_time import change_datetime_format, is_valid_period
from ..utils.files import (create_directory_if_not_exists,
                           is_valid_directory_path)
from ..utils.settings import load_settings
from ..utils.terminal import (COLOUR_ORANGE, COLOUR_RED, format_text,
                              get_clean_input)
from .abstract_task import BaseTask


class TaxFilingStatusTask(BaseTask):
    """
    A task to retrieve tax filing details for multiple GSTINs from a file.
    """
    description = "Task to retrieve tax filing details for multiple GSTINs from a file."
    FILE_CLASSES = {
        "CSV": CsvFile,
        "XLSX": ExcelFile
    }

    def __init__(self, token: Optional[str] = None):
        """
        Initialize TaxFilingStatusTask with token.
        :param token: API token, optional
        """
        self.simple_requests = SimpleRequests.get_instance(token)
        self.settings = load_settings()
        if self.simple_requests.headers.get("Authorization") is None:
            self.simple_requests.set_token(self.settings.get("token"))
        self.api_service = ApiService(token=self.settings.get("token"))

    def get_params(self) -> None:
        """
        Get parameters for the task from the user.
        """
        while True:
            self.directory_path = get_clean_input("Give the directory path containing the input files: ")
            print()
            if is_valid_directory_path(self.directory_path):
                break
            message = (
                f"The path given `{self.directory_path}` is not valid or it is a file. "
                "Please provide a valid directory path!"
            )
            print(f"{format_text(message, colour=COLOUR_RED)}\n")

        while True:
            prompt_question = (
                "For which filing period do you want to fetch the data "
                "(format is MM-YYYY. e.g 03-2023 for March 2023): "
            )
            filing_period = get_clean_input(prompt_question)
            print()
            if not is_valid_period(filing_period, "%m-%Y"):
                message = (
                    f"'{filing_period}' has an invalid format. "
                    "Please enter the filing period in the format 'MM-YYYY'.\n"
                )
                print(f"{format_text(message, colour=COLOUR_RED)}\n")
                continue
            self.filing_period = change_datetime_format(filing_period, "%m-%Y", "%b %Y")
            break

    def execute(self) -> None:
        """
        Execute the task by processing files in the given directory.
        """
        self.prepare_output_directory()
        files = self.get_input_files()
        self.process_files(files)

    def prepare_output_directory(self) -> None:
        """
        Prepare the output directory where the results will be saved.
        """
        self.output_dir = os.path.join(self.directory_path, "output")
        create_directory_if_not_exists(self.output_dir)

    def process_files(self, files: List[BaseFile]) -> None:
        """
        Process each file in the given list of files.
        :param files: List of file instances to be processed
        """
        for input_file in files:
            print(input_file.file_path)
            start_time = time.time()
            self.generate_output_file(input_file)
            end_time = time.time()
            time_taken = ((end_time - start_time)/60)
            print(
                f"Time taken to process the file: {format_text(f'{time_taken:.2f}', COLOUR_ORANGE)} minutes\n"
            )

    def get_input_files(self) -> List[BaseFile]:
        """
        Retrieve input files from the specified directory path.
        :return: List of file instances
        """
        files = []
        if not os.path.isdir(self.directory_path):
            message = f"{self.directory_path} is not a valid directory."
            print(format_text(message, colour=COLOUR_RED))
            return files

        supported_extensions = self.FILE_CLASSES.keys()
        for file in os.listdir(self.directory_path):
            filename = file
            extension = filename.split(".")[-1].upper()
            if extension not in supported_extensions:
                print(format_text(f'The file `{filename}` is not a valid input file.\n', colour=COLOUR_RED))
                continue
            file_path = os.path.join(self.directory_path, filename)
            if not os.path.isfile(file_path):
                continue
            file_instance = self.FILE_CLASSES[extension](file_path)
            files.append(file_instance)
        return files

    def get_gstins(self, file: BaseFile) -> List[str]:
        """
        Retrieve GSTINs from the file.
        :param file: Input file
        :return: List of GSTINs
        """
        file_df = file.read()
        gstin_column = next((col for col in file_df.columns if col.lower() == "gstin"), None)
        if gstin_column:
            return file_df[gstin_column].tolist()
        print("Column 'gstin' does not exist.")
        raise ValidationError("Column 'gstin' does not exist.")

    def generate_output_file_path(self, file_name: str) -> str:
        """
        Generate output file path for a given file name.
        :param file_name: Name of the input file
        :return: Path to the output file
        """
        base_name = os.path.basename(file_name)
        base, extension = os.path.splitext(base_name)
        return os.path.join(self.directory_path, "output", f"{base}_output.xlsx")

    def generate_output_file(self, file: BaseFile) -> None:
        """
        Generate output file containing tax filing data for GSTINs.
        :param file: Input file containing GSTINs
        """
        gstins = self.get_gstins(file)
        output_file_path = self.generate_output_file_path(file.file_path)
        data = []
        for index, gstin in enumerate(gstins, start=1):
            halo_message = format_text(f"{index}) Processing '{gstin}'", colour=COLOUR_ORANGE)
            with Halo(text=halo_message, spinner='dots') as spinner:
                tax_payer_response = self.api_service.call_taxpayer_endpoint(gstin)
                tax_payer_data = tax_payer_response.json()["data"]
                try:
                    tax_filing_response = self.api_service.call_tax_filing_status_endpoint(gstin)
                except HTTPError:
                    filing_data = [{"return_period": self.filing_period, "gstr1": "-", "gstr3b": "-"}]
                else:
                    if tax_filing_response.json()["data"]:
                        filing_data = tax_filing_response.json()["data"]["filing_data"]
                row_data = self.get_row_data(tax_payer_data, filing_data)
                data.append(row_data)
                spinner.succeed(f"{index}) Processed '{gstin}'")
        df = pd.DataFrame(data)
        df.to_excel(output_file_path, index=False)
        print(f"Created the output file - {output_file_path}")
        print()

    def get_row_data(self, tax_payer_data: Dict[str, str], tax_filing_data: Dict[str, str]) -> Dict[str, str]:
        """
        Extract relevant row data from tax payer data and tax filing data.
        :param tax_payer_data: Dictionary of tax payer data
        :param tax_filing_data: Dictionary of tax filing data
        :return: A dictionary of relevant data for a single row
        """
        filing_data = self.get_filing_data(tax_filing_data)
        return {
            "gstin": tax_payer_data["gstin"],
            "trade_name": tax_payer_data["trade_name"],
            "legal_name": tax_payer_data["legal_name"],
            "status": tax_payer_data["status"],
            "business_type": tax_payer_data["business_type"],
            "registration_date": tax_payer_data["registration_date"],
            "return_period": filing_data["return_period"],
            "gstr1": filing_data["gstr1"],
            "gstr3b": filing_data["gstr3b"],
        }

    def get_filing_data(self, data: Dict[str, Union[str, List[Dict]]]) -> Dict[str, str]:
        """
        Retrieve filing data from the data dictionary.
        :param data: Dictionary containing filing data
        :return: A dictionary of filing data
        """
        return next((entry for entry in data if entry["return_period"] == self.filing_period), {
            "return_period": self.filing_period, "gstr1": "-", "gstr3b": "-"
        })
