#!python3
import os
import shutil
import sys
# from datetime import date, datetime, time
# Modules
from config import CONFIG
from content import content
from metadata import metadata
from SpipDatabase import *

# Clean the output dir & create a new
shutil.rmtree(CONFIG["outputDir"], True)
os.mkdir(CONFIG["outputDir"])

# Connect to the MySQL database with Peewee ORM
db.connect()

# Query the DB to retrieve all articles sorted by publication date
articles = SpipArticles.select().order_by(SpipArticles.date.desc())
# Query the DB to retrieve all articles sorted by modification date
# articles = SpipArticles.select().order_by(SpipArticles.date_modif.desc())

# Choose how many articles to export based on first param
if len(sys.argv) > 1:
    if int(sys.argv[1]) > 0:
        nbToExport = int(sys.argv[1])
    else:
        nbToExport = len(articles)
else:
    if len(articles) > CONFIG["maxExportNb"]:
        nbToExport = CONFIG["maxExportNb"]
    else:
        nbToExport = len(articles)

print(
    f"--- Export of {nbToExport} SPIP articles to Markdown & YAML files ---\n"
)

exported = 1

# Loop among every articles & export them in Markdown files
for article in articles:
    meta = metadata(article)
    print(f"{exported}. Exporting {meta.title}")
    print(f"    in {meta.get_slug()}/index.md")
    body = content(article.texte)
    articleDir = "{}/{}".format(CONFIG["outputDir"], meta.get_slug())
    os.mkdir(articleDir)
    with open("{}/index.md".format(articleDir), "w") as f:
        f.write(
            "{}\n{}\n{}\n{}".format(
                meta.get_frontmatter(),
                meta.get_starting(),
                body.get_markdown(),
                meta.get_ending(),
            )
        )
    # End export if no more to export
    if exported > nbToExport:
        break
    elif exported % 10 == 0:
        print(f"\n--- {nbToExport - exported} articles remaining ---\n")
    exported += 1

# Close the database connection
db.close()

# Announce the end of the script
print(f"\n--- Finished exporting {nbToExport} SPIP articles to md & YAML ---")
