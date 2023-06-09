from art import *
import importlib
import inspect
import pkgutil
import time

import requests
import tasks

from scripts.tasks.abstract_task import BaseTask
from scripts.utils.api_calls import SimpleRequests
from scripts.utils.settings import generate_token, load_settings, save_settings
from scripts.utils.strings import camel_case_to_sentence
from scripts.utils.terminal import COLOURS, format_text


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
        print(f"{i}. {camel_case_to_sentence(task_name)} - {task_class.description}")
    print(f"{len(task_modules) + 1}. Exit")
    print("-" * 40 + "\n")


def get_user_choice(task_modules):
    while True:
        try:
            choice = int(input(f"Choose a task number or {len(task_modules) + 1} to Exit: ")) - 1
            print()
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


def print_heading():
    space = " "
    heading = text2art(f'{space*20} Automation Tasks {space*20}')
    print('\n')
    print(f"{format_text(heading, color=COLOURS['cyan'], bold=True)}")


def main():
    settings = load_settings()
    task_modules = load_tasks()
    print_heading()
    if not settings.get('token'):
        settings['token'] = generate_token()  # Generate the token before displaying the menu
        save_settings(settings)
    while True:
        display_menu(task_modules)
        choice = get_user_choice(task_modules)
        if choice == len(task_modules):  # If the choice is "Exit"
            break
        run_task(task_modules, choice)


if __name__ == "__main__":
    main()
