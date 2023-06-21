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


This file contains functions needed to control this package from command line and to
define a printable classes which adds terminal printing capabilites to Spip objects
"""
# pyright: strict
import logging
from os import makedirs
from os.path import isfile
from shutil import rmtree
from typing import Any, Optional

from spip2md import LOGFILE, NAME
from spip2md.config import Configuration
from spip2md.spip_models import DB
from spip2md.write import WritableSite

LOG = logging.getLogger(NAME)  # Define a custom logger for spip2md

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


# Extend Site class to add terminal output capabilities
class PrintableSite(WritableSite):
    def write_all(self) -> None:
        pass


def main(*argv: str):
    cfg = Configuration(*argv)  # Get the configuration

    # Initialize the database with settings from CFG
    DB.init(cfg.db, host=cfg.db_host, user=cfg.db_user, password=cfg.db_pass)

    # Eventually remove already existing output dir
    if cfg.clear_output:
        rmtree(cfg.output_dir, True)
    makedirs(cfg.output_dir, exist_ok=True)

    with DB:  # Connect to the database where SPIP site is stored in this block
        # Write everything while printing the output human-readably
        PrintableSite(cfg).write_all()


# def summarize(
#     tree: dict[Any, Any] | list[Any],
#     depth: int = -1,
#     prevkey: Optional[str] = None,
#     counter: Optional[dict[str, int]] = None,
# ) -> dict[str, int]:
#     if counter is None:
#         counter = {}
#         # __import__("pprint").pprint(tree)  # DEBUG
#     if type(tree) == dict:
#         for key, sub in tree.items():
#             if type(sub) == list:
#                 counter = summarize(sub, depth + 1, key, counter)
#             # if type of sub is str, it’s just the name, don’t count
#     if type(tree) == list:
#         for sub in tree:
#             if prevkey is not None:
#                 if prevkey not in counter:
#                     counter[prevkey] = 0
#                 counter[prevkey] += 1
#             if type(sub) == dict:
#                 counter = summarize(sub, depth + 1, None, counter)
#
#     # End message only if it’s the root one
#     if depth == -1:
#         LOG.debug(tree)
#         totals: str = ""
#         for key, val in counter.items():
#             totals += f"{esc(BOLD)}{val}{esc()} {key}, "
#         print(f"Exported a total of {totals[:-2]}")
#         # Warn about issued warnings in log file
#         if isfile(LOGFILE):
#             print(f"Check out warnings and infos in {esc(BOLD)}{LOGFILE}{esc()}")
#     return counter
