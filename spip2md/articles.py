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
        self.surtitle: str = article.surtitre  # Probably unused
        self.title: str = convert_meta(article.titre)
        self.subtitle: str = article.soustitre  # Probably unused
        self.section_id: int = article.id_rubrique
        self.description: str = convert_meta(article.descriptif)
        self.caption: str = article.chapo  # Probably unused
        self.text: str = convert_body(article.texte)  # Markdown
        self.ps: str = article.ps  # Probably unused
        self.publication: str = article.date
        self.draft: bool = False if article.statut == "publie" else True
        self.sector_id: int = article.id_secteur
        self.update: str = article.maj
        self.update_2: str = article.date_modif  # Probably unused duplicate of maj
        self.creation: str = article.date_redac
        self.forum: bool = article.accepter_forum  # TODO Why ?
        self.lang: str = article.lang
        self.set_lang: bool = article.langue_choisie  # TODO Why ?
        self.translation_key: int = article.id_trad
        self.extra: str = article.extra  # Probably unused
        self.sitename: str = article.nom_site  # Probably useless
        self.virtual: str = article.virtuel  # TODO Why ?
        self.microblog: str = article.microblog  # Probably unused
        # self.export = article.export  # USELESS
        # self.views: int = article.visites  # USELESS in static
        # self.referers: int = article.referers  # USELESS in static
        # self.popularity: float = article.popularite  # USELESS in static
        # self.version = article.id_version  # USELESS

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

    def get_article(self) -> str:
        # Build the final article text
        article: str = "---\n" + self.get_frontmatter() + "---"
        # If there is a caption, add the caption followed by a hr
        if len(self.caption) > 0:
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


class Section:
    def __init__(self, section) -> None:
        self.id: int = section.id_rubrique
        self.parent_id: int = section.id_parent
        self.title: str = convert_meta(section.titre)
        self.description: str = convert_meta(section.descriptif)
        self.text: str = convert_body(section.texte)  # Markdown
        self.sector_id: int = section.id_secteur
        self.update: str = section.maj
        self.publication: str = section.date
        self.draft: bool = False if section.statut == "publie" else True
        self.lang: str = section.lang
        self.lang_set: bool = False if section.langue_choisie == "oui" else True
        self.extra: str = section.extra  # Probably unused
        self.translation_key: int = section.id_trad
        self.depth: int = section.profondeur
        self.agenda: int = section.agenda


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
