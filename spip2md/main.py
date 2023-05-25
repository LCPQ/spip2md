#!python
from os import makedirs
from shutil import rmtree
from sys import argv

from peewee import ModelSelect

from config import config
from converters import unknown_chars, unknown_chars_context
from database import DB
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
DB.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
DB.connect()


# Main loop to execute only if script is directly executed
if __name__ == "__main__":
    # Define max nb of articles to export based on first CLI argument
    if len(argv) >= 2:
        max_articles_export = int(argv[1])
    else:
        max_articles_export = config.max_articles_export
    # Define max nb of sections to export based on second CLI argument
    if len(argv) >= 3:
        max_sections_export = int(argv[2])
    else:
        max_sections_export = config.max_sections_export

    # Clear the output dir & create a new
    if config.clear_output:
        rmtree(config.output_dir, True)
    makedirs(config.output_dir, exist_ok=True)

    # Make a list containing articles where unknown characters are detected
    unknown_chars_articles: list[Article] = []

    # Write each root sections with its subtree
    for section in root_sections(max_sections_export):
        section.write()
        print()  # Break line after exporting the section

    print()  # Break line between export & unknown characters warning
    # Warn about each article that contains unknown(s) character(s)
    for article in unknown_chars_articles:
        warn_unknown_chars(article)

    DB.close()  # Close the connection with the database
