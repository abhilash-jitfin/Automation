BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
RESET = "\033[0m"

COLOUR_RED = "red"
COLOUR_BLUE = "blue"
COLOUR_CYAN = "cyan"
COLOUR_GREEN = "green"
COLOUR_WHITE = "white"
COLOUR_YELLOW = "yellow"
COLOUR_ORANGE = "orange"
COLOUR_MAGENTA = "magenta"

COLOURS = {
    COLOUR_RED: "\033[31m",
    COLOUR_BLUE: "\033[34m",
    COLOUR_CYAN: "\033[36m",
    COLOUR_GREEN: "\033[32m",
    COLOUR_WHITE: "\033[37m",
    COLOUR_YELLOW: "\033[33m",
    COLOUR_ORANGE: "\033[38;5;208m",
    COLOUR_MAGENTA: "\033[35m",
}


def format_text(
    input: str, colour: str = None, bold: bool = False, underline: bool = False, blink: bool = False
) -> str:
    colour_code = COLOURS.get(colour, "")
    bold_code = BOLD if bold else ""
    underline_code = UNDERLINE if underline else ""
    blink_code = BLINK if blink else ""
    return f"{bold_code}{underline_code}{blink_code}{colour_code}{input}{RESET}"


def get_clean_input(prompt: str, input_type: type = str) -> any:
    """
    Prompt the user for input and return the cleaned value.

    :param prompt: str - The prompt to display to the user.
    :param input_type: type - The type to cast the input to. Default is str.
    :return: any - The user's input, stripped of whitespace and cast to input_type.

    Note: ValueError is not handled in this function. The caller is responsible for handling it.
    """
    return input_type(input(prompt).strip())
