#!python3
import os
import shutil
import sys
from pprint import pprint
# from peewee import *
import pymysql
from slugify import slugify
import yaml

outputDir = "output"
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

# Loop through the results and format data into Markdown files
# Columns:
#   2: titre
#   7: texte
#   9: date

if len(sys.argv) > 1:
    if int(sys.argv[1]) > 0:
        fetch = cursor.fetchmany(int(sys.argv[1]))
    else:
        fetch = cursor.fetchall()
else:
    fetch = cursor.fetchmany(3)
    print("--- {} articles will be converted to Markdown files wihth YAML metadata ---\n".format(len(fetch)))
    pprint(fetch)

for row in fetch:
    frontmatter = {"title": row[2], "date": row[9]}
    content = "---\n{}---\n{}\n\n{}".format(yaml.dump(frontmatter), row[2], row[7])
    path = "{}/{}.md".format(outputDir, slugify("{}-{}".format(row[0], row[2])))
    with open(path, "w") as f:
        f.write(content)

# Close the database connection
db.close()

# Announce the end of the script
print("\n--- End of script ---")
