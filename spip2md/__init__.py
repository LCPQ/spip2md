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


This file main purpose is to initialise the logging infrastructure of Python.
As the __init__.py file, this file is executed whenever the package is imported.
"""
# pyright: strict
import logging
from os.path import isfile

LOGFILE: str = "log-spip2md.log"  # File where logs will be written, relative to wd
LOGLEVEL: str = "WARNING"  # Minimum criticity of logs written in logfile
# Configure logging
# __import__("os").remove(LOGFILE) # Clear log ?
if isfile(LOGFILE):  # Break 2 lines before new log if there’s already one
    with open(LOGFILE, "a") as f:
        f.write("\n\n")
logging.basicConfig(encoding="utf-8", filename=LOGFILE, level=LOGLEVEL)  # Init
