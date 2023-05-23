# pyright: strict
from os.path import basename, splitext
from typing import Any, Optional

from slugify import slugify
from yaml import dump

from converter import convert_body, convert_documents, convert_meta, remove_tags
from database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)

EXPORTTYPE: str = "md"


class LimitCounter:
    def __init__(self, limit: int) -> None:
        self.count: int = -1
        self.LIMIT: int = limit

    def remaining(self) -> int:
        return self.LIMIT - self.count

    def step(self) -> int:
        self.count += 1
        if self.remaining() <= 0:
            raise StopIteration
        return self.count


class Iterator:
    items: list[Any]

    def __init__(self) -> None:
        # Set a counter caped at the number of retrieved items
        self.count = LimitCounter(len(self.items))

    def __iter__(self):
        return self

    def __len__(self) -> int:
        return self.count.LIMIT


class Document:
    def __init__(self, document: SpipDocuments) -> None:
        self.id: int = document.id_document
        self.thumbnail_id: int = document.id_vignette
        self.title: str = convert_meta(document.titre)
        self.date: str = document.date
        self.description: str = convert_meta(document.descriptif)
        self.file: str = document.fichier
        self.draft: bool = document.statut == "publie"
        self.creation: str = document.date
        self.publication: str = document.date_publication
        self.update: str = document.maj
        self.media: str = document.media

    def get_slug(self, date: bool = False) -> str:
        name_type = splitext(basename(self.file))
        return (
            slugify((self.publication + "-" if date else "") + name_type[0])
            + name_type[1]
        )


class Documents(Iterator):
    def __init__(self, object_id: int) -> None:
        # Query the DB to retrieve all documents related to object of id object_id
        self.items = (
            SpipDocuments.select()
            .join(
                SpipDocumentsLiens,
                on=(SpipDocuments.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == object_id)
        )
        super().__init__()

    def __next__(self):
        return (Document(self.items[self.count.step()]), self.count)


class Item:
    id: int

    def __init__(self, item: SpipArticles | SpipRubriques) -> None:
        self.title: str = convert_meta(item.titre)
        self.section_id: int = item.id_rubrique
        self.description: str = convert_meta(item.descriptif)
        self.text: str = convert_body(item.texte)  # Convert SPIP to Markdown
        self.publication: str = item.date
        self.draft: bool = item.statut == "publie"
        self.sector_id: int = item.id_secteur
        self.update: str = item.maj
        self.lang: str = item.lang
        self.set_lang: bool = item.langue_choisie == "oui"  # TODO Why ?
        self.translation_key: int = item.id_trad
        self.extra: str = convert_body(item.extra)  # Probably unused

    def get_slug(self, date: bool = False) -> str:
        return slugify((self.publication + "-" if date else "") + self.title)

    def get_filename(self) -> str:
        return "index" + "." + self.lang + "." + EXPORTTYPE

    def get_frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        return dump(
            {
                "lang": self.lang,
                "translationKey": self.translation_key,
                "title": self.title,
                "publishDate": self.publication,
                "lastmod": self.update,
                "draft": self.draft,
                "description": self.description,
                # Debugging
                "spip_id": self.id,
                "spip_id_secteur": self.sector_id,
            }
            | append
            if append is not None
            else {},
            allow_unicode=True,
        )

    def get_body(self) -> str:
        body: str = ""
        # Add the title as a Markdown h1
        if len(self.title) > 0:
            body += "\n\n# " + self.title
        # If there is a text, add the text preceded by two line breaks
        if len(self.text) > 0:
            # Convert images & files links
            text: str = convert_documents(
                self.text,
                [(d.id, d.title, d.get_slug()) for d, _ in self.get_documents()],
            )
            # Remove remaining HTML after & append to body
            body += "\n\n" + remove_tags(text)
        # Same with an "extra" section
        if len(self.extra) > 0:
            body += "\n\n# EXTRA\n\n" + self.extra
        return body

    def get_content(self) -> str:
        # Return the final article text
        return "---\n" + self.get_frontmatter() + "---" + self.get_body()

    def get_documents(self) -> Documents:
        return Documents(self.id)


class Article(Item):
    def __init__(self, article: SpipArticles) -> None:
        super().__init__(article)
        self.id: int = article.id_article
        self.surtitle: str = convert_meta(article.surtitre)  # Probably unused
        self.subtitle: str = convert_meta(article.soustitre)  # Probably unused
        self.caption: str = convert_body(article.chapo)  # Probably unused
        self.ps: str = convert_body(article.ps)  # Probably unused
        self.update_2: str = article.date_modif  # Probably unused duplicate of maj
        self.creation: str = article.date_redac
        self.forum: bool = article.accepter_forum == "oui"  # TODO Why ?
        self.sitename: str = article.nom_site  # Probably useless
        self.virtual: str = article.virtuel  # TODO Why ?
        self.microblog: str = article.microblog  # Probably unused
        # self.export = article.export  # USELESS
        # self.views: int = article.visites  # USELESS in static
        # self.referers: int = article.referers  # USELESS in static
        # self.popularity: float = article.popularite  # USELESS in static
        # self.version = article.id_version  # USELESS

    def get_authors(self) -> list[SpipAuteurs]:
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self.id)
        )

    def get_frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        return super().get_frontmatter(
            {
                "surtitle": self.surtitle,
                "subtitle": self.subtitle,
                "date": self.creation,
                "authors": [author.nom for author in self.get_authors()],
                # Debugging
                "spip_id_rubrique": self.section_id,
                "spip_id_secteur": self.sector_id,
                "spip_chapo": self.caption,
            }
            | append
            if append is not None
            else {},
        )

    def get_body(self) -> str:
        body: str = super().get_body()
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


class Section(Item):
    def __init__(self, section: SpipRubriques) -> None:
        super().__init__(section)
        self.id: int = section.id_rubrique
        self.parent_id: int = section.id_parent
        self.depth: int = section.profondeur
        self.agenda: int = section.agenda

    def get_filename(self) -> str:
        return "_" + super().get_filename()

    def get_articles(self, limit: int = 0):
        return Articles(self.id, limit)


class Articles(Iterator):
    def __init__(self, section_id: int, limit: int = 0) -> None:
        # Query the DB to retrieve all articles sorted by publication date
        if limit > 0:
            self.items = (
                SpipArticles.select()
                .where(SpipArticles.id_rubrique == section_id)
                .order_by(SpipArticles.date.desc())
                .limit(limit)
            )
        else:
            self.items = (
                SpipArticles.select()
                .where(SpipArticles.id_rubrique == section_id)
                .order_by(SpipArticles.date.desc())
            )
        super().__init__()

    def __next__(self):
        return (Article(self.items[self.count.step()]), self.count)


class Sections(Iterator):
    def __init__(self, limit: int = 0) -> None:
        # Query the DB to retrieve all sections sorted by publication date
        if limit > 0:
            self.items = (
                SpipRubriques.select().order_by(SpipRubriques.date.desc()).limit(limit)
            )
        else:
            self.items = SpipRubriques.select().order_by(SpipRubriques.date.desc())
        super().__init__()

    def __next__(self):
        return (Section(self.items[self.count.step()]), self.count)
