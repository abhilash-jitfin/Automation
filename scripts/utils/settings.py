import json
import os
import time

from .api_calls import ApiConstants, SimpleRequests

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)


def generate_token():
    simple_requests = SimpleRequests.get_instance()

    MAX_ATTEMPTS = 3

    phone_number = input("Enter your mobile number: ")
    for attempt in range(MAX_ATTEMPTS):
        try:
            simple_requests.post(ApiConstants.OTP_ENDPOINT, data={"phone_number": phone_number})
            while True:
                otp = input("Enter the OTP received on your mobile (or type 'resend' to generate a new OTP): ")
                if otp.lower() == "resend":
                    break
                elif otp.isdigit():
                    response = simple_requests.post(
                        ApiConstants.VALIDATE_ENDPOINT, data={"phone_number": phone_number, "otp": otp}
                    )
                    token = response.json().get("data", {}).get("token")
                    if token:
                        print("Token generated successfully.")
                        return token
                else:
                    print("Invalid input. Please enter a numeric OTP or 'resend' to generate a new OTP.")
        except requests.exceptions.RequestException as e:
            print(f"\nAttempt {attempt + 1} failed. Error: {e}")
            time.sleep(1)  # Wait for a second before retrying

    print("\nMaximum attempts exceeded. Exiting the program.")
    exit(1)
