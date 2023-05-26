import tasks
import pkgutil
import inspect
from tasks.base import BaseTask

def main():
    # Load all tasks in the tasks package
    tasks = {}
    for importer, modname, ispkg in pkgutil.iter_modules(tasks.__path__):
        module = importer.find_module(modname).load_module(modname)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseTask) and obj != BaseTask:
                tasks[name] = obj

    # Print a menu of all tasks
    for i, task_name in enumerate(tasks, start=1):
        print(f"{i}. {task_name}")

    # Get the user's choice
    choice = int(input("Choose a task: ")) - 1

    # Run the chosen task
    task_name = list(tasks.keys())[choice]
    task_class = tasks[task_name]
    task = task_class()
    task.get_params()
    task.run()

if __name__ == "__main__":
    main()
