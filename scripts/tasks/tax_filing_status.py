import os
from typing import Optional, List

import pandas as pd
import requests
from halo import Halo

from ..files.base import BaseFile
from ..files.csv import CsvFile
from ..files.excel import ExcelFile
from ..utils.api_calls import ApiService, SimpleRequests
from ..utils.date_time import change_datetime_format, is_valid_period
from ..utils.files import create_directory_if_not_exists, is_valid_directory_path
from ..utils.settings import load_settings
from ..utils.terminal import COLOURS, format_text
from .abstract_task import BaseTask


class TaxFilingStatusTask(BaseTask):
    description = "Task to get the tax filing details, GSTR1 and GSTR3B, for a number of GSTINs in a file."

    FILE_CLASSES = {
        "CSV": CsvFile,
        "XLSX": ExcelFile
    }

    def __init__(self, token: Optional[str] = None):
        self.simple_requests = SimpleRequests.get_instance(token)
        self.settings = load_settings()
        if self.simple_requests.headers.get("Authorization") is None:
            self.simple_requests.set_token(self.settings.get("token"))
        self.api_service = ApiService(token=self.settings.get("token"))

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        while True:
            self.directory_path = input("Enter the directory path containing the files: ").strip()
            print()
            if is_valid_directory_path(self.directory_path):
                break
            print(
                (
                    f"The path given `{format_text(self.directory_path, colour=COLOURS['red'], bold=True)}`"
                    " is not valid or it is a file. "
                    "Please provide a valid directory path!"
                )
            )
            print()

        while True:
            filing_period = input("Enter the filing period (format is MM-YYYY): ").strip()
            print()
            if not is_valid_period(filing_period, "%m-%Y"):
                message = (
                    f"'{filing_period}' has an invalid format. "
                    "Please enter the filing period in the format 'MM-YYYY'.\n"
                )
                print(format_text(message, colour_code=COLOURS['red']))
                continue
            self.filing_period = change_datetime_format(filing_period, "%m-%Y", "%b %Y")
            break


    def execute(self) -> None:
        files = self.get_input_files()
        print(f"{files}\n")

        self.output_dir = os.path.join(self.directory_path, "output")
        create_directory_if_not_exists(self.output_dir)

        for input_file in files:
            print(input_file.file_path)
            self.generate_output_file(input_file)

    def get_input_files(self):
        files = []
        directory = os.fsencode(self.directory_path)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            file_path = os.path.join(directory.decode("utf-8"), filename)
            if not os.path.isfile(file_path):
                print(f"The object `{filename}` is not a file.\n")
                continue
            extension = filename.split(".")[-1].upper()
            if extension not in self.FILE_CLASSES.keys():
                print(
                    (
                        f"The object `{filename}` can not be used because it is not a file which allowed."
                        f" Only allowed extensions are {', '.join(self.FILE_CLASSES.keys())}\n"
                    )
                )
                continue
            file = self.FILE_CLASSES[extension](file_path)
            files.append(file)
        return files

    def get_gstins(self, file: BaseFile) -> None:
        file_df = file.read()
        gstin_column = next((col for col in file_df.columns if col.lower() == "gstin"), None)
        if gstin_column:
            gstins = file_df[gstin_column].tolist()
            return gstins
        print("Column 'gstin' does not exist.")
        raise ValidationError("Column 'gstin' does not exist.")

    def generate_output_file_path(self, file_name):
        base_name = os.path.basename(file_name)
        base, extension = os.path.splitext(base_name)
        return os.path.join(self.directory_path, "output", f"{base}_output{extension}")

    def generate_output_file(self, file: BaseFile) -> None:
        gstins = self.get_gstins(file)
        output_file_path = self.generate_output_file_path(file.file_path)
        data = []
        for gstin in gstins:
            tax_payer_response = self.api_service.call_taxpayer_endpoint(gstin)
            tax_filing_response = self.api_service.call_tax_filing_status_endpoint(gstin)
            tax_payer_data = tax_payer_response.json()["data"]
            filing_data = tax_filing_response.json()["data"]["filing_data"]
            row_data = self.get_row_data(tax_payer_data, filing_data)
            print(row_data)
            data.append(row_data)
        df = pd.DataFrame(data)
        df.to_excel(output_file_path, index=False)

    def get_row_data(self, tax_payer_data: dict, tax_filing_data: dict) -> dict:
        filing_data = self.get_filing_data(tax_filing_data)
        row_data = {
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
        print(f"{tax_payer_data['gstin']}\n")
        return row_data

    def get_filing_data(self, data):
        return next((entry for entry in data if entry["return_period"] == self.filing_period), {
            "return_period": self.filing_period, "gstr1": "-", "gstr3b": "-"
        })
