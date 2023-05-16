#!python
from articles import Article, Articles
from config import config
from converter import highlightUnknownChars
from database import db

if __name__ != "__main__":
    exit()

import sys
from os import makedirs, mkdir
from shutil import rmtree

# Clean the output dir & create a new
rmtree(config.outputDir, True)
mkdir(config.outputDir)

# Connect to the MySQL database with Peewee ORM
db.init(config.db, host=config.dbHost, user=config.dbUser, password=config.dbPass)
db.connect()

# Define max nb of articles to export based on first CLI param
if len(sys.argv) > 1:
    maxToExport = int(sys.argv[1])
else:
    maxToExport = config.defaultNbToExport

# Define terminal escape sequences to stylize output
R: str = "\033[91m"
G: str = "\033[92m"
B: str = "\033[94m"
BOLD: str = "\033[1m"
RESET: str = "\033[0m"

# Articles that contains unknown chars
unknownCharsArticles: list[Article] = []

# Loop among first maxToExport articles & export them
for counter, article in Articles(maxToExport):
    if (counter["exported"] - 1) % 100 == 0:
        print(
            f"\n{BOLD}Exporting {R}{counter['remaining']+1}{RESET}"
            + f"{BOLD} SPIP articles to Markdown & YAML files{RESET}\n"
        )
    print(
        f"{BOLD}{counter['exported']}.{RESET} " + highlightUnknownChars(article.title)
    )
    fullPath: str = config.outputDir + "/" + article.getPath()
    print(f"{BOLD}>{RESET} {fullPath}{article.getFilename()}")
    makedirs(fullPath, exist_ok=True)
    with open(fullPath + article.getFilename(), "w") as f:
        f.write(article.getArticle())
    # Store detected unknown characters
    if len(article.getUnknownChars()) > 0:
        unknownCharsArticles.append(article)

for article in unknownCharsArticles:
    unknownCharsApparitions: list = article.getUnknownChars()
    nb: int = len(unknownCharsApparitions)
    s: str = "s" if nb > 1 else ""
    print(
        f"\n{BOLD}{nb}{RESET} unknown character{s} "
        + f"detected in article {BOLD}{article.id}{RESET}"
        + f"\n{BOLD}·{RESET} "
        + highlightUnknownChars(article.title)
    )
    for text in unknownCharsApparitions:
        print(f"  {BOLD}…{RESET} " + highlightUnknownChars(text))

db.close()  # Close the database connection
