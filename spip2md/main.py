#!python
# pyright: basic
from articles import Article, Articles
from config import config
from converter import highlight_unknown_chars
from database import db

if __name__ != "__main__":
    exit()

import sys
from os import makedirs, mkdir
from shutil import rmtree

# Clean the output dir & create a new
rmtree(config.output_dir, True)
mkdir(config.output_dir)

# Connect to the MySQL database with Peewee ORM
db.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
db.connect()

# Define max nb of articles to export based on first CLI param
if len(sys.argv) > 1:
    maxexport = int(sys.argv[1])
else:
    maxexport = config.default_export_nb

# Define terminal escape sequences to stylize output
R: str = "\033[91m"
G: str = "\033[92m"
B: str = "\033[94m"
BOLD: str = "\033[1m"
RESET: str = "\033[0m"

# Articles that contains unknown chars
unknown_chars_articles: list[Article] = []

# Loop among first maxToExport articles & export them
for counter, article in Articles(maxexport):
    if (counter["exported"] - 1) % 100 == 0:
        print(
            f"\n{BOLD}Exporting {R}{counter['remaining']+1}{RESET}"
            + f"{BOLD} SPIP articles to Markdown & YAML files{RESET}\n"
        )
    print(
        f"{BOLD}{counter['exported']}.{RESET} " + highlight_unknown_chars(article.title)
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
    unknown_chars_apparitions: list = article.get_unknown_chars()
    nb: int = len(unknown_chars_apparitions)
    s: str = "s" if nb > 1 else ""
    print(
        f"\n{BOLD}{nb}{RESET} unknown character{s} "
        + f"detected in article {BOLD}{article.id}{RESET}"
        + f"\n{BOLD}·{RESET} "
        + highlight_unknown_chars(article.title)
    )
    for text in unknown_chars_apparitions:
        print(f"  {BOLD}…{RESET} " + highlight_unknown_chars(text))

db.close()  # Close the database connection
