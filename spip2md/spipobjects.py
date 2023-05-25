from os.path import basename, splitext
from re import I, compile, finditer
from typing import Any

from peewee import ModelSelect
from slugify import slugify
from yaml import dump

from config import config
from converters import convert, link_document
from database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)


class Document(SpipDocuments):
    class Meta:
        table_name: str = "spip_documents"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.statut: str = "false" if self.statut == "publie" else "true"

    def slug(self, date: bool = False) -> str:
        name_type: tuple[str, str] = splitext(basename(self.fichier))
        return (
            slugify((self.date_publication + "-" if date else "") + name_type[0])
            + name_type[1]
        )


class SpipObject:
    id: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common fields that need conversions
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.texte: str = convert(self.texte)  # Convert SPIP to Markdown
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        self.extra: str = convert(self.extra)  # Probably unused
        # Define file prefix (need to be changed later)
        self.prefix = "index"

    def documents(self) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.id)
        )
        for d in documents:
            self.texte = link_document(self.texte, d.id_document, d.titre, d.slug())
        # Internal (articles) links
        self.text = link_articles(self.texte)
        return documents

    def slug(self, date: bool = False) -> str:
        return slugify((self.date + "-" if date else "") + self.titre)

    def filename(self) -> str:
        return self.prefix + "." + self.lang + "." + config.export_filetype

    def frontmatter(self) -> str:
        raise NotImplementedError("Subclasses must implement 'frontmatter' method.")

    def common_frontmatter(self) -> dict[str, Any]:
        return {
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

    def body(self) -> str:
        body: str = ""
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

    def content(self) -> str:
        # Return the final article text
        return "---\n" + self.frontmatter() + "---" + self.body()


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

    def frontmatter(self) -> str:
        return dump(
            {
                **super().common_frontmatter(),
                # Article specific
                "summary": self.chapo,
                "surtitle": self.surtitre,
                "subtitle": self.soustitre,
                "date": self.date_redac,
                "authors": [author.nom for author in self.authors()],
                # Debugging
                "spip_id_rubrique": self.id_rubrique,
            },
            allow_unicode=True,
        )

    def body(self) -> str:
        body: str = super().body()
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


# Query the DB to retrieve all articles sorted by publication date
def get_articles(section_id: int, limit: int = 10**6) -> ModelSelect:
    return (
        Article.select()
        .where(Article.id_rubrique == section_id)
        .order_by(Article.date.desc())
        .limit(limit)
    )


def link_articles(text: str):
    for match in finditer(r"\[(.*?)]\((?:art|article)([0-9]+)\)", text):
        article = Article.get(Article.id_article == match.group(2))
        if len(match.group(1)) > 0:
            title: str = match.group(1)
        else:
            title: str = article.titre
        text = text.replace(
            match.group(0), f"[{title}]({article.slug()}/{article.filename()})"
        )
    return text


class Rubrique(SpipObject, SpipRubriques):
    class Meta:
        table_name: str = "spip_rubriques"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ID
        self.id = self.id_rubrique
        # File prefix
        self.prefix = "_index"

    def frontmatter(self) -> str:
        return dump(
            {
                **super().common_frontmatter(),
                # Debugging
                "spip_id_parent": self.id_parent,
                "spip_profondeur": self.profondeur,
            },
            allow_unicode=True,
        )


# Query the DB to retrieve all sections sorted by publication date
def get_sections(limit: int = 10**6) -> ModelSelect:
    return Rubrique.select().order_by(Rubrique.date.desc()).limit(limit)
