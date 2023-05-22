# pyright: strict
from os.path import isfile
from typing import Optional

# from yaml import CLoader as Loader
from yaml import Loader, load

config_paths = ("spip2md.yml", "spip2md.yaml")


class Configuration:
    db = "spip"
    db_host = "localhost"
    db_user = "spip"
    db_pass = "password"
    output_dir = "output"
    default_export_max = 1000

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


config = Configuration()

for path in config_paths:
    if isfile(path):
        config = Configuration(path)
        break
