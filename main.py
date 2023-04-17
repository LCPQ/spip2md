import pymysql
import os
import yaml

# Connect to the MySQL database
db = pymysql.connect(
    host='localhost',
    db='spip',
    user='spip',
    password='password',
)

# Query the database to retrieve all data
cursor = db.cursor()
cursor.execute('SELECT * FROM spip_articles')

# Loop through the results and format data into Markdown files
# Columns:
#   2: titre
#   7: texte
#   9: date
# for row in cursor.fetchall():
for row in cursor.fetchmany(5):
    frontmatter = {'title': row[2], 'date': row[9]}
    content = f'---\n{yaml.dump(frontmatter)}---\n{row[7]}'
    path = f'markdown/{row[2]}.md'
    with open(path, 'w') as f:
        f.write(content)

# Close the database connection
db.close()
