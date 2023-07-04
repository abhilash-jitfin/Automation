import re
from typing import List


def camel_case_to_sentence(input_string: str) -> str:
    """
    Converts a camel case string to sentence format.

    Args:
        input_string (str): The input string in camel case format.

    Returns:
        str: The formatted string in sentence format.
    """
    splits: List[str] = re.findall(r"[A-Z][^A-Z]*", input_string)
    formatted_splits: List[str] = [word.lower() if i else word.capitalize() for i, word in enumerate(splits)]
    formatted_string: str = " ".join(formatted_splits)
    return formatted_string
