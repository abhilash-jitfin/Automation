import re
from typing import Optional
from ..utils.exceptions import ValidationError


def calculate_check_digit(gstin_without_check_digit: str) -> str:
    """
    Calculates the expected check digit for a given GSTIN string without the check digit.
    This function uses the Luhn Mod N algorithm, which is a generalization of the Luhn algorithm
    for non-decimal number systems (like Modulus 36 in this case).

    :param gstin_without_check_digit: A GSTIN string without the check digit.
    :return: The calculated check digit as a string.

    Example:
    --------
    >>> gstin = "27AAECS1234M1Z5"
    >>> gstin_without_check_digit = gstin[:-1]
    >>> check_digit = calculate_check_digit(gstin_without_check_digit)
    >>> check_digit
    '5'
    """
    factor = 1
    total = 0
    code_points = list(range(48, 58)) + list(range(65, 91))
    input_mod = len(code_points)

    for char in reversed(gstin_without_check_digit):
        digit = code_points.index(ord(char))
        factor = 1 if factor % 2 == 0 else 2
        sum_of_digits = sum(divmod(digit * factor, input_mod))
        total += sum_of_digits

    remainder = total % input_mod
    return chr(code_points[(input_mod - remainder) % input_mod])


def validate_gstin(gstin: str) -> Optional[str]:
    """
    Validates the provided GSTIN (Goods and Services Tax Identification Number) string by
    checking if it follows the correct format and if the check digit is correct.

    :param gstin: A GSTIN string to be validated.
    :return: The validated GSTIN string or raises ValidationError if the GSTIN is invalid.

    Example:
    --------
    >>> gstin = "27AAECS1234M1Z5"
    >>> valid_gstin = validate_gstin(gstin)
    >>> valid_gstin
    '27AAECS1234M1Z5'
    """
    if not isinstance(gstin, str):
        raise ValidationError(f"`{gstin}` should be a string!")
    gstin = gstin.strip()
    pattern = r'^[0-9]{2}[A-Za-z]{5}\d{4}[A-Za-z]{1}[0-9A-Za-z]{1}[Zz]{1}[0-9A-Za-z]{1}$'

    if not re.match(pattern, gstin):
        raise ValidationError(f"`{gstin}` is an invalid GSTIN!")

    gstin_without_check_digit = gstin[:-1]
    expected_check_digit = calculate_check_digit(gstin_without_check_digit)

    if gstin[-1] != expected_check_digit:
        raise ValidationError(f"`{gstin}` has an invalid check digit!")

    return gstin


def is_gstin_valid(gstin: str) -> bool:
    """
    Returns True if the given gstin string is a valid gstin.
    Otherwise, returns False.

    :param gstin: A string representing a gstin.
    :return: True if the gstin is valid, otherwise False.
    """
    try:
        validate_gstin(gstin)
    except ValidationError:
        return False
    return True
