# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
#!python
from os import makedirs
from shutil import rmtree
from sys import argv

from config import CFG
from converters import unknown_chars, unknown_chars_context
from database import DB
from peewee import ModelSelect
from spipobjects import (
    Article,
    Rubrique,
)
from styling import highlight, style


# Query the DB to retrieve all sections without parent, sorted by publication date
def root_sections(limit: int = 10**3) -> ModelSelect:
    return (
        Rubrique.select()
        .where(Rubrique.id_parent == 0)
        .order_by(Rubrique.date.desc())
        .limit(limit)
    )


def has_unknown_chars(article: Article) -> bool:
    if len(unknown_chars_context(article.texte)) > 0:
        return True
    return False


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


# Connect to the MySQL database with Peewee ORM
DB.init(CFG.db, host=CFG.db_host, user=CFG.db_user, password=CFG.db_pass)
DB.connect()


# Main loop to execute only if script is directly executed
if __name__ == "__main__":
    # Define max nb of articles to export based on first CLI argument
    if len(argv) >= 2:
        max_articles_export = int(argv[1])
    else:
        max_articles_export = CFG.max_articles_export
    # Define max nb of sections to export based on second CLI argument
    if len(argv) >= 3:
        max_sections_export = int(argv[2])
    else:
        max_sections_export = CFG.max_sections_export

    # Clear the output dir & create a new
    if CFG.clear_output:
        rmtree(CFG.output_dir, True)
    makedirs(CFG.output_dir, exist_ok=True)

    # Get the first max_sections_export root sections
    sections: ModelSelect = root_sections(max_sections_export)
    total: int = len(sections)

    # Write each root sections with its subtree
    for i, section in enumerate(sections):
        section.write_tree(CFG.output_dir, i, total)
        print()  # Break line after exporting the section

    # print()  # Break line between export & unknown characters warning
    # Warn about each article that contains unknown(s) character(s)
    # TODO do it with Python warnings

    DB.close()  # Close the connection with the database
