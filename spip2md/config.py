# pyright: strict
from os.path import isfile
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
    output_dir: str = "output"
    max_articles_export: int = 1000
    max_sections_export: int = 500
    data_dir: str = "data"
    clear_output: bool = False

    def __init__(self, config_file: Optional[str] = None):
        if config_file is not None:
            with open(config_file) as f:
                config = load(f.read(), Loader=Loader)
            for attr in config:
                setattr(self, attr, config[attr])


config = Configuration(config_file())
