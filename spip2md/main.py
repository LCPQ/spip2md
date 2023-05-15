#!python
from config import config
from database import db
from iterator import Articles

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
R = "\033[91m"
G = "\033[92m"
B = "\033[94m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

# Loop among first maxToExport articles & export them
for counter, article in Articles(maxToExport):
    if (counter["exported"] - 1) % 100 == 0:
        print(
            f"\n{BOLD}Exporting {R}{counter['remaining']+1}{RESET}"
            + f"{BOLD} SPIP articles to Markdown & YAML files{RESET}\n"
        )
    print(f"{BOLD}{counter['exported']}.{RESET} {article.title}")
    fullPath = config.outputDir + "/" + article.get_path()
    print(f"\t-> {fullPath}/index.md")
    mkdir(fullPath)
    with open(fullPath + "/index.md", "w") as f:
        f.write(article.get_article())

# Close the database connection
db.close()
