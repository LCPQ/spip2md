# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
from os import makedirs
from os.path import basename, splitext
from re import finditer
from shutil import copyfile
from typing import Any, Optional

from peewee import BigAutoField, DateTimeField, ModelSelect
from slugify import slugify
from yaml import dump

from spip2md import BLUE, BOLD, GREEN, RED, YELLOW, highlight, indent, ss, style
from spip2md.config import CFG
from spip2md.converters import convert, link_document, unknown_chars
from spip2md.database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)


class SpipWritable:
    term_color: int
    texte: str
    lang: str
    titre: str

    def filename(self, date: bool = False) -> str:
        raise NotImplementedError(
            f"Subclasses need to implement filename(), date: {date}"
        )

    def begin_message(
        self, index: int, limit: int, depth: int = 0, step: int = 100
    ) -> None:
        # Print the remaining number of objects to export every step object
        if index % step == 0:
            indent(depth)
            print("Exporting", end="")
            style(f" {limit-index}", BOLD, self.term_color)
            if hasattr(self, "profondeur"):
                print(f" level {self.profondeur}", end="")
            style(f" {type(self).__name__}{ss(limit-index)}\n")
        # Print the counter & title of the object being exported
        indent(depth)
        style(f"{index + 1}. ")
        if len(self.titre) > 0:
            highlight(self.titre, *unknown_chars(self.titre))
        else:
            print("MISSING NAME", end="")
        # + ("EMPTY " if len(self.texte) < 1 else "")
        # + f"{self.lang} "

    # Write object to output destination
    def write(self, parent_dir: str) -> str:
        raise NotImplementedError(
            f"Subclasses need to implement write(), export dir: {parent_dir}"
        )

    # Output information about file that was just exported
    def end_message(self, message: str | Exception):
        style(" -> ", BOLD, self.term_color)
        if message is Exception:
            style("ERROR ", BOLD, RED)
        print(message)


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
        name_type: tuple[str, str] = splitext(basename(str(self.fichier)))
        return (
            slugify(
                (self.date_publication + "-" if date else "") + name_type[0],
                max_length=100,
            )
            + name_type[1]
        )

    # Write document to output destination
    def write(self, parent_dir: str) -> str:
        # Define file source and destination
        src: str = CFG.data_dir + self.fichier
        dest: str = parent_dir + self.filename()
        # Copy the document from it’s SPIP location to the new location
        copyfile(src, dest)
        return dest


class SpipObject(SpipWritable):
    object_id: BigAutoField
    id_trad: int
    date: DateTimeField
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
            self.texte = link_document(self.texte, d.id_document, d.titre, d.filename())

    # Output related documents & link them in the text by the way
    def documents(self, link_documents: bool = True) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.object_id)
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
                match.group(0), f"[{title}]({article.dir_slug()}/{article.filename()})"
            )

    # Output related articles
    def articles(self) -> ModelSelect:
        return (
            Article.select()
            .where(Article.id_rubrique == self.object_id)
            .order_by(Article.date.desc())
            # .limit(limit)
        )

    # Get slugified directory of this object
    def dir_slug(self, include_date: bool = False, end_slash: bool = True) -> str:
        date: str = self.date + "-" if include_date else ""
        slash: str = "/" if end_slash else ""
        return slugify(date + self.titre, max_length=100) + slash

    # Get filename of this object
    def filename(self) -> str:
        return self.prefix + "." + self.lang + "." + CFG.export_filetype

    # Get the YAML frontmatter string
    def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
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
            "spip_id": self.object_id,
        }
        if append is not None:
            return dump(meta | append, allow_unicode=True)
        else:
            return dump(meta, allow_unicode=True)

    # Get file text content
    def content(self) -> str:
        # Start the content with frontmatter
        body: str = "---\n" + self.frontmatter() + "---"
        # Add the title as a Markdown h1
        if len(self.titre) > 0 and CFG.prepend_h1:
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
    def write(self, parent_dir: str) -> str:
        # Define actual export directory
        directory: str = parent_dir + self.dir_slug()
        # Make a directory for this object if there isn’t
        makedirs(directory, exist_ok=True)
        # Define actual export path
        path: str = directory + self.filename()
        # Write the content of this object into a file named as self.filename()
        with open(path, "w") as f:
            f.write(self.content())
        return path


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
        self.object_id = self.id_article
        # Terminal output color
        self.term_color = YELLOW

    def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        meta: dict[str, Any] = {
            # Article specific
            "summary": self.chapo,
            "surtitle": self.surtitre,
            "subtitle": self.soustitre,
            "date": self.date_redac,
            "authors": [author.nom for author in self.authors()],
            # Debugging
            "spip_id_rubrique": self.id_rubrique,
        }
        if append is not None:
            return super().frontmatter(meta | append)
        else:
            return super().frontmatter(meta)

    def content(self) -> str:
        body: str = super().content()
        # If there is a caption, add the caption followed by a hr
        if len(str(self.chapo)) > 0:
            body += "\n\n" + self.chapo + "\n\n***"
        # PS
        if len(str(self.ps)) > 0:
            body += "\n\n# POST-SCRIPTUM\n\n" + self.ps
        # Microblog
        if len(str(self.microblog)) > 0:
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
        self.object_id = self.id_rubrique
        # File prefix
        self.prefix = "_index"
        # Terminal output color
        self.term_color = GREEN

    def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        meta: dict[str, Any] = {
            # Debugging
            "spip_id_parent": self.id_parent,
            "spip_profondeur": self.profondeur,
        }
        if append is not None:
            return super().frontmatter(meta | append)
        else:
            return super().frontmatter(meta)

    def write_tree(self, parent_dir: str, index: int, total: int):
        self.begin_message(index, total, int(self.profondeur))
        # Get this section’s articles documents
        articles = self.articles()
        documents = self.documents()
        # Write this section
        self.link_articles()
        export_path: str = self.write(parent_dir)
        self.end_message(export_path)
        # Redefine parent_dir for subtree elements
        parent_dir = parent_dir + self.dir_slug()

        # Write this section’s articles and documents
        def write_loop(objects: ModelSelect):
            total = len(objects)
            for i, obj in enumerate(objects):
                obj.begin_message(i, total, self.profondeur + 1)
                try:
                    export_path: str = obj.write(parent_dir)
                    obj.end_message(export_path)
                except Exception as err:
                    obj.end_message(err)

        write_loop(articles)
        write_loop(documents)

        # Get all child section of self
        child_sections = (
            Rubrique.select()
            .where(Rubrique.id_parent == self.id_rubrique)
            .order_by(Rubrique.date.desc())
        )
        nb: int = len(child_sections)
        # Do the same for subsections (write their entire subtree)
        for i, s in enumerate(child_sections):
            s.write_tree(parent_dir, i, nb)
