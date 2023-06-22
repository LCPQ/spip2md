# File for test purposes, mainly in interactive python
from spip2md.config import Configuration
from spip2md.convert import (
    ConvertableSite,
)
from spip2md.spip_models import DB

cfg = Configuration()  # Get the configuration

DB.init(  # type: ignore
    cfg.db, host=cfg.db_host, user=cfg.db_user, password=cfg.db_pass
)

SITE = ConvertableSite(cfg)

ID = ("document", 1293)
