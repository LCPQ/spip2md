# pyright: basic
from re import finditer

from slugify import slugify
from yaml import dump

from converter import convert_body, convert_meta, unknown_iso
from database import SpipArticles, SpipAuteurs, SpipAuteursLiens, SpipRubriques

# from yaml import CDumper as Dumper


class Article:
    def __init__(self, article):
        self.id: int = article.id_article
        # self.surtitle = article.surtitre  # Probably unused
        self.title: str = convert_meta(article.titre)
        self.subtitle: str = article.soustitre  # Probably unused
        self.section_id: int = article.id_rubrique
        self.description: str = convert_meta(article.descriptif)
        self.caption: str = article.chapo  # Probably unused
        self.text: str = convert_body(article.texte)  # Markdown
        self.ps: str = article.ps  # Probably unused
        self.publicationDate: str = article.date
        self.draft: bool = False if article.statut == "publie" else True
        # self.sector = article.id_secteur # TODO join
        self.update: str = article.maj
        # self.export = article.export  # USELESS
        self.creationDate: str = article.date_redac
        # self.views = article.visites  # USELESS in static
        # self.referers = article.referers  # TODO Why ?
        # self.popularity = article.popularite  # USELESS in static
        # self.acceptForum = article.accepter_forum  # TODO Why ?
        self.contentUpdate: str = article.date_modif  # Probably unused
        self.lang: str = article.lang
        self.choosenLang: str = article.langue_choisie  # TODO Why ?
        # self.translation = article.id_trad # TODO join
        self.extra: str = article.extra  # Probably unused
        # self.version = article.id_version  # USELESS
        self.sitename: str = article.nom_site  # Probably useless
        self.virtual: str = article.virtuel  # TODO Why ?
        self.microblog: str = article.microblog  # Probably unused

    def get_section(self) -> str:
        return convert_meta(
            SpipRubriques.select()
            .where(SpipRubriques.id_rubrique == self.section_id)[0]
            .titre
        )

    def get_path(self) -> str:
        return slugify(self.get_section()) + "/" + slugify(f"{self.title}") + "/"

    def get_filename(self) -> str:
        return "index." + self.lang + ".md"

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
                "title": self.title,
                # "subtitle": self.subtitle,
                "date": self.creationDate,
                "publishDate": self.publicationDate,
                "lastmod": self.update,
                "draft": self.draft,
                "description": self.description,
                "authors": [author.nom for author in self.get_authors()],
            },
            allow_unicode=True,
        )

    def get_article(self) -> str:
        # Build the final article text
        article: str = "---\n" + self.get_frontmatter() + "---"
        # If there is a caption, add the caption followed by a hr
        if len(self.caption) > 0:
            article += "\n\n" + self.caption + "\n\n***"
        # If there is a text, add the text preceded by two line breaks
        if len(self.text) > 0:
            article += "\n\n" + self.text
        # Same with an "extra" section
        if self.extra is not None and len(self.extra) > 0:
            article += "\n\n# EXTRA\n\n" + self.extra
        # PS
        if len(self.ps) > 0:
            article += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if len(self.microblog) > 0:
            article += "\n\n# MICROBLOGGING\n\n" + self.microblog
        return article

    def get_unknown_chars(self) -> list[str]:
        errors: list[str] = []
        for text in (self.title, self.text):
            for char in unknown_iso:
                for match in finditer(char + r".*(?=\r?\n|$)", text):
                    errors.append(match.group())
        return errors


class Articles:
    exported: int = 0

    def __init__(self, maxexport: int) -> None:
        # Query the DB to retrieve all articles sorted by publication date
        self.articles = (
            SpipArticles.select().order_by(SpipArticles.date.desc()).limit(maxexport)
        )
        self.toExport: int = len(self.articles)

    def remaining(self):
        return self.toExport - self.exported

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining() <= 0:
            raise StopIteration
        self.exported += 1
        article = Article(self.articles[self.exported - 1])
        return (
            {"exported": self.exported, "remaining": self.remaining()},
            article,
        )
