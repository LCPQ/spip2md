# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs
from os.path import basename, splitext
from re import finditer, search, sub
from shutil import copyfile
from typing import Any, Match, Optional

from peewee import BigAutoField, DateTimeField, ModelSelect
from slugify import slugify
from yaml import dump

from spip2md.config import CFG
from spip2md.database import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)
from spip2md.regexmap import (
    BLOAT,
    DOCUMENT_LINK,
    DOCUMENT_LINK_REPL,
    HTMLTAG,
    ISO_UTF,
    MULTILANG_BLOCK,
    MULTILANGS,
    SPECIAL_OUTPUT,
    SPIP_MARKDOWN,
    UNKNOWN_ISO,
    WARNING_OUTPUT,
)
from spip2md.style import BLUE, BOLD, GREEN, WARNING_STYLE, YELLOW, esc

# Output logs to logfile
logging.basicConfig(filename=CFG.logfile, encoding="utf-8")


class SpipWritable:
    term_color: int
    texte: str
    lang: str
    titre: str
    descriptif: str
    profondeur: int
    style: tuple[int, ...]

    # Returns the first detected language (& instantiate a new object for the second)
    # (currently don’t instantiate, just warns)
    def translate(self, text: str) -> str:
        def replace_lang(match: Match[str]) -> str:
            first_lang: str = match.group(1)
            # The first group is the inside of <multi></multi> blocks
            for i, lang in enumerate(MULTILANGS.finditer(match.group(1))):
                if i == 0:
                    # Redefine this lang to the first one WARNING
                    self.lang = lang.group(1)
                    # Outputs the first lang associated text
                    first_lang = lang.group(2)
                else:
                    pass
                    logging.warning(
                        f"Ignored {lang.group(1)} translation of {first_lang[:40]}: "
                        + lang.group(2)[:40],
                    )
            return first_lang

        return MULTILANG_BLOCK.sub(replace_lang, text)

    # Apply different mappings to a text field, like SPIP to Markdown or encoding
    def convert(self, text: Optional[str]) -> str:
        # Return unknown char surrounded by context_length chars
        def unknown_chars_context(text: str, char: str, context_len: int = 24) -> str:
            context: str = r".{0," + str(context_len) + r"}"
            match = search(
                context + r"(?=" + char + r")" + char + context,
                text,
            )
            if match is not None:
                return match.group()
            else:
                return char

        if text is not None and len(text) > 0:
            for spip, markdown in SPIP_MARKDOWN:
                text = spip.sub(markdown, text)
            for bloat in BLOAT:
                text = bloat.sub("", text)
            for iso, utf in ISO_UTF:
                text = text.replace(iso, utf)
            for char in UNKNOWN_ISO:
                lastend: int = 0
                for match in finditer("(" + char + ")+", text):
                    context: str = unknown_chars_context(text[lastend:], char)
                    logging.warn(
                        f"Unknown char {char} found in {self.titre[:40]} at: {context}"
                    )
                    lastend = match.end()
            text = self.translate(text)
        else:
            return ""
        return text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre = self.convert(self.titre)
        self.descriptif = self.convert(self.descriptif)

    def filename(self, date: bool = False) -> str:
        raise NotImplementedError(
            f"Subclasses need to implement filename(), date: {date}"
        )

    # Print one or more string(s) in which special elements are stylized
    def style_print(self, string: str, indent: bool = True, end: str = "\n") -> str:
        stylized: str = string
        for o in SPECIAL_OUTPUT:
            stylized = o.sub(esc(*self.style) + r"\1" + esc(), stylized)
        for w in WARNING_OUTPUT:
            stylized = w.sub(esc(*WARNING_STYLE) + r"\1" + esc(), stylized)
        if indent:
            stylized = "  " * self.profondeur + stylized
        print(stylized, end=end)
        # Return the stylized string
        return stylized

    def begin_message(self, index: int, limit: int, step: int = 100) -> list[str]:
        output: list[str] = []
        # Output the remaining number of objects to export every step object
        if index % step == 0:
            output.append(f"Exporting {limit-index}")
            if hasattr(self, "profondeur"):
                output[-1] += f" level {self.profondeur}"
            s: str = "s" if limit - index > 1 else ""
            output[-1] += f" {type(self).__name__}{s}"
            # Print the output as the program goes
            self.style_print(output[-1])
        # Output the counter & title of the object being exported
        output.append(f"{index + 1}. ")
        if len(self.titre) > 0:
            output[-1] += self.titre.strip(" ")
        else:
            output[-1] += "MISSING NAME"
        # Print the output as the program goes
        self.style_print(output[-1], end="")
        return output

    # Write object to output destination
    def write(self, parent_dir: str) -> str:
        raise NotImplementedError(
            f"Subclasses need to implement write(), export dir: {parent_dir}"
        )

    # Output information about file that was just exported
    def end_message(self, message: str | Exception) -> str:
        output: str = " -> "
        if message is Exception:
            output += "ERROR "
        # Print the output as the program goes
        self.style_print(output + str(message), indent=False)
        return output + str(message)


class Document(SpipWritable, SpipDocuments):
    # Documents accent color is blue
    style = (BOLD, BLUE)

    class Meta:
        table_name: str = "spip_documents"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statut: str = "false" if self.statut == "publie" else "true"

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
    descriptif: str
    extra: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common fields that need conversions
        self.extra: str = self.convert(self.extra)
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        # Define file prefix (needs to be redefined for sections)
        self.prefix = "index"

    # Convert SPIP style internal links for images & other files into Markdown style
    def link_documents(self, documents: ModelSelect) -> None:
        for d in documents:
            self.texte = sub(
                DOCUMENT_LINK.format(d.id_document),
                DOCUMENT_LINK_REPL.format(d.titre, d.filename()),
                self.texte,
            )

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

    # Clean remaining HTML tags in attrs
    def clean_html(self, *attrs: str) -> None:
        attrs += "titre", "texte", "descriptif", "extra"
        for attr in attrs:
            a = getattr(self, attr)
            if len(a) > 0:
                setattr(self, attr, HTMLTAG.sub("", a))

    # Write object to output destination
    def write(self, parent_dir: str, clean_html: bool = True) -> str:
        # Link articles
        self.link_articles()
        # Delete remaining HTML tags WARNING
        if clean_html:
            self.clean_html()
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
    # Articles accent color is yellow
    style = (BOLD, YELLOW)

    class Meta:
        table_name: str = "spip_articles"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # More conversions needed for articles
        self.surtitre: str = self.convert(self.surtitre)
        self.soustitre: str = self.convert(self.soustitre)
        self.chapo: str = self.convert(self.chapo)
        self.ps: str = self.convert(self.ps)
        self.accepter_forum: str = "true" if self.accepter_forum == "oui" else "false"
        # ID
        self.object_id = self.id_article

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
    # Sections accent color is green
    style = (BOLD, GREEN)

    class Meta:
        table_name: str = "spip_rubriques"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ID
        self.object_id = self.id_rubrique
        # File prefix
        self.prefix = "_index"

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

    def write_tree(
        self, parent_dir: str, index: int, total: int
    ) -> list[str | list[Any]]:
        # Define dictionary output to diplay
        output: list[str | list[Any]] = []
        for m in self.begin_message(index, total):
            output.append(m)
        # Get this section’s articles documents
        articles = self.articles()
        documents = self.documents()
        # Write this section
        output[-1] += self.end_message(self.write(parent_dir))
        # Redefine parent_dir for subtree elements
        parent_dir = parent_dir + self.dir_slug()

        # Write this section’s articles and documents
        def write_loop(objects: ModelSelect) -> list[str]:
            output: list[str] = []
            total = len(objects)
            for i, obj in enumerate(objects):
                obj.profondeur = self.profondeur + 1
                for m in obj.begin_message(i, total):
                    output.append(m)
                try:
                    output[-1] += obj.end_message(obj.write(parent_dir))
                except Exception as err:
                    output[-1] += obj.end_message(err)
            return output

        output.append(write_loop(articles))
        output.append(write_loop(documents))

        # Get all child section of self
        child_sections: ModelSelect = (
            Rubrique.select()
            .where(Rubrique.id_parent == self.id_rubrique)
            .order_by(Rubrique.date.desc())
        )
        nb: int = len(child_sections)
        # Do the same for subsections (write their entire subtree)
        for i, s in enumerate(child_sections):
            output.append(s.write_tree(parent_dir, i, nb))
        return output


class RootRubrique(Rubrique):
    class Meta:
        table_name: str = "spip_rubriques"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 0 ID
        self.id_rubrique = 0
        # self.object_id = 0
        self.profondeur = 0

    def write_tree(
        self, parent_dir: str, sections_limit: int = 0, articles_limit: int = 0
    ) -> list[str | list]:
        # Define dictionary output to diplay
        output: list[str | list] = []
        # Print starting message
        print(
            f"""\
Begin exporting {esc(BOLD)}{CFG.db}@{CFG.db_host}{esc()} SPIP database to plain \
Markdown+YAML files,
into the directory {esc(BOLD)}{parent_dir}{esc()}, \
as database user {esc(BOLD)}{CFG.db_user}{esc()}
"""
        )
        # Get all child section of self
        child_sections: ModelSelect = (
            Rubrique.select()
            .where(Rubrique.id_parent == self.id_rubrique)
            .order_by(Rubrique.date.desc())
        )
        nb: int = len(child_sections)
        # Do the same for subsections (write their entire subtree)
        for i, s in enumerate(child_sections):
            output.append(s.write_tree(parent_dir, i, nb))
            print()  # Break line for level 1
        return output
