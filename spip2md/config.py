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
# pyright: strict
from os import environ
from os.path import expanduser, isfile
from typing import Optional

from yaml import Loader, load


# Global configuration object
class Configuration:
    # config_file: Optional[str] = None  # Location of the config file

    name: str = "spip2md"  # Name of program, notably used in logs

    db: str = "spip"  # DB name
    db_host: str = "localhost"  # Where is the DB
    db_user: str = "spip"  # A DB user with read access to SPIP database
    db_pass: str = "password"  # Password of db_user
    data_dir: str = "IMG/"  # The directory in which SPIP images & documents are stored
    export_languages = ("fr", "en")  # Languages that will be exported
    storage_language: Optional[str] = "fr"  # Language of files and directories names
    output_dir: str = "output/"  # The directory to which DB will be exported
    prepend_h1: bool = False  # Add the title of the article as a Markdown h1
    move_fields: list[dict[str, str]] = []  # Alternative destination for fields
    prepend_id: bool = False  # Add the ID of object before slug
    prepend_lang: bool = False  # Add the lang of object before slug
    export_drafts: bool = True  # Should we export drafts as draft:true articles
    export_empty: bool = True  # Should we export empty articles
    remove_html: bool = True  # Should spip2md remove every HTML tags
    metadata_markup: bool = False  # Should spip2md keep the markup in metadata fields
    title_max_length: int = 40  # Maximum length of a single title for directory names
    unknown_char_replacement: str = "??"  # Replaces unknown characters
    clear_log: bool = True  # Clear log before every run instead of appending to
    clear_output: bool = True  # Remove eventual output dir before running
    ignore_patterns: list[str] = []  # Ignore objects of which title match
    export_filetype: str = "md"  # Extension of exported text files

    debug: bool = False  # Enable debug mode

    # Searches for a configuration file from standard locations or params
    def _find_config_file(self, *start_locations: str) -> str:
        # Search for config files in function params first
        config_locations: list[str] = list(start_locations)

        if "XDG_CONFIG_HOME" in environ:
            config_locations += [
                environ["XDG_CONFIG_HOME"] + "/spip2md.yml",
                environ["XDG_CONFIG_HOME"] + "/spip2md.yaml",
            ]

        if "HOME" in environ:
            config_locations += [
                environ["HOME"] + "/.config/spip2md.yml",
                environ["HOME"] + "/.config/spip2md.yaml",
                environ["HOME"] + "/spip2md.yml",
                environ["HOME"] + "/spip2md.yaml",
            ]

        # Search in working directory in last resort
        config_locations += [
            "/spip2md.yml",
            "/spip2md.yaml",
        ]

        # Return the first path that actually exists
        for path in config_locations:
            if isfile(path):
                # self.config_file = path
                return path
        # If not found, raise error
        raise FileNotFoundError

    def __init__(self, *argv: str):
        try:
            # Read config from config file
            with open(self._find_config_file(*argv[1:])) as f:
                # Tell user about config
                print(f"Read configuration file from {f.name}")
                config = load(f.read(), Loader=Loader)
            # Assign configuration for each attribute in config file
            for attr in config:
                # If attribute is a dir, ensure that ~ is converted to home path
                if "dir" in attr:
                    directory = expanduser(config[attr])
                    # Ensure that directory ends with a slash
                    directory = directory if directory[:-1] == "/" else directory + "/"
                    setattr(self, attr, directory)
                else:
                    setattr(self, attr, config[attr])
        except FileNotFoundError:
            print("No configuration file found, using defaults")
