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
for row in cursor.fetchall():
    front_matter = {'title': row[1], 'date': row[2]} # Example front matter fields
    markdown_content = f'---\n{yaml.dump(front_matter)}---\n{row[3]}' # Example Markdown content
    file_path = f'{row[0]}.md' # Example file path
    with open(file_path, 'w') as f:
        f.write(markdown_content)

# Close the database connection
db.close()
