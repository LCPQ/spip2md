from os.path import basename, splitext

from peewee import ModelSelect
from slugify import slugify
from yaml import dump

from converters import convert, link_document
from database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)

EXPORTTYPE: str = "md"


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


class Article(SpipArticles):
    class Meta:
        table_name: str = "spip_articles"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.texte: str = convert(self.texte)  # Convert SPIP to Markdown
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        self.extra: str = convert(self.extra)  # Probably unused
        # Article specific
        self.surtitle: str = convert(self.surtitre, True)  # Probably unused
        self.subtitle: str = convert(self.soustitre, True)  # Probably unused
        self.caption: str = convert(self.chapo)  # Probably unused
        self.ps: str = convert(self.ps)  # Probably unused
        self.accepter_forum: str = "true" if self.accepter_forum == "oui" else "false"

    def documents(self) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.id_article)
        )
        for d in documents:
            self.texte = link_document(self.texte, d.id_document, d.titre, d.slug())
        return documents

    def slug(self, date: bool = False) -> str:
        return slugify((self.date + "-" if date else "") + self.titre)

    def filename(self) -> str:
        return "index" + "." + self.lang + "." + EXPORTTYPE

    def frontmatter(self) -> str:
        return dump(
            {
                "lang": self.lang,
                "translationKey": self.id_trad,
                "title": self.titre,
                "publishDate": self.date,
                "lastmod": self.maj,
                "draft": self.statut,
                "description": self.descriptif,
                # Debugging
                "spip_id": self.id_article,
                "spip_id_secteur": self.id_secteur,
                # Article specific
                "surtitle": self.surtitle,
                "subtitle": self.subtitle,
                "date": self.date_redac,
                "authors": [author.nom for author in self.authors()],
                # Debugging
                "spip_id_rubrique": self.id_rubrique,
                "spip_chapo": self.caption,
            },
            allow_unicode=True,
        )

    def body(self) -> str:
        body: str = ""
        # Add the title as a Markdown h1
        if len(self.titre) > 0:
            body += "\n\n# " + self.titre
        # If there is a text, add the text preceded by two line breaks
        if len(self.texte) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self.texte
        # Same with an "extra" section
        if len(self.extra) > 0:
            body += "\n\n# EXTRA\n\n" + self.extra
        # If there is a caption, add the caption followed by a hr
        if hasattr(self, "caption") and len(self.caption) > 0:
            body += "\n\n" + self.caption + "\n\n***"
        # PS
        if hasattr(self, "ps") and len(self.ps) > 0:
            body += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if hasattr(self, "microblog") and len(self.microblog) > 0:
            body += "\n\n# MICROBLOGGING\n\n" + self.microblog
        return body

    def content(self) -> str:
        # Return the final article text
        return "---\n" + self.frontmatter() + "---" + self.body()

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


class Rubrique(SpipRubriques):
    class Meta:
        table_name: str = "spip_rubriques"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre: str = convert(self.titre, True)
        self.descriptif: str = convert(self.descriptif, True)
        self.texte: str = convert(self.texte)  # Convert SPIP to Markdown
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        self.extra: str = convert(self.extra)  # Probably unused

    def documents(self) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.id_rubrique)
        )
        for d in documents:
            self.texte = link_document(self.texte, d.id_document, d.titre, d.slug())
        return documents

    def slug(self, date: bool = False) -> str:
        return slugify((self.date + "-" if date else "") + self.titre)

    def filename(self) -> str:
        return "_index" + "." + self.lang + "." + EXPORTTYPE

    def frontmatter(self) -> str:
        return dump(
            {
                "lang": self.lang,
                "translationKey": self.id_trad,
                "title": self.titre,
                "publishDate": self.date,
                "lastmod": self.maj,
                "draft": self.statut,
                "description": self.descriptif,
                # Debugging
                "spip_id": self.id_rubrique,
                "spip_id_secteur": self.id_secteur,
            },
            allow_unicode=True,
        )

    def body(self) -> str:
        body: str = ""
        # Add the title as a Markdown h1
        if len(self.titre) > 0:
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


# Query the DB to retrieve all sections sorted by publication date
def get_sections(limit: int = 10**6) -> ModelSelect:
    return Rubrique.select().order_by(Rubrique.date.desc()).limit(limit)
