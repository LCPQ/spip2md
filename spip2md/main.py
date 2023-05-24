#!python
from os import makedirs
from os.path import expanduser
from shutil import copyfile, rmtree
from sys import argv

from config import config
from converters import unknown_chars, unknown_chars_context
from database import DB
from spipobjects import (
    Article,
    Document,
    Rubrique,
    get_articles,
    get_sections,
)

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


# Print a string, highlighting every substring starting at start_stop[x][0] …
def highlight(string: str, *start_stop: tuple[int, int]) -> None:
    previous_stop = 0
    for start, stop in start_stop:
        print(string[previous_stop:start], end="")
        style(string[start:stop], BO, R)
        previous_stop = stop
    print(string[previous_stop:], end="")


# Plural ?
def s(nb: int) -> str:
    return "s" if nb > 1 else ""


# Indent with spaces
def indent(nb: int = 1) -> None:
    for _ in range(nb):
        print("  ", end="")


# Output information about ongoing export & write section to output destination
def write_section(index: int, total: int, section: Rubrique) -> str:
    color = G  # Associate sections to green
    # Print the name of the exported section & number of remaining sections
    style(f"{index + 1}. ", BO)
    highlight(section.titre, *unknown_chars(section.titre))
    style(f" {total-index-1}", BO, color)
    style(f" section{s(total-index)} left")
    # Define the section’s path (directory) & create directory(ies) if needed
    sectiondir: str = config.output_dir + "/" + section.slug()
    makedirs(sectiondir, exist_ok=True)
    # Define the section filename & write the index at that filename
    sectionpath: str = sectiondir + "/" + section.filename()
    with open(sectionpath, "w") as f:
        f.write(section.content())
    # Print export location when finished exporting
    style(" -> ", BO, color)
    print(sectionpath)
    # Return the first "limit" articles of section
    return sectiondir


# Output information about ongoing export & write article to output destination
def write_article(index: int, total: int, article: Article, sectiondir: str) -> str:
    color = Y  # Associate articles to yellow
    # Print the remaining number of articles to export every 100 articles
    if index % 100 == 0:
        indent()
        print("Exporting", end="")
        style(f" {total-index}", BO, color)
        print(" SPIP", end="")
        style(f" article{s(total-index)}")
        print(" to Markdown & YAML files")
    # Print the title of the article being exported
    style(
        f"  {index + 1}. "
        + ("EMPTY " if len(article.texte) < 1 else "")
        + f"{article.lang} "
    )
    highlight(article.titre, *unknown_chars(article.titre))
    # Define the full article path & create directory(ies) if needed
    articledir: str = sectiondir + "/" + article.slug()
    makedirs(articledir, exist_ok=True)
    # Define the article filename & write the article at the filename
    articlepath: str = articledir + "/" + article.filename()
    with open(articlepath, "w") as f:
        f.write(article.content())
    # Print export location when finished exporting
    style(" -> ", BO, color)
    print(articlepath)
    return articledir


# Output information about ongoing export & copy document to output destination
def write_document(
    index: int, total: int, document: Document, objectdir: str, indent_depth: int = 1
) -> None:
    color = B  # Associate documents to blue
    if index % 100 == 0:
        indent(indent_depth)
        print("Exporting", end="")
        style(f" {total-index}", BO, color)
        style(f" document{s(total-index)}\n")
    # Print the name of the file with a counter
    indent(indent_depth)
    style(f"{index + 1}. {document.media} ")
    if len(document.titre) > 0:
        highlight(document.titre + " ", *unknown_chars(document.titre))
    style("at ")
    print(document.fichier, end="")
    # Define document path
    documentpath: str = expanduser(config.data_dir + "/" + document.fichier)
    # Copy the document from it’s SPIP location to the new location
    try:
        copyfile(documentpath, objectdir + "/" + document.slug())
    except FileNotFoundError:
        style(" -> NOT FOUND!\n", BO, R)
    else:
        # Print the outputted file’s path when copied the file
        style(" ->", BO, color)
        print(f" {objectdir}/{document.slug()}")


# Return true if an article field contains an unknown character
def has_unknown_chars(article: Article) -> bool:
    if len(unknown_chars_context(article.texte)) > 0:
        return True
    return False


# Print the detected unknown chars in article in their context but highlighted
def warn_unknown_chars(article: Article) -> None:
    # Print the title of the article in which there is unknown characters
    # & the number of them
    unknown_chars_apparitions: list[str] = unknown_chars_context(article.texte)
    nb: int = len(unknown_chars_apparitions)
    s: str = "s" if nb > 1 else ""
    style(f"{nb}")
    print(f" unknown character{s} in", end="")
    style(f" {article.lang} ")
    highlight(article.titre, *unknown_chars(article.titre))
    print()  # Break line
    # Print the context in which the unknown characters are found
    for text in unknown_chars_apparitions:
        style("  … ")
        highlight(text, *unknown_chars(text))
        style(" … \n")
    print()  # Break line


# Connect to the MySQL database with Peewee ORM
DB.init(config.db, host=config.db_host, user=config.db_user, password=config.db_pass)
DB.connect()


# Main loop to execute only if script is directly executed
if __name__ == "__main__":
    # Define max nb of articles to export based on first CLI argument
    if len(argv) >= 2:
        max_articles_export = int(argv[1])
    else:
        max_articles_export = config.max_articles_export
    # Define max nb of sections to export based on second CLI argument
    if len(argv) >= 3:
        max_sections_export = int(argv[2])
    else:
        max_sections_export = config.max_sections_export

    # Clear the output dir & create a new
    if config.clear_output:
        rmtree(config.output_dir, True)
    makedirs(config.output_dir, exist_ok=True)

    # Make a list containing articles where unknown characters are detected
    unknown_chars_articles: list[Article] = []

    # Get sections with an eventual maximum
    sections = get_sections(max_sections_export)
    nb_sections_export: int = len(sections)

    # Loop among sections & export them
    for i, section in enumerate(sections):
        # Get section’s documents & link them
        documents = section.documents()
        # Write the section and store its output directory
        sectiondir = write_section(i, nb_sections_export, section)
        # Loop over section’s related documents (images …)
        for i, document in enumerate(documents):
            write_document(i, len(documents), document, sectiondir)
        # Loop over section’s articles
        articles = get_articles(section.id_rubrique, (max_articles_export))
        for i, article in enumerate(articles):
            # Get article’s documents & link them
            documents = article.documents()
            # Write the article and store its output directory
            articledir = write_article(i, len(articles), article, sectiondir)
            # Add article to unknown_chars_articles if needed
            if has_unknown_chars(article):
                unknown_chars_articles.append(article)
            # Decrement export limit
            max_articles_export -= 1
            # Loop over article’s related documents (images …)
            for i, document in enumerate(documents):
                write_document(i, len(documents), document, articledir, 2)
        # Break line when finished exporting the section
        print()

    print()  # Break line
    # Loop through each article that contains an unknown character
    for article in unknown_chars_articles:
        warn_unknown_chars(article)

    DB.close()  # Close the connection with the database
