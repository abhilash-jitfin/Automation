import os
import pandas as pd
from datetime import datetime

from ..utils.api_calls import SimpleRequests, ApiConstants
from ..utils.settings import load_settings
from .abstract_task import BaseTask


class TaxPayerDetailsTask(BaseTask):
    description = "Task to get taxpayer details for GSTINs"

    def __init__(self, token=None):
        self.simple_requests = SimpleRequests.get_instance(token)
        self.settings = load_settings()
        if self.simple_requests.headers.get('Authorization') is None:
            self.simple_requests.set_token(self.settings.get('token'))
        self.file_path = None
        self.output_fields = [
            'date_of_cancellation',
            'last_updated_date',
            'registration_date',
            'state_jurisdiction_code',
            'business_type',
            'legal_name',
            'state_jurisdiction',
            'addresses',
            'gstin',
            'nature_of_business_activities',
            'constitution_of_business',
            'principal_place_of_business',
            'commissionerate_code',
            'trade_name',
            'status',
            'is_gstin_inactive',
            'commissionerate',
            'tax_payer_updated_at',
            'registration_date_formatted',
            'primary_address',
            'other_addresses'
        ]

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.input_file = input("\nEnter the path to the file containing GSTINs: ")
        print("\n")

    def execute(self) -> None:
        """Execute the task."""
        gstins = self.read_gstins_from_file()
        if not gstins:
            print("No GSTINs found in the input file.")
            return

        self.file_path = self.generate_output_file_path()

        try:
            taxpayer_details = self.get_taxpayer_details(gstins)
            if taxpayer_details:
                self.write_taxpayer_details_to_file(taxpayer_details)
            else:
                print("Failed to get taxpayer details.")
        except Exception as e:
            print(f"Failed to get taxpayer details. Error: {e}")

    def read_gstins_from_file(self) -> list:
        """Read GSTINs from the input file."""
        try:
            ext = os.path.splitext(self.input_file)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(self.input_file, header=None)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(self.input_file, header=None)
            else:
                raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")

            gstins = df[0].tolist()  # Assuming the GSTINs are in the first column
            return gstins
        except FileNotFoundError:
            print("Input file not found.")
        except Exception as e:
            print(f"Failed to read GSTINs from the input file. Error: {e}")

        return []

    def get_taxpayer_details(self, gstins: list):
        """Get taxpayer details for the given GSTINs."""
        taxpayer_details = {}

        for i, gstin in enumerate(gstins, start=1):
            try:
                response = self.simple_requests.get(f"{ApiConstants.TAX_PAYER_ENDPOINT}{gstin}")
                if response.json().get('success'):
                    data = response.json().get("data", {})
                    if data:
                        taxpayer_details[gstin] = self.extract_taxpayer_details(data)
                    else:
                        print(f"No details found for GSTIN: {gstin}")
                else:
                    print(f"Failed to get taxpayer details for GSTIN: {gstin}. Response status code: {response.status_code}")
            except Exception as e:
                print(f"Failed to get taxpayer details for GSTIN: {gstin}. Error: {e}")

        return taxpayer_details

    def extract_taxpayer_details(self, data: dict) -> dict:
        """Extract taxpayer details from the data response."""
        details = {}

        # Extract the required details from the 'data' dictionary
        details['date_of_cancellation'] = data.get('date_of_cancellation')
        details['last_updated_date'] = data.get('last_updated_date')
        details['registration_date'] = data.get('registration_date')
        details['state_jurisdiction_code'] = data.get('state_jurisdiction_code')
        details['business_type'] = data.get('business_type')
        details['legal_name'] = data.get('legal_name')
        details['state_jurisdiction'] = data.get('state_jurisdiction')
        details['addresses'] = data.get('addresses')
        details['gstin'] = data.get('gstin')
        details['nature_of_business_activities'] = data.get('nature_of_business_activities')
        details['constitution_of_business'] = data.get('constitution_of_business')
        details['principal_place_of_business'] = data.get('principal_place_of_business')
        details['commissionerate_code'] = data.get('commissionerate_code')
        details['trade_name'] = data.get('trade_name')
        details['status'] = data.get('status')
        details['is_gstin_inactive'] = data.get('is_gstin_inactive')
        details['commissionerate'] = data.get('commissionerate')
        details['tax_payer_updated_at'] = data.get('tax_payer_updated_at')
        details['registration_date_formatted'] = data.get('registration_date_formatted')
        details['primary_address'] = data.get('primary_address')
        details['other_addresses'] = data.get('other_addresses')

        return details

    def generate_output_file_path(self) -> str:
        """Generate the output file path."""
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file_name = f"{base_name}_output_{timestamp}.xlsx"
        output_dir = os.path.dirname(self.input_file)
        output_file_path = os.path.join(output_dir, output_file_name)
        return output_file_path

    def write_taxpayer_details_to_file(self, taxpayer_details: dict):
        """Write taxpayer details to the output file."""
        try:
            output_file = self.file_path
            df = pd.DataFrame.from_dict(taxpayer_details, orient='index', columns=self.output_fields)
            df.to_excel(output_file, index=False)

            print("Taxpayer details written to the output file:", output_file)
        except Exception as e:
            print("Failed to write taxpayer details to the output file. Error:", e)
