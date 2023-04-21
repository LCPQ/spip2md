#!python3
import os
import shutil
import sys
from datetime import *

# Modules
from config import CONFIG
from SpipDatabase import *
from metadata import metadata
from content import content

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
        nbToExport = 0
else:
    nbToExport = CONFIG["nbToExport"]

print(
    "--- Conversion of {} articles to Markdown files + YAML metadata ---\n".format(
        nbToExport
    )
)

# Loop among every articles & export them in Markdown files
for article in articles:
    meta = metadata(article)
    body = content(article.texte)
    articleDir = "{}/{}".format(CONFIG["outputDir"], meta.get_slug())
    os.mkdir(articleDir)
    with open("{}/index.md".format(articleDir), "w") as f:
        f.write(
            "{}\n{}\n{}".format(
                meta.get_frontmatter(), meta.get_title(), body.get_markdown()
            )
        )
    # End export if no more to export
    nbToExport -= 1
    if nbToExport <= 0:
        break

# Close the database connection
db.close()

# Announce the end of the script
print("\n--- End of script ---")
