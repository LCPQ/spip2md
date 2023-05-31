# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs, remove
from os.path import isfile
from shutil import rmtree

from spip2md.config import CFG
from spip2md.extended_models import RootRubrique
from spip2md.spip_models import DB
from spip2md.style import BOLD, esc


# Count on outputted tree
def count_output(
    tree: list[str | list[str | list]],
    indent: str = "  ",
    depth: int = -1,
    branches: int = 1,
    leaves: int = 0,
) -> tuple[int, int]:
    for sub in tree:
        if type(sub) == list:
            branches, leaves = count_output(
                sub, indent, depth + 1, branches + 1, leaves
            )
        elif type(sub) == str:
            leaves += 1
    return (branches, leaves)


# Clear the previous log file if needed, then configure logging
def init_logging() -> None:
    if CFG.clear_log and isfile(CFG.logfile):
        remove(CFG.logfile)
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        filename=CFG.logfile,
        encoding="utf-8",
        level=CFG.loglevel,
    )


# Summary message at the end of the program
def summary(branches: int, leaves: int) -> None:
    print(
        f"""\
Exported a total of {esc(BOLD)}{leaves}{esc()} Markdown files, \
stored into {esc(BOLD)}{branches}{esc()} directories"""
    )
    # Warn about issued warnings in log file
    if isfile(CFG.logfile):
        print(f"\nTake a look at warnings and infos in {esc(BOLD)}{CFG.logfile}{esc()}")


# Clear the output dir if needed & create a new
def clear_output() -> None:
    if CFG.clear_output:
        rmtree(CFG.output_dir, True)
    makedirs(CFG.output_dir, exist_ok=True)


# Define the virtual id=0 section
ROOT = RootRubrique()


# To execute when script is directly executed as a script
def cli():
    # def cli(*addargv: str):
    # import sys

    # argv: list[str] = sys.argv + list(addargv)

    # TODO Define max nb of sections/articles to export based on first CLI argument
    # if len(argv) >= 2:
    #     sections_export = int(argv[1])
    # else:
    #     sections_export = CFG.max_sections_export

    init_logging()
    clear_output()

    # Connect to the MySQL database with Peewee ORM
    DB.init(CFG.db, host=CFG.db_host, user=CFG.db_user, password=CFG.db_pass)
    DB.connect()

    # Write everything while printing the output human-readably
    summary(*count_output(ROOT.write_tree(CFG.output_dir)))

    DB.close()  # Close the connection with the database
