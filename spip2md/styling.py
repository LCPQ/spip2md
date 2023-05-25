# pyright: strict
# Define styles
BOLD = 1  # Bold
ITALIC = 3  # Italic
UNDER = 4  # Underline
# Define colors
RED = 91  # Red
GREEN = 92  # Green
YELLOW = 93  # Yellow
BLUE = 94  # Blue
C0 = 95  # Color
C1 = 96  # Color
C2 = 96  # Color


# Print a stylized string, without trailing newline
def style(string: str, *args: int, end: str = "") -> None:
    esc = "\033["  # Terminal escape sequence, needs to be closed by "m"
    if len(args) == 0:
        params: str = "1;"  # Defaults to bold
    else:
        params: str = ""
    for a in args:
        params += str(a) + ";"
    print(esc + params[:-1] + "m" + string + esc + "0m", end=end)


# Print a string, highlighting every substring starting at start_stop[x][0] …
def highlight(string: str, *start_stop: tuple[int, int], end: str = "") -> None:
    previous_stop = 0
    for start, stop in start_stop:
        print(string[previous_stop:start], end="")
        style(string[start:stop], BOLD, RED)
        previous_stop = stop
    print(string[previous_stop:], end=end)


# Plural ?
def ss(nb: int) -> str:
    return "s" if nb > 1 else ""


# Indent with 2 spaces
def indent(nb: int = 1) -> None:
    for _ in range(nb):
        print("  ", end="")
