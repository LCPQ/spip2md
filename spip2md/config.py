# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# pyright: strict
from os.path import expanduser, isfile
from typing import Optional

from yaml import Loader, load

CONFIG_PATHS = ("spip2md.yml", "spip2md.yaml")


def config_file() -> Optional[str]:
    for path in CONFIG_PATHS:
        if isfile(path):
            return path


class Configuration:
    db: str = "spip"  # DB name
    db_host: str = "localhost"  # Where is the DB
    db_user: str = "spip"  # A DB user with read access to SPIP database
    db_pass: str = "password"  # Password of db_user
    export_languages = ("fr", "en")  # Languages that will be exported
    storage_language: Optional[str] = "fr"  # Language of files and directories names
    data_dir: str = "IMG/"  # The directory in which SPIP images & documents are stored
    output_dir: str = "output/"  # The directory to which DB will be exported
    prepend_h1: bool = False  # Add the title of the article as a Markdown h1
    prepend_id: bool = False  # Add the ID of object before slug
    prepend_lang: bool = False  # Add the lang of object before slug
    export_drafts: bool = True  # Should we export drafts as draft:true articles
    remove_html: bool = True  # Should spip2md remove every HTML tags
    unknown_char_replacement: str = "??"  # Replaces unknown characters
    clear_log: bool = True  # Clear log before every run instead of appending to
    clear_output: bool = True  # Remove eventual output dir before running
    logfile: str = "log-spip2md.log"  # File where logs will be written, relative to wd
    loglevel: str = "WARNING"  # Minimum criticity of logs written in logfile
    logname: str = "spip2md"  # Labelling of logs
    export_filetype: str = "md"  # Extension of exported text files
    max_articles_export: int = 1000  # TODO reimplement
    max_sections_export: int = 500  # TODO reimplement

    def __init__(self, config_file: Optional[str] = None):
        if config_file is not None:
            # Read config from config file
            with open(config_file) as f:
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


CFG = Configuration(config_file=config_file())
