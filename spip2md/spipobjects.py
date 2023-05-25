from os import makedirs
from os.path import basename, splitext
from re import finditer
from shutil import copyfile
from typing import Any

from peewee import Model, ModelSelect
from slugify import slugify
from yaml import dump

from config import config
from converters import convert, link_document, unknown_chars
from database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)
from styling import BLUE, BOLD, GREEN, YELLOW, highlight, indent, ss, style


class SpipWritable:
    class Meta:
        table_name: str

    term_color: int
    texte: str
    lang: str
    titre: str

    def filename(self, date: bool = False) -> str:
        raise NotImplementedError("Subclasses need to implement filename()")

    # Output information about file that will be exported
    def begin_message(
        self, index: int, limit: int, depth: int = 0, step: int = 100
    ) -> None:
        # Print the remaining number of objects to export every step object
        if index % step == 0:
            indent(depth)
            print("Exporting", end="")
            style(f" {limit-index}", BOLD, self.term_color)
            print(f" element{ss(limit-index)} from", end="")
            style(f" {self.Meta.table_name}")
        # Print the counter & title of the object being exported
        indent(depth)
        style(f"{index + 1}. ")
        highlight(self.titre, *unknown_chars(self.titre))
        # + ("EMPTY " if len(self.texte) < 1 else "")
        # + f"{self.lang} "

    # Write object to output destination
    def write(self, export_dir: str) -> None:
        raise NotImplementedError("Subclasses need to implement write()")

    # Output information about file that was just exported
    def end_message(self, export_dir: str):
        style(" -> ", BOLD, self.term_color)
        print(export_dir + self.filename())


class Document(SpipWritable, SpipDocuments):
    class Meta:
        table_name: str = "spip_documents"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.statut: str = "false" if self.statut == "publie" else "true"
        # Terminal output color
        self.term_color: int = BLUE

    # Get slugified name of this file
    def filename(self, date: bool = False) -> str:
        name_type: tuple[str, str] = splitext(basename(self.fichier))
        return (
            slugify((self.date_publication + "-" if date else "") + name_type[0])
            + name_type[1]
        )

    # Write document to output destination
    def write(self, export_dir: str) -> None:
        # Copy the document from it’s SPIP location to the new location
        try:
            copyfile(config.data_dir + self.fichier, export_dir + self.filename())
        except FileNotFoundError:
            raise FileNotFoundError(" -> NOT FOUND!\n") from None


class SpipObject(SpipWritable):
    id: int
    id_trad: int
    date: str
    maj: str
    id_secteur: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common fields that need conversions
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.texte: str = convert(self.texte)  # Convert SPIP to Markdown
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        self.extra: str = convert(self.extra)  # Probably unused
        # Define file prefix (needs to be redefined for sections)
        self.prefix = "index"

    # Convert SPIP style internal links for images & other files into Markdown style
    def link_documents(self, documents: ModelSelect) -> None:
        for d in documents:
            self.texte = link_document(self.texte, d.id_document, d.titre, d.slug())

    # Output related documents & link them in the text by the way
    def documents(self, link_documents: bool = True) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.id)
        )
        if link_documents:
            self.link_documents(documents)
        return documents

    # Convert SPIP style internal links for other articles or sections into Markdown
    def link_articles(self) -> None:
        for match in finditer(r"\[(.*?)]\((?:art|article)([0-9]+)\)", self.texte):
            article = Article.get(Article.id_article == match.group(2))
            if len(match.group(1)) > 0:
                title: str = match.group(1)
            else:
                title: str = article.titre
            self.texte = self.texte.replace(
                match.group(0), f"[{title}]({article.slug()}/{article.filename()})"
            )

    # Output related articles
    def articles(self) -> ModelSelect:
        return (
            Article.select()
            .where(Article.id_rubrique == self.id)
            .order_by(Article.date.desc())
            # .limit(limit)
        )

    # Get slugified directory of this object
    def dir_slug(self, include_date: bool = False, end_slash: bool = True) -> str:
        date: str = self.date + "-" if include_date else ""
        slash: str = "/" if end_slash else ""
        return slugify(date + self.titre) + slash

    # Get filename of this object
    def filename(self) -> str:
        return self.prefix + "." + self.lang + "." + config.export_filetype

    # Get the YAML frontmatter string
    def frontmatter(self, append: dict[str, Any] = {}) -> str:
        meta: dict[str, Any] = {
            "lang": self.lang,
            "translationKey": self.id_trad,
            "title": self.titre,
            "publishDate": self.date,
            "lastmod": self.maj,
            "draft": self.statut,
            "description": self.descriptif,
            # Debugging
            "spip_id_secteur": self.id_secteur,
            "spip_id": self.id,
        }
        return dump(meta | append, allow_unicode=True)

    # Get file text content
    def content(self) -> str:
        # Start the content with frontmatter
        body: str = "---\n" + self.frontmatter() + "---"
        # Add the title as a Markdown h1
        if len(self.titre) > 0 and config.prepend_h1:
            body += "\n\n# " + self.titre
        # If there is a text, add the text preceded by two line breaks
        if len(self.texte) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self.texte
        # Same with an "extra" section
        if len(self.extra) > 0:
            body += "\n\n# EXTRA\n\n" + self.extra
        return body

    # Write object to output destination
    def write(self, export_dir: str) -> None:
        with open(export_dir + self.filename(), "w") as f:
            f.write(self.content())


class Article(SpipObject, SpipArticles):
    class Meta:
        table_name: str = "spip_articles"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # More conversions needed for articles
        self.surtitre: str = convert(self.surtitre, True)  # Probably unused
        self.soustitre: str = convert(self.soustitre, True)  # Probably unused
        self.chapo: str = convert(self.chapo)  # Probably unused
        self.ps: str = convert(self.ps)  # Probably unused
        self.accepter_forum: str = "true" if self.accepter_forum == "oui" else "false"
        # ID
        self.id = self.id_article
        # Terminal output color
        self.term_color = YELLOW

    def frontmatter(self, append: dict[str, Any] = {}) -> str:
        return super().frontmatter(
            {
                # Article specific
                "summary": self.chapo,
                "surtitle": self.surtitre,
                "subtitle": self.soustitre,
                "date": self.date_redac,
                "authors": [author.nom for author in self.authors()],
                # Debugging
                "spip_id_rubrique": self.id_rubrique,
            }
        )

    def content(self) -> str:
        body: str = super().content()
        # If there is a caption, add the caption followed by a hr
        if len(self.chapo) > 0:
            body += "\n\n" + self.chapo + "\n\n***"
        # PS
        if len(self.ps) > 0:
            body += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if len(self.microblog) > 0:
            body += "\n\n# MICROBLOGGING\n\n" + self.microblog
        return body

    def authors(self) -> list[SpipAuteurs]:
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self.id_article)
        )


class Rubrique(SpipObject, SpipRubriques):
    class Meta:
        table_name: str = "spip_rubriques"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ID
        self.id = self.id_rubrique
        # File prefix
        self.prefix = "_index"
        # Terminal output color
        self.term_color = GREEN

    def frontmatter(self, append: dict[str, Any] = {}) -> str:
        return super().frontmatter(
            {
                # Debugging
                "spip_id_parent": self.id_parent,
                "spip_profondeur": self.profondeur,
            }
        )
