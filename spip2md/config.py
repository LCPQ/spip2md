# pyright: strict
from os.path import isfile

from yaml import CLoader as Loader
from yaml import load

configPaths = ("spip2md.yml", "spip2md.yaml")


class Configuration:
    db = "spip"
    dbHost = "localhost"
    dbUser = "spip"
    dbPass = "password"
    outputDir = "output"
    defaultNbToExport = 1000

    def __init__(self, configFile: str | None = None) -> None:
        if configFile != None:
            with open(configFile) as f:
                config = load(f.read(), Loader=Loader)
            if "db" in config:
                self.db = config["db"]
            if "dbUser" in config:
                self.dbUser = config["dbUser"]
            if "dbPass" in config:
                self.dbPass = config["dbPass"]
            if "outputDir" in config:
                self.outputDir = config["outputDir"]
            if "defaultNbToExport" in config:
                self.defaultNbToExport = config["defaultNbToExport"]


config = Configuration()

for path in configPaths:
    if isfile(path):
        config = Configuration(path)
        break
