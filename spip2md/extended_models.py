# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from copy import deepcopy
from os import makedirs
from os.path import basename, splitext
from re import Pattern, finditer, search
from shutil import copyfile
from typing import Any, Optional

from peewee import (
    BigAutoField,
    BigIntegerField,
    DateTimeField,
    DoesNotExist,
    IntegerField,
)
from slugify import slugify
from typing_extensions import Self
from yaml import dump

from spip2md.config import CFG
from spip2md.regexmaps import (
    ARTICLE_LINK,
    BLOAT,
    DOCUMENT_LINK,
    HTMLTAGS,
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


class SpipNormalized:
    # From SPIP database
    texte: str
    lang: str
    titre: str
    descriptif: str
    statut: str
    # profondeur: int
    # Custom
    obj_id: BigAutoField | int = 0  # same ID attribute name for all objects
    depth: IntegerField | int  # Equals `profondeur` for sections
    fileprefix: str  # String to prepend to written files
    parentdir: str  # Path from output dir to direct parent
    style: tuple[int, ...]  # Styles to apply to some elements of printed output

    def status(self) -> bool:
        return self.statut == "publie"

    def dest_directory(self, prepend: str = "", append: str = "") -> str:
        raise NotImplementedError(
            f"Subclasses need to implement directory(), params:{prepend}{append}"
        )

    def dest_filename(self, prepend: str = "", append: str = "") -> str:
        raise NotImplementedError(
            f"Subclasses need to implement dest_filename(), params:{prepend}{append}"
        )

    def dest_path(self) -> str:
        return self.dest_directory() + self.dest_filename()


class NormalizedSection(SpipNormalized, SpipRubriques):
    fileprefix: str = "_index"
    style = (BOLD, GREEN)  # Sections accent color is green

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_id = self.id_rubrique
        self.depth = self.profondeur


class NormalizedArticle(SpipNormalized, SpipArticles):
    fileprefix: str = "index"
    style = (BOLD, YELLOW)  # Articles accent color is yellow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_id = self.id_article


class NormalizedDocument(SpipNormalized, SpipDocuments):
    fileprefix: str = ""
    style = (BOLD, BLUE)  # Documents accent color is blue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_id = self.id_document


class WritableObject(SpipNormalized):
    translations: dict[str, Self]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Detect every language present in <multi> blocks of text
    # For each language in <multi> block, output a new object with the translation
    def translate_multi(self, text: str) -> dict[str, str]:
        # title: str = self.title()  # Memoize self title # WARNING recurses
        title: str = self.titre.strip()  # Memoize self title # WARNING recurses
        translations: dict[str, str] = {self.lang: text}  # Dict such as lang: text
        # for each langs of <multi> blocks, add its text to the corresponding dict key
        for block in MULTILANG_BLOCK.finditer(text):
            for lang in MULTILANGS.finditer(block.group(1)):
                if lang.group(1) == self.lang:
                    translations[self.lang] = translations[self.lang].replace(
                        block.group(), lang.group(2)
                    )
                elif lang.group(1) in translations:
                    translations[lang.group(1)] += lang.group(2)
                else:
                    translations[lang.group(1)] = lang.group(2)
                # Logs the translation
                translated: str = lang.group(2)[:50].strip()
                logging.info(f"{title} {lang.group(1)} translation: {translated}")
        return translations

    # Apply a mapping from regex maps
    @staticmethod
    def apply_mapping(text: str, mapping: tuple) -> str:
        if type(mapping) == tuple and len(mapping) > 0:
            if type(mapping[0]) == tuple and len(mapping[0]) > 0:
                if type(mapping[0][0]) == Pattern:
                    for old, new in mapping:
                        text = old.sub(new, text)
                else:
                    for old, new in mapping:
                        text = text.replace(old, new)
            elif type(mapping[0]) == Pattern:
                for old in mapping:
                    text = old.sub("", text)
            else:
                for old in mapping:
                    text = old.replace("", text)
        return text

    # Warn about unknown chars & replace them with config defined replacement
    def warn_unknown(self, text: str, unknown_mapping: tuple) -> str:
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

        for char in unknown_mapping:
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

    # Apply needed methods on text fields
    def convert_field(self, field: Optional[str], clean_html: bool = True) -> str:
        if field is None:
            return ""
        if len(field) == 0:
            return ""
        # Convert SPIP syntax to Markdown
        field = self.apply_mapping(field, SPIP_MARKDOWN)
        # Remove useless text
        field = self.apply_mapping(field, BLOAT)
        # Convert broken ISO encoding to UTF
        field = self.apply_mapping(field, ISO_UTF)
        if clean_html:
            # Delete remaining HTML tags in body WARNING
            field = self.apply_mapping(field, HTMLTAGS)
        # Warn about unknown chars
        field = self.warn_unknown(field, UNKNOWN_ISO)
        return field.strip()  # Strip whitespaces around text

    def title(self) -> str:
        return self.convert_field(self.titre)

    def description(self) -> str:
        return self.convert_field(self.descriptif)

    # Print one or more line(s) in which special elements are stylized
    def style_print(self, string: str, indent: bool = True, end: str = "\n") -> str:
        stylized: str = string
        for o in SPECIAL_OUTPUT:
            stylized = o.sub(esc(*self.style) + r"\1" + esc(), stylized)
        for w in WARNING_OUTPUT:
            stylized = w.sub(esc(*WARNING_STYLE) + r"\1" + esc(), stylized)
        if indent:
            stylized = "  " * self.depth + stylized
        print(stylized, end=end)
        # Return the stylized string
        return stylized

    # Print the message telling what is going to be done
    def begin_message(
        self, index: int, limit: int, prepend: str = "", step: int = 100
    ) -> list[str]:
        output: list[str] = []
        # Output the remaining number of objects to export every step object
        if index % step == 0:
            output.append(f"Exporting {limit-index}")
            output[-1] += f" level {self.depth}"
            s: str = "s" if limit - index > 1 else ""
            output[-1] += f" {type(self).__name__}{s}"
            # Print the output as the program goes
            self.style_print(output[-1])
        # Output the counter & title of the object being exported
        output.append(f"{index + 1}. ")
        output.append(prepend)
        if len(self.title()) == 0:
            output[-1] += "EMPTY NAME"
        else:
            output[-1] += self.title()
        # Print the output as the program goes
        self.style_print(output[-1], end="")
        return output

    # Write object to output destination
    def write(self) -> str:
        raise NotImplementedError("Subclasses need to implement write()")

    # Output information about file that was just exported
    def end_message(self, message: str | Exception) -> str:
        output: str = " -> "
        if type(message) is not str:
            output += "ERROR "
        # Print the output as the program goes
        self.style_print(output + str(message), indent=False)
        return output + str(message)


class Document(WritableObject, NormalizedDocument):
    class Meta:
        table_name: str = "spip_documents"

    # Get source name of this file
    def src_path(self, data_dir: Optional[str] = None) -> str:
        if data_dir is None:
            return CFG.data_dir + self.fichier
        return data_dir + self.fichier

    # Get directory of this object
    def dest_directory(self, prepend: str = "", append: str = "/") -> str:
        return self.parentdir + prepend + slugify(self.titre, max_length=100) + append

    # Get destination slugified name of this file
    def dest_filename(self, prepend: str = "", append: str = "") -> str:
        name, filetype = splitext(basename(str(self.fichier)))
        return slugify(prepend + name, max_length=100) + append + filetype

    # Write document to output destination
    def write(self) -> str:
        # Copy the document from it’s SPIP location to the new location
        return copyfile(self.src_path(), self.dest_path())


class RedactionalObject(WritableObject):
    id_trad: BigIntegerField | int
    id_rubrique: BigIntegerField | int
    # date: DateTimeField | str
    date: DateTimeField
    maj: str
    id_secteur: BigIntegerField | int
    extra: str
    langue_choisie: str
    # Custom
    prefix: str = "index"

    def replace_links(
        self,
        text: str,
        mapping: tuple,
        obj_type: type[NormalizedSection | NormalizedArticle | NormalizedDocument],
    ) -> str:
        for id_link, path_link in mapping:
            # print(f"Looking for links like {id_link}")
            for match in id_link.finditer(text):
                logging.info(f"Found document link {match.group()} in {self.titre}")
                try:
                    o: obj_type = obj_type.get(obj_type.obj_id == match.group(2))
                    # TODO get relative path
                    if len(match.group(1)) > 0:
                        repl: str = path_link.format(match.group(1), o.dest_path())
                    else:
                        repl: str = path_link.format(o.titre, o.dest_path())
                    logging.info(f"Translating link to {repl}")
                    text = text.replace(match.group(), repl)
                except DoesNotExist:
                    logging.warn(f"No object for link {match.group()} in {self.titre}")
                    text = text.replace(
                        match.group(), path_link.format("", "NOT FOUND"), 1
                    )
        return text

    def title(self) -> str:
        if self.texte is None:
            return ""
        if len(self.texte) == 0:
            return ""
        text: str = self.texte
        # Handle <multi> multi language blocks
        for lang, translation in self.translate_multi(text):
            if lang == self.lang:
                text = translation
            else:
                self.translations: dict[str, Self] = {}
                self.translations[lang] = deepcopy(self)
                self.translations[lang].titre = translation
        return self.convert_field(text)

    def text(self) -> str:
        if self.texte is None:
            return ""
        if len(self.texte) == 0:
            return ""
        text: str = self.texte
        # Handle <multi> multi language blocks
        for lang, translation in self.translate_multi(text):
            if lang == self.lang:
                text = translation
            else:
                self.translations: dict[str, Self] = {}
                self.translations[lang] = deepcopy(self)
                self.translations[lang].texte = translation
        # Replace ID based SPIP links with relative path links
        text = self.replace_links(text, DOCUMENT_LINK, Document)
        text = self.replace_links(text, ARTICLE_LINK, Article)
        text = self.replace_links(text, SECTION_LINK, Section)
        return self.convert_field(text)

    def ext(self) -> str:
        if self.extra is None:
            return ""
        if len(self.extra) == 0:
            return ""
        text: str = self.extra
        text = self.replace_links(text, ARTICLE_LINK, Article)
        text = self.replace_links(text, SECTION_LINK, Section)
        return self.convert_field(text)

    def choosen_language(self) -> bool:
        return self.langue_choisie == "oui"

    # Get related documents
    def documents(self) -> list[Document]:
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self.obj_id)
        )
        return documents

    # Get slugified directory of this object
    def dest_directory(self, prepend: str = "", append: str = "/") -> str:
        return self.parentdir + prepend + slugify(self.titre, max_length=100) + append

    # Get filename of this object
    def dest_filename(self) -> str:
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
            "spip_id": self.obj_id,
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
        if len(self.title()) > 0 and CFG.prepend_h1:
            body += "\n\n# " + self.title()
        # If there is a text, add the text preceded by two line breaks
        if len(self.text()) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self.text()
        # Same with an "extra" section
        if len(self.ext()) > 0:
            body += "\n\n# EXTRA\n\n" + self.ext()
        return body

    # Write object to output destination
    def write(self) -> str:
        # Make a directory for this object if there isn’t
        makedirs(self.dest_directory(), exist_ok=True)
        # Write the content of this object into a file named as self.filename()
        with open(self.dest_path(), "w") as f:
            f.write(self.content())
        return self.dest_path()


class Article(RedactionalObject, NormalizedArticle):
    class Meta:
        table_name: str = "spip_articles"

    def surtitle(self) -> str:
        return self.convert_field(str(self.surtitre))

    def subtitle(self) -> str:
        return self.convert_field(str(self.soustitre))

    def caption(self) -> str:
        return self.convert_field(str(self.chapo))

    def postscriptum(self) -> str:
        return self.convert_field(str(self.ps))

    def ublog(self) -> str:
        return self.convert_field(str(self.microblog))

    def accept_forum(self) -> bool:
        return self.accepter_forum == "oui"

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
        if len(self.caption()) > 0:
            body += "\n\n" + self.caption() + "\n\n***"
        # PS
        if len(self.postscriptum()) > 0:
            body += "\n\n# POST-SCRIPTUM\n\n" + self.postscriptum()
        # Microblog
        if len(self.ublog()) > 0:
            body += "\n\n# MICROBLOGGING\n\n" + self.ublog()
        return body

    def authors(self) -> list[SpipAuteurs]:
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self.obj_id)
        )


class Section(RedactionalObject, NormalizedSection):
    class Meta:
        table_name: str = "spip_rubriques"

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

    # Get articles of this section
    def articles(self) -> list[Article]:
        return (
            Article.select()
            .where((Article.id_rubrique == self.obj_id) & (Article.lang == self.lang))
            .order_by(Article.date.desc())
            # .limit(limit)
        )

    def write_tree(self, index: int, total: int) -> list[str | list[Any]]:
        # Define dictionary output to diplay
        output: list[str | list[Any]] = []
        # Print & add to output the message before the section write
        for m in self.begin_message(index, total):
            output.append(m)
        # Get this section’s articles & documents
        articles: list[Article] = self.articles()
        documents: list[Document] = self.documents()
        # Write this section & print the finish message of the section writing
        output[-1] += self.end_message(self.write())

        # Write this section’s articles and documents
        def write_loop(objects: list[Article] | list[Document]) -> list[str]:
            output: list[str] = []
            total = len(objects)
            for i, obj in enumerate(objects):
                obj.depth = self.depth + 1
                obj.parentdir = self.dest_directory()
                for m in obj.begin_message(i, total):
                    output.append(m)
                try:
                    output[-1] += obj.end_message(obj.write())
                except Exception as err:
                    output[-1] += obj.end_message(err)
            return output

        output.append(write_loop(articles))
        output.append(write_loop(documents))

        # Get all child section of this section
        child_sections: tuple[Section, ...] = (
            Section.select()
            .where(Section.id_parent == self.obj_id)
            .order_by(Section.date.desc())
        )
        nb: int = len(child_sections)
        # Do the same for subsections (write their entire subtree)
        for i, s in enumerate(child_sections):
            s.parentdir = self.dest_directory()
            output.append(s.write_tree(i, nb))
        return output
