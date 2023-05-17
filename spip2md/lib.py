# pyright: basic
from re import finditer

from slugify import slugify
from yaml import dump

from converter import convert_body, convert_meta, unknown_iso
from database import SpipArticles, SpipAuteurs, SpipAuteursLiens, SpipRubriques

# from yaml import CDumper as Dumper

FILETYPE: str = "md"


class Item:
    id: int

    def __init__(self, item) -> None:
        self.title: str = convert_meta(item.titre)
        self.section_id: int = item.id_rubrique
        self.description: str = convert_meta(item.descriptif)
        self.text: str = convert_body(item.texte)  # Markdown
        self.publication: str = item.date
        self.draft: bool = item.statut == "publie"
        self.sector_id: int = item.id_secteur
        self.update: str = item.maj
        self.lang: str = item.lang
        self.set_lang: bool = item.langue_choisie  # TODO Why ?
        self.translation_key: int = item.id_trad
        self.extra: str = item.extra  # Probably unused

    def get_slug(self, date: bool = False) -> str:
        return slugify(f"{self.publication if date else ''}-{self.title}")

    def get_filename(self) -> str:
        return "index" + "." + self.lang + "." + FILETYPE

    def get_frontmatter(self) -> str:
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
            },
            allow_unicode=True,
        )

    def get_content(self) -> str:
        # Build the final article text
        article: str = "---\n" + self.get_frontmatter() + "---"
        # If there is a caption, add the caption followed by a hr
        if hasattr(self, "caption") and len(self.caption) > 0:
            article += "\n\n" + self.caption + "\n\n***"
        # Add the title as a Markdown h1
        if len(self.title) > 0:
            article += "\n\n# " + self.title
        # If there is a text, add the text preceded by two line breaks
        if len(self.text) > 0:
            article += "\n\n" + self.text
        # Same with an "extra" section
        if self.extra is not None and len(self.extra) > 0:
            article += "\n\n# EXTRA\n\n" + self.extra
        # PS
        if hasattr(self, "ps") and len(self.ps) > 0:
            article += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if hasattr(self, "microblog") and len(self.microblog) > 0:
            article += "\n\n# MICROBLOGGING\n\n" + self.microblog
        return article

    def get_unknown_chars(self) -> list[str]:
        errors: list[str] = []
        for text in (self.title, self.text):
            for char in unknown_iso:
                for match in finditer(r".{0-20}" + char + r".*(?=\r?\n|$)", text):
                    errors.append(match.group())
        return errors


class Article(Item):
    def __init__(self, article) -> None:
        super().__init__(article)
        self.id: int = article.id_article
        self.surtitle: str = article.surtitre  # Probably unused
        self.subtitle: str = article.soustitre  # Probably unused
        self.caption: str = article.chapo  # Probably unused
        self.ps: str = article.ps  # Probably unused
        self.update_2: str = article.date_modif  # Probably unused duplicate of maj
        self.creation: str = article.date_redac
        self.forum: bool = article.accepter_forum  # TODO Why ?
        self.sitename: str = article.nom_site  # Probably useless
        self.virtual: str = article.virtuel  # TODO Why ?
        self.microblog: str = article.microblog  # Probably unused
        # self.export = article.export  # USELESS
        # self.views: int = article.visites  # USELESS in static
        # self.referers: int = article.referers  # USELESS in static
        # self.popularity: float = article.popularite  # USELESS in static
        # self.version = article.id_version  # USELESS

    def get_authors(self) -> tuple:
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self.id)
        )

    def get_frontmatter(self) -> str:
        return dump(
            {
                "lang": self.lang,
                "translationKey": self.translation_key,
                "title": self.title,
                "surtitle": self.surtitle,
                "subtitle": self.subtitle,
                "date": self.creation,
                "publishDate": self.publication,
                "lastmod": self.update,
                "draft": self.draft,
                "description": self.description,
                "authors": [author.nom for author in self.get_authors()],
                # Debugging
                "spip_id_article": self.id,
                "spip_id_rubrique": self.section_id,
                "spip_id_secteur": self.sector_id,
                "spip_chapo": self.caption,
            },
            allow_unicode=True,
        )


class Section(Item):
    def __init__(self, section) -> None:
        super().__init__(section)
        self.id: int = section.id_rubrique
        self.parent_id: int = section.id_parent
        self.depth: int = section.profondeur
        self.agenda: int = section.agenda

    def get_articles(self, limit: int = 0):
        return Articles(self.id, limit)


class LimitCounter:
    count: int
    LIMIT: int

    def __init__(self, limit: int) -> None:
        self.count = -1
        self.LIMIT = limit

    def remaining(self) -> int:
        return self.LIMIT - self.count

    def step(self) -> int:
        self.count += 1
        if self.remaining() <= 0:
            raise StopIteration
        return self.count


class Items:
    items: list

    def __init__(self) -> None:
        # Set a counter caped at the number of retrieved items
        self.count = LimitCounter(len(self.items))

    def __iter__(self):
        return self

    def __len__(self) -> int:
        return self.count.LIMIT


class Articles(Items):
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
            self.items = SpipArticles.select().order_by(SpipArticles.date.desc())
        super().__init__()

    def __next__(self):
        return (Article(self.items[self.count.step()]), self.count)


class Sections(Items):
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
