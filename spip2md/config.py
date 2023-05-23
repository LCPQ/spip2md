# pyright: strict
from os.path import isfile
from typing import Optional

# from yaml import CLoader as Loader
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
    default_export_max: int = 1000
    data_dir: str = "data"
    clear_output: bool = False

    def __init__(self, config_file: Optional[str] = None) -> None:
        if config_file is not None:
            with open(config_file) as f:
                config = load(f.read(), Loader=Loader)
            if "db" in config:
                self.db = config["db"]
            if "db_user" in config:
                self.db_user = config["db_user"]
            if "db_pass" in config:
                self.db_pass = config["db_pass"]
            if "output_dir" in config:
                self.output_dir = config["output_dir"]
            if "default_export_nb" in config:
                self.default_export_max = config["default_export_max"]
            if "data_dir" in config:
                self.data_dir = config["data_dir"]
            if "clear_output" in config:
                self.clear_output = config["clear_output"]


config = Configuration(config_file())
