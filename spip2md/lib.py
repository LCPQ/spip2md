# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs, remove
from os.path import isfile
from shutil import rmtree

from spip2md.config import CFG
from spip2md.extended_models import Section
from spip2md.spip_models import DB
from spip2md.style import BOLD, esc

# Define parent ID of level 0 sections
ROOTID = 0


# Write the level 0 sections and their subtrees
def write_root_tree(parent_dir: str) -> list[str | list]:
    # Define dictionary output to diplay
    output: list[str | list] = []
    # Print starting message
    print(
        f"""\
Begin exporting {esc(BOLD)}{CFG.db}@{CFG.db_host}{esc()} SPIP database to plain \
Markdown+YAML files,
into the directory {esc(BOLD)}{parent_dir}{esc()}, \
as database user {esc(BOLD)}{CFG.db_user}{esc()}
"""
    )
    # Get all sections of parentID ROOTID
    child_sections: tuple[Section, ...] = (
        Section.select()
        .where(Section.id_parent == ROOTID)
        .order_by(Section.date.desc())
    )
    nb: int = len(child_sections)
    # Write each subsections (write their entire subtree)
    for i, s in enumerate(child_sections):
        s._parentdir = CFG.output_dir
        output.append(s.write_tree(i, nb))
        print()  # Break line between level 0 sections in output
    return output


# Count on outputted tree & print results if finished
def summarize(
    tree: list[str | list[str | list]],
    indent: str = "  ",
    depth: int = -1,
    branches: int = 1,
    leaves: int = 0,
) -> tuple[int, int]:
    for sub in tree:
        if type(sub) == list:
            branches, leaves = summarize(sub, indent, depth + 1, branches + 1, leaves)
        elif type(sub) == str:
            leaves += 1
    # End message only if it’s the root one
    if depth == -1:
        print(
            f"""\
Exported a total of {esc(BOLD)}{leaves}{esc()} Markdown files, \
stored into {esc(BOLD)}{branches}{esc()} directories"""
        )
        # Warn about issued warnings in log file
        if isfile(CFG.logfile):
            print(f"\nWarnings and informations in {esc(BOLD)}{CFG.logfile}{esc()}")
    return (branches, leaves)


# Clear the previous log file if needed, then configure logging
def init_logging(**kwargs) -> None:
    if CFG.clear_log and isfile(CFG.logfile):
        remove(CFG.logfile)

    logging.basicConfig(
        encoding="utf-8", filename=CFG.logfile, level=CFG.loglevel, **kwargs
    )

    # return logging.getLogger(CFG.logname)


# Clear the output dir if needed & create a new
def clear_output() -> None:
    if CFG.clear_output:
        rmtree(CFG.output_dir, True)
    makedirs(CFG.output_dir, exist_ok=True)


# When directly executed as a script
def cli():
    # def cli(*addargv: str):
    # import sys

    # argv: list[str] = sys.argv + list(addargv)

    # TODO Define max nb of sections/articles to export based on first CLI argument
    # if len(argv) >= 2:
    #     sections_export = int(argv[1])
    # else:
    #     sections_export = CFG.max_sections_export

    init_logging()  # Initialize logging and logfile
    clear_output()  # Eventually remove already existing output dir

    # Connect to the MySQL database with Peewee ORM
    DB.init(CFG.db, host=CFG.db_host, user=CFG.db_user, password=CFG.db_pass)
    DB.connect()

    # Write everything while printing the output human-readably
    summarize(write_root_tree(CFG.output_dir))

    DB.close()  # Close the connection with the database
