#!python
from config import config
from database import db
from iterator import Articles, highlightUnknownChars

if __name__ != "__main__":
    exit()

import sys
from os import mkdir
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

unknownChars: dict = {}

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
    fullPath = config.outputDir + "/" + article.getPath()
    print(f"{BOLD}>{RESET} {fullPath}/index.md")
    mkdir(fullPath)
    with open(fullPath + "/index.md", "w") as f:
        f.write(article.getArticle())
    # Store detected unknown characters
    if len(article.getUnknownChars()) > 0:
        unknownChars[article.title] = article.getUnknownChars()

for title in unknownChars:
    nb = len(unknownChars[title])
    print(
        f"\n{BOLD}{nb} "
        + f"unknown character{'s' if nb > 1 else ''} detected in{RESET} " +
            highlightUnknownChars(title)
    )
    for text in unknownChars[title]:
        print(f"  {BOLD}…{RESET} " + highlightUnknownChars(text))

# Close the database connection
db.close()
