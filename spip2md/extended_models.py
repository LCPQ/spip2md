# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs
from os.path import basename, splitext
from re import finditer, search
from shutil import copyfile
from typing import Any, Match, Optional

from peewee import BigAutoField, DateTimeField, DoesNotExist, ModelSelect
from slugify import slugify
from yaml import dump

from spip2md.config import CFG
from spip2md.regexmaps import (
    ARTICLE_LINK,
    BLOAT,
    DOCUMENT_LINK,
    HTMLTAG,
    ISO_UTF,
    MULTILANG_BLOCK,
    MULTILANGS,
    SECTION_LINK,
    SPECIAL_OUTPUT,
    SPIP_MARKDOWN,
    UNKNOWN_ISO,
    WARNING_OUTPUT,
)
from spip2md.spip_models import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipRubriques,
)
from spip2md.style import BLUE, BOLD, GREEN, WARNING_STYLE, YELLOW, esc


class SpipWritable:
    texte: str
    lang: str
    titre: str
    descriptif: str
    profondeur: int
    style: tuple[int, ...]

    # Returns the first detected language & instantiate a new object for the nexts
    def translate_multi(self, text: str) -> str:
        # Create a lang: text dict
        translations: dict[str, str] = {"default": text}
        # Keep the first lang in default translation, then
        # for each langs of <multi> blocks, add its text to the corresponding dict key
        for block in MULTILANG_BLOCK.finditer(translations["default"]):
            for i, lang in enumerate(MULTILANGS.finditer(block.group(1))):
                if i == 0:
                    translations["default"] = translations["default"].replace(
                        block.group(), lang.group(2)
                    )
                if lang.group(1) in translations:
                    translations[lang.group(1)] += lang.group(2)
                else:
                    translations[lang.group(1)] = lang.group(2)
                # Logs the translation
                title: str = self.titre.strip()
                translated: str = lang.group(2)[:50].strip()
                logging.info(f"{lang.group(1)} translation of {title}: {translated}")
        # Instantiate & write translated
        # for lang, translation in translations.items():
        #     if lang == "non existant lang":
        #         new_lang = self.__init__(
        #             texte=translation,
        #             lang=lang,
        #             titre=self.titre,
        #             descriptif=self.descriptif,
        #             profondeur=self.profondeur,
        #             style=self.style,
        #         )
        # Return the translations dict
        # return translations
        # Return the first detected language
        return translations["default"]

    # Apply different mappings to a text field, like SPIP to Markdown or encoding
    def convert(self, text: str, clean_html: bool = True) -> str:
        if len(text) == 0:
            # print("Empty text")
            return ""

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

        # Convert SPIP syntax to Markdown
        for spip, markdown in SPIP_MARKDOWN:
            text = spip.sub(markdown, text)
        # Remove useless text
        for bloat in BLOAT:
            text = bloat.sub("", text)
        # Convert broken ISO encoding to UTF
        for iso, utf in ISO_UTF:
            text = text.replace(iso, utf)
        # Handle <multi> multi language blocks
        text = self.translate_multi(text)
        # Delete remaining HTML tags in body WARNING
        if clean_html:
            text = HTMLTAG.sub("", text)
        # Warn about unknown chars
        for char in UNKNOWN_ISO:
            lastend: int = 0
            for match in finditer("(" + char + ")+", text):
                context: str = unknown_chars_context(text[lastend:], char)
                logging.warn(
                    f"Unknown char {char} found in {self.titre[:40]} at: {context}"
                )
                if CFG.unknown_char_replacement is not None:
                    logging.warn(
                        f"Replacing {match.group()} with {CFG.unknown_char_replacement}"
                    )
                    text = text.replace(match.group(), CFG.unknown_char_replacement, 1)
                lastend = match.end()
        return text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.titre is not None:
            # print(f"Convert titre from {type(self)} {self.titre}")
            self.titre: str = self.convert(self.titre)
        if self.descriptif is not None:
            # print(f"Convert descriptif from {type(self)} {self.titre}")
            self.descriptif: str = self.convert(self.descriptif)

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
            output[-1] += f" level {self.profondeur}"
            s: str = "s" if limit - index > 1 else ""
            output[-1] += f" {type(self).__name__}{s}"
            # Print the output as the program goes
            self.style_print(output[-1])
        # Output the counter & title of the object being exported
        output.append(f"{index + 1}. ")
        if self.titre is None:
            output[-1] += "MISSING NAME"
        elif len(self.titre) == 0:
            output[-1] += "EMPTY NAME"
        else:
            output[-1] += self.titre.strip(" ")
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
        if type(message) is not str:
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

    def convert(self, text: str, clean_html: bool = True) -> str:
        if len(text) == 0:
            # print("Empty text")
            return ""

        def found_replace(path_link: str, doc: Any, text: str, match: Match) -> str:
            # TODO get relative path
            if len(match.group(1)) > 0:
                repl: str = path_link.format(match.group(1), doc.filename())
            else:
                repl: str = path_link.format(doc.titre, doc.filename())
            logging.info(f"Translating link to {repl}")
            return text.replace(match.group(), repl)

        def not_found_warn(path_link: str, text: str, match: Match) -> str:
            logging.warn(f"No object for link {match.group()} in {self.titre}")
            return text.replace(match.group(), path_link.format("", "NOT FOUND"), 1)

        for id_link, path_link in DOCUMENT_LINK:
            # print(f"Looking for links like {id_link}")
            for match in id_link.finditer(text):
                logging.info(f"Found document link {match.group()} in {self.titre}")
                try:
                    doc: Document = Document.get(Document.id_document == match.group(2))
                    text = found_replace(path_link, doc, text, match)
                except DoesNotExist:
                    text = not_found_warn(path_link, text, match)
        for id_link, path_link in ARTICLE_LINK:
            # print(f"Looking for links like {id_link}")
            for match in id_link.finditer(text):
                logging.info(f"Found article link {match.group()} in {self.titre}")
                try:
                    art: Article = Article.get(Article.id_article == match.group(2))
                    text = found_replace(path_link, art, text, match)
                except DoesNotExist:
                    text = not_found_warn(path_link, text, match)
        for id_link, path_link in SECTION_LINK:
            # print(f"Looking for links like {id_link}")
            for match in id_link.finditer(text):
                logging.info(f"Found section link {match.group()} in {self.titre}")
                try:
                    section: Rubrique = Rubrique.get(
                        Rubrique.id_rubrique == match.group(2)
                    )
                    text = found_replace(path_link, section, text, match)
                except DoesNotExist:
                    text = not_found_warn(path_link, text, match)
        return super().convert(text, clean_html)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common fields that need conversions
        if self.texte is not None:
            # print(f"Convert texte from {type(self)} {self.titre}")
            # print(f"First 500 chars: {self.texte[:500]}")
            self.texte: str = self.convert(self.texte)
        if self.extra is not None:
            # print(f"Convert extra from {type(self)} {self.titre}")
            # print(f"First 500 chars: {self.extra[:500]}")
            self.extra: str = self.convert(self.extra)
        self.statut: str = "false" if self.statut == "publie" else "true"
        self.langue_choisie: str = "false" if self.langue_choisie == "oui" else "true"
        # Define file prefix (needs to be redefined for sections)
        self.prefix = "index"

    # Get related documents
    def documents(self) -> ModelSelect:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.object_id)
        )
        return documents

    # Get related articles
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
        if self.titre is not None and len(self.titre) > 0 and CFG.prepend_h1:
            body += "\n\n# " + self.titre
        # If there is a text, add the text preceded by two line breaks
        if self.texte is not None and len(self.texte) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self.texte
        # Same with an "extra" section
        if self.extra is not None and len(self.extra) > 0:
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
    # Articles accent color is yellow
    style = (BOLD, YELLOW)

    class Meta:
        table_name: str = "spip_articles"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # More conversions needed for articles
        if self.surtitre is not None:
            self.surtitre: str = self.convert(self.surtitre)
        if self.soustitre is not None:
            self.soustitre: str = self.convert(self.soustitre)
        if self.chapo is not None:
            self.chapo: str = self.convert(self.chapo)
        if self.ps is not None:
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

    def write_tree(self, parent_dir: str) -> list[str | list]:
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
