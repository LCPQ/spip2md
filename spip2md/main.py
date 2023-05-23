#!python
# pyright: strict
from os import makedirs
from os.path import expanduser
from shutil import copyfile, rmtree
from sys import argv

from config import config
from converter import get_unknown_chars, unknown_chars
from database import db
from items import (
    Article,
    Articles,
    Document,
    Documents,
    LimitCounter,
    Section,
    Sections,
)


# Print a stylized string, without trailing newline
def style(string: str, *args: int) -> None:
    esc = "\033["  # Terminal escape sequence, needs to be closed by "m"
    if len(args) == 0:
        params: str = "1;"  # Defaults to bold
    else:
        params: str = ""
    for a in args:
        params += str(a) + ";"
    print(esc + params[:-1] + "m" + string + esc + "0m", end="")


# Define styles
BO = 1  # Bold
IT = 3  # Italic
UN = 4  # Underline
# Define colors
R = 91  # Red
G = 92  # Green
Y = 93  # Yellow
B = 94  # Blue
C0 = 95  # Color
C1 = 96  # Color
C2 = 96  # Color


# Print a string, highlighting every substring starting at start_stop[x][0] …
def highlight(string: str, *start_stop: tuple[int, int]) -> None:
    previous_stop = 0
    for start, stop in start_stop:
        print(string[previous_stop:start], end="")
        style(string[start:stop], BO, R)
        previous_stop = stop
    print(string[previous_stop:], end="")


# Connect to the MySQL database with Peewee ORM
db.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
db.connect()


# Output information about ongoing export & write section to output destination
def write_section(
    section: Section, counter: LimitCounter
) -> tuple[Articles, Documents, str]:
    # Print the name of the exported section & number of remaining sections
    style(f"{counter.count + 1}. ", BO)
    highlight(section.title, *unknown_chars(section.title))
    if counter.remaining() > 2:
        style(f"   {counter.remaining()-1}", BO, G)
        style(" sections")
        print(" left to export", end="")
    if toexport > 1:
        style(f"   {toexport}", BO, Y)
        style(" articles")
        print(" left before export limit", end="")
    print()
    # Define the section’s path (directory) & create directory(ies) if needed
    sectiondir: str = config.output_dir + "/" + section.get_slug()
    makedirs(sectiondir, exist_ok=True)
    # Define the section filename & write the index at that filename
    sectionpath: str = sectiondir + "/" + section.get_filename()
    with open(sectionpath, "w") as f:
        f.write(section.get_content())
    # Return the first "limit" articles of section
    return (section.get_articles(), section.get_documents(), sectiondir)


# Output information about ongoing export & write article to output destination
def write_article(
    article: Article, counter: LimitCounter, sectiondir: str
) -> tuple[Documents, str]:
    # Print the remaining number of articles to export every 100 articles
    if counter.count % 100 == 0:
        s: str = "s" if counter.remaining() > 1 else ""
        print("  Exporting", end="")
        style(f" {counter.remaining()}", BO, Y)
        print(" SPIP", end="")
        style(f" article{s}")
        print(" to Markdown & YAML files")
    # Print the title of the article being exported
    style(
        f"  {counter.count + 1}. "
        + ("EMPTY " if len(article.text) < 1 else "")
        + f"{article.lang} "
    )
    highlight(article.title, *unknown_chars(article.title))
    print()
    # Define the full article path & create directory(ies) if needed
    articledir: str = sectiondir + "/" + article.get_slug()
    makedirs(articledir, exist_ok=True)
    # Define the article filename & write the article at the filename
    articlepath: str = articledir + "/" + article.get_filename()
    with open(articlepath, "w") as f:
        f.write(article.get_content())
    # Store articles with unknown characters
    if len(get_unknown_chars(article.text)) > 0:
        unknown_chars_articles.append(article)
    return (article.get_documents(), articledir)


# Output information about ongoing export & copy document to output destination
def write_document(document: Document, counter: LimitCounter, objectdir: str) -> None:
    if counter.count % 100 == 0:
        s: str = "s" if counter.remaining() > 1 else ""
        print("    Exporting", end="")
        style(f" {counter.remaining()}", BO, B)
        style(f" document{s}")
        print(" in this article")
    # Print the name of the file with a counter
    style(f"    {counter.count + 1}. {document.media} ")
    if len(document.title) > 0:
        highlight(document.title + " ", *unknown_chars(document.title))
    style("at ")
    print(document.file)
    # Define document path
    documentpath: str = expanduser(config.data_dir + "/" + document.file)
    # Copy the document from it’s SPIP location to the new location
    try:
        copyfile(documentpath, objectdir + "/" + document.get_slug())
    except FileNotFoundError:
        style("    NOT FOUND: ", BO, R)
        print(documentpath)
    else:
        # Print the outputted file’s path when copied the file
        style("    -->", BO, B)
        print(f" {objectdir}/{document.get_slug()}")


# Return true if an article field contains an unknown character
def has_unknown_chars(article: Article) -> bool:
    return True


# Print the detected unknown chars in article in their context but highlighted
def warn_unknown_chars(article: Article) -> None:
    # Print the title of the article in which there is unknown characters
    # & the number of them
    unknown_chars_apparitions: list[str] = get_unknown_chars(article.text)
    nb: int = len(unknown_chars_apparitions)
    s: str = "s" if nb > 1 else ""
    style(f"{nb}")
    print(f" unknown character{s} in", end="")
    style(f" {article.lang} ")
    highlight(article.title, *unknown_chars(article.title))
    print()  # Break line
    # Print the context in which the unknown characters are found
    for text in unknown_chars_apparitions:
        style("  … ")
        highlight(text, *unknown_chars(text))
        style(" … \n")
    print()  # Break line


# Main loop to execute only if script is directly executed
if __name__ == "__main__":
    # Define max nb of articles to export based on first CLI argument
    if len(argv) >= 2:
        toexport = int(argv[1])
    else:
        toexport = config.default_export_max

    # Clear the output dir & create a new
    if config.clear_output:
        rmtree(config.output_dir, True)
    makedirs(config.output_dir, exist_ok=True)

    # Make a list containing articles where unknown characters are detected
    unknown_chars_articles: list[Article] = []

    # Loop among first maxexport articles & export them
    for section, counter in Sections(toexport):
        # Write the section & store its articles
        articles, documents, sectiondir = write_section(section, counter)
        # Loop over section’s related files (images …)
        for document, counter in documents:
            write_document(document, counter, sectiondir)
        # Loop over section’s articles
        for article, counter in articles:
            documents, articledir = write_article(article, counter, sectiondir)
            # Add article to unknown_chars_articles if needed
            if has_unknown_chars(article):
                unknown_chars_articles.append(article)
            # Loop over article’s related files (images …)
            for document, counter in documents:
                write_document(document, counter, articledir)
        # Break 2 lines when finished exporting the section
        print("\n")

    # Loop through each article that contains an unknown character
    for article in unknown_chars_articles:
        warn_unknown_chars(article)

    db.close()  # Close the connection with the database
