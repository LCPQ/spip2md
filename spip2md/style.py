# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# Define styles for terminal printing
BOLD = 1  # Bold
ITALIC = 3  # Italic
UNDER = 4  # Underline
# Define colors
RED = 91  # Red
GREEN = 92  # Green
YELLOW = 93  # Yellow
BLUE = 94  # Blue
MAGENTA = 95  # Magenta
CYAN = 96  # Cyan
WHITE = 97  # Clear White
# Style used for warnings
WARNING_STYLE = (BOLD, RED)


# Terminal escape sequence
def esc(*args: int) -> str:
    if len(args) == 0:
        params: str = "0;"  # Defaults to reset
    else:
        params: str = ""
    # Build a string from args, that will be stripped from its trailing ;
    for a in args:
        params += str(a) + ";"
    # Base terminal escape sequence that needs to be closed by "m"
    return "\033[" + params[:-1] + "m"
