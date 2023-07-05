import os
import shutil


def create_directory_if_not_exists(directory_path):
    """
    This function creates a directory if it does not exist.

    Args:
        directory_path (str): The path of the directory to create.

    Returns:
        None
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def is_valid_directory_path(path):
    if os.path.isdir(path):
        return True
    if os.path.isfile(path):
        return False
    return False


def move_file_to_destination_dir(source_file_path: str, destination_dir: str, can_overwrite: bool = False) -> None:
    if not os.path.isfile(source_file_path):
        raise FileNotFoundError(f"The specified path '{source_file_path}' is not a valid file path.")
    destination_file_path = os.path.join(destination_dir, os.path.basename(source_file_path))
    if os.path.exists(destination_file_path) and can_overwrite:
        os.remove(destination_file_path)
    try:
        shutil.move(source_file_path, destination_file_path)
    except shutil.Error as e:
        print(f"{str(e)}\n")
