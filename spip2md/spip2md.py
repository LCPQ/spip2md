#!python
import sys
from os import mkdir
from shutil import rmtree

from config import CONFIG
from convert import convert
from Metadata import metadata
from SpipDatabase import *

# Clean the output dir & create a new
rmtree(CONFIG["outputDir"], True)
mkdir(CONFIG["outputDir"])

# Connect to the MySQL database with Peewee ORM
db.connect()

# Query the DB to retrieve all articles sorted by publication date
articles = SpipArticles.select().order_by(SpipArticles.date.desc())
# Query the DB to retrieve all articles sorted by modification date
# articles = SpipArticles.select().order_by(SpipArticles.date_modif.desc())

# Choose how many articles to export based on first param
if len(sys.argv) > 1:
    if int(sys.argv[1]) > 0 and int(sys.argv[1]) < len(articles):
        nbToExport = int(sys.argv[1])
    else:
        nbToExport = len(articles)
else:
    if len(articles) > CONFIG["maxExportNb"]:
        nbToExport = CONFIG["maxExportNb"]
    else:
        nbToExport = len(articles)

print(f"--- Export of {nbToExport} SPIP articles to Markdown & YAML files ---\n")

# Loop among every articles & export them in Markdown files
for exported in range(nbToExport):
    if exported > 0 and exported % 10 == 0:
        print(f"\n--- {nbToExport - exported} articles remaining ---\n")
    article = articles[exported]
    meta = metadata(article)

    print(f"{exported+1}. Exporting {meta.title}")
    print(f"    to {meta.get_slug()}/index.md")
    articleDir = "{}/{}".format(CONFIG["outputDir"], meta.get_slug())

    mkdir(articleDir)
    with open("{}/index.md".format(articleDir), "w") as f:
        f.write(
            "{}\n{}\n{}\n{}".format(
                meta.get_frontmatter(),
                meta.get_starting(),
                convert(article.texte),
                meta.get_ending(),
            )
        )

# Close the database connection
db.close()

# Announce the end of the script
print(
    f"\n--- Exported {nbToExport} SPIP articles to ./{CONFIG['outputDir']}/*/index.md ---"
)
