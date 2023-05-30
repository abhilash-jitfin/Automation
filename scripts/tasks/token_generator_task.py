import time
import requests
from .abstract_task import BaseTask
from ..utils.api_calls import SimpleRequests


class TokenGeneratorTask(BaseTask):
    description = "Task to generate and validate OTP for token generation"
    MAX_ATTEMPTS = 3

    def __init__(self):
        self.base_url = "https://qa.appv2.kyss.ai/apis"
        self.simple_requests = SimpleRequests(self.base_url)

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.phone_number = input("\nEnter your mobile number: ")
        self.otp_endpoint = "/accounts/signin/otp"
        self.validate_endpoint = "/accounts/signin/otp/validate"

    def execute(self) -> None:
        """Execute the task."""
        attempts = 0
        while attempts < self.MAX_ATTEMPTS:
            try:
                self.send_otp()
                otp = self.get_otp_input()
                if otp is None:
                    continue
                self.validate_otp(otp)
                break
            except requests.exceptions.RequestException as e:
                print(f"\nAttempt {attempts + 1} failed. Error: {e}")
                attempts += 1
                self.wait_for_retry(attempts)

        if attempts == self.MAX_ATTEMPTS:
            print("\nMaximum attempts exceeded. Exiting the program.")
            exit(1)

    def send_otp(self) -> None:
        """Send OTP to the user's phone number."""
        self.simple_requests.post(self.otp_endpoint, data={"phone_number": self.phone_number})

    def get_otp_input(self) -> str:
        """Get OTP input from the user and handle 'resend' option."""
        while True:
            otp = input("Enter the OTP received on your mobile (or type 'resend' to generate a new OTP): ")
            if otp.lower() == 'resend':
                return None
            elif otp.isdigit():
                return otp
            else:
                print("Invalid input. Please enter a numeric OTP or 'resend' to generate a new OTP.")

    def validate_otp(self, otp: str) -> None:
        """Validate the OTP provided by the user."""
        response = self.simple_requests.post(self.validate_endpoint, data={"phone_number": self.phone_number, "otp": otp})
        token = response.get("token")
        if token:
            print("Token generated successfully.")
            # Store the token in a variable accessible by other tasks
            SimpleRequests.token = token

    @staticmethod
    def wait_for_retry(attempts: int) -> None:
        """Wait for a specific duration before the next retry attempt."""
        sleep_time = 2 ** attempts  # Exponential backoff
        time.sleep(sleep_time)
