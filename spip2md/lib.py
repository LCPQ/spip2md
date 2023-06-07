# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs, remove
from os.path import isfile
from shutil import rmtree
from typing import Optional

from spip2md.config import CFG
from spip2md.extended_models import (
    DeepDict,
    DontExportDraftError,
    LangNotFoundError,
    Section,
)
from spip2md.spip_models import DB
from spip2md.style import BOLD, esc

# Define loggers for this file
ROOTLOG = logging.getLogger(CFG.logname + ".root")
TREELOG = logging.getLogger(CFG.logname + ".tree")
# Initialize the database with settings from CFG
DB.init(CFG.db, host=CFG.db_host, user=CFG.db_user, password=CFG.db_pass)


# Write the root sections and their subtrees
def write_root(parent_dir: str, parent_id: int = 0) -> DeepDict:
    # Print starting message
    print(
        f"""\
Begin exporting {esc(BOLD)}{CFG.db}@{CFG.db_host}{esc()} SPIP database to plain \
Markdown+YAML files,
into the directory {esc(BOLD)}{parent_dir}{esc()}, \
as database user {esc(BOLD)}{CFG.db_user}{esc()}
"""
    )
    output: DeepDict = {"sections": []}  # Define dictionary output
    # Write each sections (write their entire subtree) for each export language
    # Language specified in database can differ from markup, se we force a language
    #   and remove irrelevant ones at each looping
    for lang in CFG.export_languages:
        ROOTLOG.debug("Initialize root sections")
        # Get all sections of parentID ROOTID
        child_sections: tuple[Section, ...] = (
            Section.select()
            .where(Section.id_parent == parent_id)
            .order_by(Section.date.desc())
        )
        nb: int = len(child_sections)
        for i, s in enumerate(child_sections):
            buffer: list[DeepDict] = []
            ROOTLOG.debug(f"Begin exporting {lang} root section {i}/{nb}")
            try:
                buffer.append(s.write_all(-1, CFG.output_dir, i, nb, lang))
            except LangNotFoundError as err:
                ROOTLOG.debug(err)  # Log the message
            except DontExportDraftError as err:  # Will happen in not CFG.export_drafts
                ROOTLOG.debug(err)  # Log the message
            print()  # Break line between level 0 sections in output
            ROOTLOG.debug(f"Finished exporting {lang} root section {i}/{nb} {s._title}")
            output["sections"] = buffer
    return output


# Count on outputted tree & print results if finished
def summarize(
    tree: DeepDict | list[DeepDict] | list[str],
    depth: int = -1,
    prevkey: Optional[str] = None,
    counter: Optional[dict[str, int]] = None,
) -> dict[str, int]:
    if counter is None:
        counter = {}
        # __import__("pprint").pprint(tree)  # DEBUG
    if type(tree) == dict:
        for key, sub in tree.items():
            if type(sub) == list:
                counter = summarize(sub, depth + 1, key, counter)
            # if type of sub is str, it’s just the name, don’t count
    if type(tree) == list:
        for sub in tree:
            if prevkey is not None:
                if prevkey not in counter:
                    counter[prevkey] = 0
                counter[prevkey] += 1
            if type(sub) == dict:
                counter = summarize(sub, depth + 1, None, counter)

    # End message only if it’s the root one
    if depth == -1:
        TREELOG.debug(tree)
        totals: str = ""
        for key, val in counter.items():
            totals += f"{esc(BOLD)}{val}{esc()} {key}, "
        print(f"Exported a total of {totals[:-2]}")
        # Warn about issued warnings in log file
        if isfile(CFG.logfile):
            print(
                f"Logging level was set to {esc(BOLD)}{CFG.loglevel}{esc()}, there are"
                + f" warnings and informations in {esc(BOLD)}{CFG.logfile}{esc()}"
            )
    return counter


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


# def main(*addargv: str):
# import sys
# argv: list[str] = sys.argv + list(addargv)

# TODO Define max nb of sections/articles to export based on first CLI argument
# if len(argv) >= 2:
#     sections_export = int(argv[1])
# else:
#     sections_export = CFG.max_sections_export


# When directly executed as a script
def cli():
    init_logging()  # Initialize logging and logfile
    clear_output()  # Eventually remove already existing output dir

    with DB:  # Connect to the database where SPIP site is stored in this block
        # Write everything while printing the output human-readably
        summarize(write_root(CFG.output_dir))
