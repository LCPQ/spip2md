#!python
# pyright: strict
from os import makedirs, mkdir
from shutil import rmtree
from sys import argv

from config import config
from converter import highlight_unknown_chars
from database import db
from lib import Article, Sections

# Define terminal escape sequences to stylize output
R: str = "\033[91m"
G: str = "\033[92m"
B: str = "\033[94m"
BOLD: str = "\033[1m"
RESET: str = "\033[0m"

# Connect to the MySQL database with Peewee ORM
db.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
db.connect()

if __name__ == "__main__":  # Following is executed only if script is directly executed
    # Define max nb of articles to export based on first CLI argument
    if len(argv) > 1:
        maxexport = int(argv[1])
    else:
        maxexport = config.default_export_nb

    # Clear the output dir & create a new
    rmtree(config.output_dir, True)
    mkdir(config.output_dir)

    # Articles that contains unknown chars
    unknown_chars_articles: list[Article] = []

    # Loop among first maxexport articles & export them
    for section, counter in Sections():
        # Print the name of the exported section & number of remaining sections
        print(
            f"{BOLD}{counter.count}. {RESET}"
            + highlight_unknown_chars(section.title, R, RESET),
            end="",
        )
        if counter.remaining() > 2:
            print(
                f"   {BOLD}{R}{counter.remaining()-1}{RESET} {BOLD}sections left"
                + RESET,
            )
        else:
            print()
        # Define the section’s path (directory) & create directory(ies) if needed
        sectiondir: str = config.output_dir + "/" + section.get_slug()
        makedirs(sectiondir, exist_ok=True)
        # Define the section filename & write the index at that filename
        sectionpath: str = sectiondir + "/" + section.get_filename()
        with open(sectionpath, "w") as f:
            f.write(section.get_content())
        # Loop over section’s articles
        articles = section.get_articles(maxexport)
        maxexport -= len(articles)
        for article, counter in articles:
            # Print the remaining number of articles to export every 100 articles
            if counter.count % 100 == 0:
                s: str = "s" if counter.remaining() > 1 else ""
                print(
                    f"  {BOLD}Exporting {R}{counter.remaining()}{RESET}"
                    + f"{BOLD} SPIP article{s}{RESET} to Markdown & YAML files\n"
                )
            # Print the title of the article being exported
            print(
                f"  {BOLD}{counter.count + 1}. "
                + ("EMPTY " if len(article.text) < 1 else "")
                + RESET
                + highlight_unknown_chars(article.title, R, RESET)
            )
            # Define the full article path & create directory(ies) if needed
            articledir: str = sectiondir + "/" + article.get_slug()
            makedirs(articledir, exist_ok=True)
            # Define the article filename & write the article at the filename
            articlepath: str = articledir + "/" + article.get_filename()
            with open(articlepath, "w") as f:
                f.write(article.get_content())
            # Store detected unknown characters
            if len(article.get_unknown_chars()) > 0:
                unknown_chars_articles.append(article)
            # Print the outputted file’s path when finished exporting the article
            print(f"  {BOLD}Article>{RESET} {articlepath}")
        # Print the outputted file’s path when finished exporting the section
        print(f"\n{BOLD}Section>{RESET} {sectionpath}\n")

    # Loop through each article that contains an unknown character
    for article in unknown_chars_articles:
        # Print the title of the article in which there is unknown characters
        # & the number of them
        unknown_chars_apparitions: list[str] = article.get_unknown_chars()
        nb: int = len(unknown_chars_apparitions)
        s: str = "s" if nb > 1 else ""
        print(
            f"\n{BOLD}{nb}{RESET} unknown character{s} in {BOLD}{article.lang}{RESET} "
            + highlight_unknown_chars(article.title, R, RESET)
        )
        # Print the context in which the unknown characters are found
        for text in unknown_chars_apparitions:
            print(f"  {BOLD}…{RESET} " + highlight_unknown_chars(text, R, RESET))

    db.close()  # Close the connection with the database
