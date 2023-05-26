# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# Top level functions
import sys
from os import makedirs
from shutil import rmtree
from typing import Any

from peewee import ModelSelect

from spip2md.config import CFG
from spip2md.database import DB
from spip2md.spipobjects import RootRubrique, Rubrique

# Define styles
BOLD = 1  # Bold
ITALIC = 3  # Italic
UNDER = 4  # Underline
# Define colors
RED = 91  # Red
GREEN = 92  # Green
YELLOW = 93  # Yellow
BLUE = 94  # Blue
C0 = 95  # Color
C1 = 96  # Color
C2 = 96  # Color


# Print a stylized string, without trailing newline
def style(string: str, *args: int, end: str = "") -> None:
    esc = "\033["  # Terminal escape sequence, needs to be closed by "m"
    if len(args) == 0:
        params: str = "1;"  # Defaults to bold
    else:
        params: str = ""
    for a in args:
        params += str(a) + ";"
    print(esc + params[:-1] + "m" + string + esc + "0m", end=end)


# Print a string, highlighting every substring starting at start_stop[x][0] …
def highlight(string: str, *start_stop: tuple[int, int], end: str = "") -> None:
    previous_stop = 0
    for start, stop in start_stop:
        print(string[previous_stop:start], end="")
        style(string[start:stop], BOLD, RED)
        previous_stop = stop
    print(string[previous_stop:], end=end)


# Query the DB to retrieve all sections without parent, sorted by publication date
def root_sections(limit: int = 10**3) -> ModelSelect:
    return (
        Rubrique.select()
        .where(Rubrique.id_parent == 0)
        .order_by(Rubrique.date.desc())
        .limit(limit)
    )


r"""
# Print the detected unknown chars in article in their context but highlighted
def warn_unknown_chars(article: Article) -> None:
    # Print the title of the article in which there is unknown characters
    # & the number of them
    unknown_chars_apparitions: list[str] = unknown_chars_context(article.texte)
    nb: int = len(unknown_chars_apparitions)
    s: str = "s" if nb > 1 else ""
    style(f"{nb}")
    print(f" unknown character{s} in", end="")
    style(f" {article.lang} ")
    highlight(article.titre, *unknown_chars(article.titre))
    print()  # Break line
    # Print the context in which the unknown characters are found
    for text in unknown_chars_apparitions:
        style("  … ")
        highlight(text, *unknown_chars(text))
        style(" … \n")
    print()  # Break line
"""


# Print one root section list output correctly
# sys.setrecursionlimit(2000)
def print_output(
    tree: list[Any],
    indent: str = "  ",
    depth: int = 0,
    branches: int = 1,
    leaves: int = 0,
) -> tuple[int, int]:
    for sub in tree:
        if type(sub) == list:
            branches, leaves = print_output(
                sub, indent, depth + 1, branches + 1, leaves
            )
        else:
            leaves += 1
            print(indent * depth + sub)
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

    # Get the virtual id=0 section
    root: Rubrique = RootRubrique()

    # Write everything & print the output human-readably
    sections, articles = print_output(root.write_tree(CFG.output_dir))
    # End, summary message
    print(f"Exported a total of {sections} sections, containing {articles} articles")

    # print()  # Break line between export & unknown characters warning
    # Warn about each article that contains unknown(s) character(s)
    # TODO do it with Python warnings

    DB.close()  # Close the connection with the database
