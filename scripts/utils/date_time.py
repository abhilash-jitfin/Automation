from datetime import datetime


def is_valid_period(period: str, format: str) -> bool:
    """
    Validate if the given period is in the correct format.

    Args:
        period: The period string to validate.
        format: The format to validate the period against.

    Returns:
        True if the period is in the correct format, False otherwise.
    """
    try:
        datetime.strptime(period, format)
    except ValueError:
        return False
    return True


def change_datetime_format(date_string: str, current_format: str, new_format: str) -> str:
    """
    Convert a date string from the current format to a new format.

    Args:
        date_string: The original date string.
        current_format: The current format of the date string.
        new_format: The new format to convert to.

    Returns:
        The date string in the new format.
    """
    datetime_obj = datetime.strptime(date_string, current_format)
    new_date_string = datetime_obj.strftime(new_format)
    return new_date_string
