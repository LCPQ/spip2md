#!python3
import os
import shutil
import sys
from pprint import pprint
# from peewee import *
import pymysql
# Local modules
from metadata import metadata
from content import content

# Constants definition
outputDir = "output"
outputType = "md"

# Clean the output dir & create a new
shutil.rmtree(outputDir, True)
os.mkdir(outputDir)

# Connect to the MySQL database
db = pymysql.connect(
    host="localhost",
    db="spip",
    user="spip",
    password="password",
)

# Query the database to retrieve all data
cursor = db.cursor()
cursor.execute("SELECT * FROM spip_articles ORDER BY date DESC")

# Choose how many articles export based on first param
if len(sys.argv) > 1:
    if int(sys.argv[1]) > 0:
        fetch = cursor.fetchmany(int(sys.argv[1]))
    else:
        fetch = cursor.fetchall()
else:
    fetch = cursor.fetchmany(3)

print("--- Conversion of {} articles to Markdown files + YAML metadata ---\n"
      .format(len(fetch)))

if len(fetch) < 5:
    pprint(fetch)

# Loop among every articles & export them in Markdown files
for row in fetch:
    meta = metadata(row)
    body = content(row[7])
    articleDir = "{}/{}".format(outputDir, meta.get_slug())
    os.mkdir(articleDir)
    with open("{}/index.md".format(articleDir), "w") as f:
        f.write("{}\n{}\n{}"
                .format(meta.get_frontmatter(), meta.get_title(), body.get_markdown()))

# Close the database connection
db.close()

# Announce the end of the script
print("\n--- End of script ---")
