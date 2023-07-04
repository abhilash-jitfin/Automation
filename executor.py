import importlib
import inspect
import pkgutil

from art import text2art

from scripts.tasks.abstract_task import BaseTask
from scripts.utils.api_calls import Env
from scripts.utils.settings import generate_token, load_settings, save_settings
from scripts.utils.strings import camel_case_to_sentence
from scripts.utils.terminal import COLOUR_ORANGE, format_text, get_clean_input


def load_tasks():
    task_modules = {}
    task_module_names = [name for _, name, _ in pkgutil.iter_modules(["scripts/tasks"])]
    for modname in task_module_names:
        module = importlib.import_module(f"scripts.tasks.{modname}")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseTask) and obj != BaseTask:
                task_modules[name] = obj
    return task_modules


def display_menu(task_modules):
    print("\n" + "-" * 40)
    print("       TASK SELECTION MENU")
    print("-" * 40)
    for i, (task_name, task_class) in enumerate(task_modules.items(), start=1):
        print(f"{i}. {camel_case_to_sentence(task_name)} - {task_class.description}")
    print(f"{len(task_modules) + 1}. Exit")
    print("-" * 40 + "\n")


def get_user_choice(task_modules):
    while True:
        try:
            choice = get_clean_input(f"Choose a task number or {len(task_modules) + 1} to Exit: ", int) - 1
            print()
            if choice < 0 or choice > len(task_modules):
                raise ValueError("Invalid choice, please enter a number corresponding to the task.")
            return choice
        except ValueError as e:
            print(f"{e}\n")


def run_task(task_modules, choice):
    task_name = list(task_modules.keys())[choice]
    task_class = task_modules[task_name]
    task = task_class()
    task.get_params()
    task.execute()


def print_heading():
    space = " "
    heading = text2art(f"{space*20} Automation Tasks {space*20}")
    fromated_heading = format_text(heading, colour=COLOUR_ORANGE, bold=True)
    print("\n")
    print(fromated_heading)


def get_environment():
    envs = [env for env in Env]
    print("\nSelect Environment:")
    for i, env in enumerate(envs, start=1):
        print(f"{i}. {env.name}")

    while True:
        try:
            print("\n")
            choice = int(input(f"Enter the number corresponding to the environment (1-{len(envs)}): "))
            if 1 <= choice <= len(envs):
                return envs[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.\n")
        except ValueError:
            print("Invalid input. Please enter a number.\n")


def main():
    settings = load_settings()
    task_modules = load_tasks()
    print_heading()

    # Always ask the user to select an environment
    env = get_environment()
    settings["environment"] = env.value

    # Save the settings
    save_settings(settings)

    # Generate token if not already present in settings
    if not settings.get(env.value, {}).get("token"):
        # Assuming you have defined generate_token elsewhere
        token = generate_token(env)
        settings.setdefault(env.value, {})["token"] = token
        save_settings(settings)

    while True:
        display_menu(task_modules)
        choice = get_user_choice(task_modules)
        if choice == len(task_modules):  # If the choice is "Exit"
            break
        run_task(task_modules, choice)


if __name__ == "__main__":
    main()
