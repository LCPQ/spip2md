import yaml
from convert import convert
from slugify import slugify
from SpipDatabase import *


class metadata:
    def __init__(self, article):
        self.id = article.id_article
        # self.surtitle = article.surtitre  # Probably unused
        self.title = convert(article.titre)
        self.subtitle = article.soustitre  # Probably unused
        # self.section = article.id_rubrique # TODO join
        self.description = convert(article.descriptif)
        self.caption = article.chapo  # Probably unused
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

    def get_authors(self):
        return SpipAuteursLiens.select().where(SpipAuteursLiens.id_objet == self.id)

    def get_frontmatter(self):
        return "---\n{}---".format(
            yaml.dump(
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
        )

    # Contains things before the article like caption & titles
    def get_starting(self):
        return (
            # f"{self.caption}\n" if len(self.caption) > 0 else "" + f"# {self.title}\n"
            f"{self.caption}\n\n***\n"
            if len(self.caption) > 0 and self.caption != " "
            else ""
        )

    # Contains things after the article like ps & extra
    def get_ending(self):
        return (
            f"# EXTRA\n\n{self.extra}"
            if self.extra != None and len(self.extra) > 0
            else "" + f"# POST-SCRIPTUM\n\n{self.ps}"
            if len(self.ps) > 0
            else "" + f"# MICROBLOGGING\n\n{self.microblog}"
            if len(self.microblog) > 0
            else ""
        )
