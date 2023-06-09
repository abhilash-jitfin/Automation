BOLD = "\033[1m"
RESET = "\033[0m"

COLOURS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

def format_text(input: str, colour: str = None, bold: bool = False) -> str:
    colour_code = COLOURS.get(colour, "")
    bold_code = BOLD if bold else ""
    return f"{bold_code}{colour_code}{input}{RESET}"
