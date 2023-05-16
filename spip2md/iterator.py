from array import array

from converter import convertBody, convertMeta
from database import *
from slugify import slugify
# from yaml import CDumper as Dumper
from yaml import dump


class Article:
    def __init__(self, article):
        self.id = article.id_article
        # self.surtitle = article.surtitre  # Probably unused
        self.title, self.title_unknown = convertMeta(article.titre)
        self.subtitle = article.soustitre  # Probably unused
        # self.section = article.id_rubrique # TODO join
        self.description, self.description_unknown = convertMeta(article.descriptif)
        self.caption = article.chapo  # Probably unused
        self.text, self.text_unknown = convertBody(article.texte)  # Markdown
        self.ps = article.ps  # Probably unused
        self.publicationDate = article.date
        self.draft = False if article.statut == "publie" else True
        # self.sector = article.id_secteur # TODO join
        self.update = article.maj
        # self.export = article.export  # USELESS
        self.creationDate = article.date_redac
        # self.views = article.visites  # USELESS in static
        self.referers = article.referers  # TODO Why ?
        # self.popularity = article.popularite  # USELESS in static
        self.acceptForum = article.accepter_forum  # TODO Why ?
        self.contentUpdate = article.date_modif  # Probably unused
        self.lang = article.lang
        self.choosenLang = article.langue_choisie  # TODO Why ?
        # self.translation = article.id_trad # TODO join
        self.extra = article.extra  # Probably unused
        # self.version = article.id_version  # USELESS
        self.sitename = article.nom_site  # Probably useless
        self.virtual = article.virtuel  # TODO Why ?
        self.microblog = article.microblog  # Probably unused

    def get_slug(self):
        return slugify(f"{self.id}-{self.title}")

    def get_path(self):
        return self.get_slug()

    def get_authors(self):
        return SpipAuteursLiens.select().where(SpipAuteursLiens.id_objet == self.id)

    def get_frontmatter(self):
        return dump(
            {
                "lang": self.lang,
                "title": self.title,
                # "subtitle": self.subtitle,
                "date": self.creationDate,
                "publishDate": self.publicationDate,
                "lastmod": self.update,
                "draft": self.draft,
                "description": self.description,
                "authors": [author.id_auteur for author in self.get_authors()],
            },
            allow_unicode=True,
        )

    def get_article(self):
        # Build the final article text
        article: str = "---\n" + self.get_frontmatter() + "---"
        # If there is a caption, add the caption followed by a hr
        if len(self.caption) > 0:
            article += "\n\n" + self.caption + "\n\n***"
        # If there is a text, add the text preceded by two line breaks
        if len(self.text) > 0:
            article += "\n\n" + self.text
        # Same with an "extra" section
        if self.extra != None and len(self.extra) > 0:
            article += "\n\n# EXTRA\n\n" + self.extra
        # PS
        if len(self.ps) > 0:
            article += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if len(self.microblog) > 0:
            article += "\n\n# MICROBLOGGING\n\n" + self.microblog
        return article


class Articles:
    exported: int = 0
    unknownChars: list = []

    def __init__(self, maxToExport) -> None:
        # Query the DB to retrieve all articles sorted by publication date
        self.articles = (
            SpipArticles.select().order_by(SpipArticles.date.desc()).limit(maxToExport)
        )
        self.toExport: int = len(self.articles)

    def remaining(self):
        return self.toExport - self.exported

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining() <= 0:
            raise StopIteration()
        self.exported += 1
        return (
            {"exported": self.exported, "remaining": self.remaining()},
            Article(self.articles[self.exported - 1]),
        )
