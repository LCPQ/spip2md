import yaml
from slugify import slugify


class metadata:
    def __init__(self, article):
        self.id = article.id_article
        # self.surtitle = article.surtitre  # Probably unused
        self.title = article.titre
        self.subtitle = article.soustitre  # Probably unused
        # self.section = article.id_rubrique # TODO join
        self.caption = article.chapo  # Probably unused
        self.ps = article.ps  # Probably unused
        self.publicationDate = article.date
        self.status = article.statut
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
        return slugify("{}-{}".format(self.id, self.title))

    def get_frontmatter(self):
        return "---\n{}---".format(
            yaml.dump(
                {
                    "lang": self.lang,
                    "title": self.title,
                    "subtitle": self.subtitle,
                    "creation": self.creationDate,
                    "date": self.publicationDate,
                    "update": self.update,
                    "status": self.status,
                }
            )
        )

    # Contains things before the article like caption & titles
    def get_starting(self):
        return "{}\n\n# {}\n".format(self.caption, self.title)

    # Contains things after the article like ps & extra
    def get_ending(self):
        return "# EXTRA\n\n{}\n\n# POST-SCRIPTUM\n\n{}\n\n# MICROBLOGGING\n\n{}".format(
            self.extra, self.ps, self.microblog
        )
