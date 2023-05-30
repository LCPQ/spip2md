# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import sys
from os import makedirs, remove
from shutil import rmtree

from spip2md.config import CFG
from spip2md.database import DB
from spip2md.spipobjects import RootRubrique, Rubrique
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


# Connect to the MySQL database with Peewee ORM
DB.init(CFG.db, host=CFG.db_host, user=CFG.db_user, password=CFG.db_pass)
DB.connect()


# Main loop to execute only if script is directly executed
def main(*argv):
    # Allow main to get args when directly executed
    if len(argv) == 0:
        argv = sys.argv

    # TODO Define max nb of sections to export based on first CLI argument
    # if len(argv) >= 2:
    #     sections_export = int(argv[1])
    # else:
    #     sections_export = CFG.max_sections_export

    # Clear the output dir & create a new
    if CFG.clear_output:
        rmtree(CFG.output_dir, True)
    makedirs(CFG.output_dir, exist_ok=True)
    # Clear the log file
    # if CFG.clear_log:
    #     remove(CFG.logfile)

    # Get the virtual id=0 section
    root: Rubrique = RootRubrique()

    # Write everything while printing the output human-readably
    branches, leaves = count_output(root.write_tree(CFG.output_dir))

    DB.close()  # Close the connection with the database

    print(  # End, summary message
        f"""\
Exported a total of {esc(BOLD)}{leaves}{esc()} Markdown files, \
stored into {esc(BOLD)}{branches}{esc()} directories"""
    )

    # Warn about issued warnings in log file
    print(f"\nThere might be warnings in {esc(BOLD)}{CFG.logfile}{esc()}")
