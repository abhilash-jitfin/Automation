import importlib
import inspect
import pkgutil
import time

import requests
import tasks

from scripts.tasks.abstract_task import BaseTask
from scripts.utils.api_calls import SimpleRequests


def load_tasks():
    task_modules = {}
    task_module_names = [name for _, name, _ in pkgutil.iter_modules(['scripts/tasks'])]
    for modname in task_module_names:
        module = importlib.import_module(f'scripts.tasks.{modname}')
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseTask) and obj != BaseTask:
                task_modules[name] = obj
    return task_modules


def display_menu(task_modules):
    print("\n" + "-" * 40)
    print("       TASK SELECTION MENU")
    print("-" * 40)
    for i, (task_name, task_class) in enumerate(task_modules.items(), start=1):
        print(f"{i}. {task_name} - {task_class.description}")
    print(f"{len(task_modules) + 1}. Exit")
    print("-" * 40 + "\n")


def get_user_choice(task_modules):
    while True:
        try:
            choice = int(input(f"Choose a task number or {len(task_modules) + 1} to Exit: ")) - 1
            if choice < 0 or choice > len(task_modules):
                raise ValueError("Invalid choice, please enter a number corresponding to the task.")
            return choice
        except ValueError as e:
            print(e)


def run_task(task_modules, choice):
    task_name = list(task_modules.keys())[choice]
    task_class = task_modules[task_name]
    task = task_class()
    task.get_params()
    task.execute()


def generate_token():
    simple_requests = SimpleRequests.get_instance()

    MAX_ATTEMPTS = 3

    phone_number = input("\nEnter your mobile number: ")
    # phone_number = "+919611412486"
    otp_endpoint = "/accounts/signin/otp"
    validate_endpoint = "/accounts/signin/otp/validate"

    for attempt in range(MAX_ATTEMPTS):
        try:
            simple_requests.post(otp_endpoint, data={"phone_number": phone_number})

            while True:
                otp = input(
                    "Enter the OTP received on your mobile (or type 'resend' to generate a new OTP): "
                )
                if otp.lower() == 'resend':
                    break
                elif otp.isdigit():
                    response = simple_requests.post(
                        validate_endpoint, data={"phone_number": phone_number, "otp": otp}
                    )
                    token = response.json().get('data', {}).get('token')
                    if token:
                        print("Token generated successfully.")
                        print(f"token - {token}")
                        simple_requests.set_token(token)
                        return token
                else:
                    print("Invalid input. Please enter a numeric OTP or 'resend' to generate a new OTP.")
        except requests.exceptions.RequestException as e:
            print(f"\nAttempt {attempt + 1} failed. Error: {e}")
            time.sleep(1)  # Wait for a second before retrying

    print("\nMaximum attempts exceeded. Exiting the program.")
    exit(1)


def main():
    generate_token()  # Generate the token before displaying the menu
    task_modules = load_tasks()
    while True:
        display_menu(task_modules)
        choice = get_user_choice(task_modules)
        if choice == len(task_modules):  # If the choice is "Exit"
            break
        run_task(task_modules, choice)


if __name__ == "__main__":
    main()
