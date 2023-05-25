# pyright: strict
from os.path import expanduser, isfile
from typing import Optional

from yaml import Loader, load

config_paths = ("spip2md.yml", "spip2md.yaml")


def config_file() -> Optional[str]:
    for path in config_paths:
        if isfile(path):
            return path


class Configuration:
    db: str = "spip"
    db_host: str = "localhost"
    db_user: str = "spip"
    db_pass: str = "password"
    output_dir: str = "output/"
    data_dir: str = "data/"
    clear_output: bool = False
    prepend_h1: bool = True
    export_filetype: str = "md"
    max_articles_export: int = 1000  # TODO reimplement with recursion
    max_sections_export: int = 500  # TODO reimplement with recursion

    def __init__(self, config_file: Optional[str] = None):
        if config_file is not None:
            # Read config from config file
            with open(config_file) as f:
                config = load(f.read(), Loader=Loader)
            # Assign configuration for each attribute in config file
            for attr in config:
                # If attribute is a dir, ensure that ~ is converted to home path
                if type(attr) == "string" and "dir" in attr:
                    directory = expanduser(config[attr])
                    # Ensure that directory ends with a slash
                    directory = (
                        directory if directory.last() == "/" else directory + "/"
                    )
                    setattr(self, attr, directory)
                setattr(self, attr, config[attr])


config = Configuration(config_file())
