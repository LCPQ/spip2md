#!python
# pyright: strict
import sys
from os import makedirs, mkdir
from shutil import rmtree

from articles import Article, Articles
from config import config
from converter import highlight_unknown_chars
from database import db

# Define terminal escape sequences to stylize output
R: str = "\033[91m"
G: str = "\033[92m"
B: str = "\033[94m"
BOLD: str = "\033[1m"
RESET: str = "\033[0m"

# Connect to the MySQL database with Peewee ORM
db.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
db.connect()

if __name__ == "__main__":
    # Define max nb of articles to export based on first CLI param
    if len(sys.argv) > 1:
        maxexport = int(sys.argv[1])
    else:
        maxexport = config.default_export_nb

    # Clean the output dir & create a new
    rmtree(config.output_dir, True)
    mkdir(config.output_dir)

    # Articles that contains unknown chars
    unknown_chars_articles: list[Article] = []

    # Loop among first maxexport articles & export them
    for counter, article in Articles(maxexport):
        if (counter["exported"] - 1) % 100 == 0:
            print(
                f"\n{BOLD}Exporting {R}{counter['remaining']+1}{RESET}"
                + f"{BOLD} SPIP articles to Markdown & YAML files{RESET}\n"
            )
        empty: str = "EMPTY " if len(article.text) < 1 else ""
        print(
            f"{BOLD}{counter['exported']}. {empty}{RESET}"
            + highlight_unknown_chars(article.title, R, RESET)
        )
        fullpath: str = config.output_dir + "/" + article.get_path()
        print(f"{BOLD}>{RESET} {fullpath}{article.get_filename()}")
        makedirs(fullpath, exist_ok=True)
        with open(fullpath + article.get_filename(), "w") as f:
            f.write(article.get_article())
        # Store detected unknown characters
        if len(article.get_unknown_chars()) > 0:
            unknown_chars_articles.append(article)

    for article in unknown_chars_articles:
        unknown_chars_apparitions: list[str] = article.get_unknown_chars()
        nb: int = len(unknown_chars_apparitions)
        s: str = "s" if nb > 1 else ""
        print(
            f"\n{BOLD}{nb}{RESET} unknown character{s} in {BOLD}{article.lang}{RESET} "
            + highlight_unknown_chars(article.title, R, RESET)
        )
        for text in unknown_chars_apparitions:
            print(f"  {BOLD}…{RESET} " + highlight_unknown_chars(text, R, RESET))

    db.close()  # Close the database connection
