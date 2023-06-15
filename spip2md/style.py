"""
This file is part of spip2md.
Copyright (C) 2023 LCPQ/Guilhem Fauré

spip2md is free software: you can redistribute it and/or modify it under the terms of
the GNU General Public License version 2 as published by the Free Software Foundation.

spip2md is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with spip2md.
If not, see <https://www.gnu.org/licenses/>.
"""
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
