# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# Top level functions
import sys
from os import makedirs
from shutil import rmtree

from spip2md.config import CFG
from spip2md.database import DB
from spip2md.regexmap import SPECIAL_OUTPUT
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


# Terminal escape sequence
def esc(*args: int) -> str:
    if len(args) == 0:
        params: str = "0;"  # Defaults to reset
    else:
        params: str = ""
    # Build a string from args, that will be stripped from its trailing ;
    for a in args:
        params += str(a) + ";"
    # Base terminal escape sequence that needs to be closed by "m"
    return "\033[" + params[:-1] + "m"


# Print one root section list output correctly
# sys.setrecursionlimit(2000)
def print_output(
    tree: list[str | list[str | list]],
    indent: str = "  ",
    depth: int = -1,
    branches: int = 1,
    leaves: int = 0,
) -> tuple[int, int]:
    for sub in tree:
        if type(sub) == list:
            branches, leaves = print_output(
                sub, indent, depth + 1, branches + 1, leaves
            )
        elif type(sub) == str:
            leaves += 1
            # Highlight special elements (in red for the moment)
            for elmnt in SPECIAL_OUTPUT:
                sub = elmnt.sub(esc(BOLD, GREEN) + r"\1" + esc(), sub)
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
    branches, leaves = print_output(root.write_tree(CFG.output_dir))
    # End, summary message
    print(
        f"""
Exported a total of {leaves} Markdown files, stored into {branches} directories"""
    )

    # print()  # Break line between export & unknown characters warning
    # Warn about each article that contains unknown(s) character(s)
    # TODO do it with Python warnings

    DB.close()  # Close the connection with the database


r""" OLD CODE
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

# Return a list of tuples giving the start and end of unknown substring in text
def unknown_chars(text: str) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for char in UNKNOWN_ISO:
        for match in finditer("(" + char + ")+", text):
            positions.append((match.start(), match.end()))
    return positions

# Return strings with unknown chards found in text, surrounded by context_length chars
def unknown_chars_context(text: str, context_length: int = 24) -> list[str]:
    errors: list[str] = []
    context: str = r".{0," + str(context_length) + r"}"
    for char in UNKNOWN_ISO:
        matches = finditer(
            context + r"(?=" + char + r")" + char + context,
            text,
        )
        for match in matches:
            errors.append(match.group())
    return errors
"""
