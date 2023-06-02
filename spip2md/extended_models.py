# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
import logging
from os import makedirs
from os.path import basename, splitext
from re import Match, Pattern, finditer, search
from shutil import copyfile
from typing import Any, Optional

from peewee import (
    BigAutoField,
    BigIntegerField,
    DateTimeField,
    DoesNotExist,
)
from slugify import slugify
from typing_extensions import Self
from yaml import dump

from spip2md.config import CFG
from spip2md.regexmaps import (
    ARTICLE_LINK,
    BLOAT,
    CONFIGLANGS,
    DOCUMENT_LINK,
    HTMLTAGS,
    ISO_UTF,
    MULTILANG_BLOCK,
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
from spip2md.style import BOLD, CYAN, GREEN, WARNING_STYLE, YELLOW, esc

# Define recursive list type
RecursiveList = list["str | RecursiveList"]

# Define logger for this file’s logs
LOG = logging.getLogger(CFG.logname + ".models")


class SpipInterface:
    # From SPIP database
    texte: str
    lang: str
    titre: str
    descriptif: str
    statut: str
    profondeur: int
    # Converted fields
    _title: str
    _status: bool
    # Additional fields
    _id: BigAutoField | int = 0  # same ID attribute name for all objects
    # _depth: IntegerField | int  # Equals `profondeur` for sections
    _depth: int  # Equals `profondeur` for sections
    _fileprefix: str  # String to prepend to written files
    _parentdir: str  # Path from output dir to direct parent
    _style: tuple[int, ...]  # _styles to apply to some elements of printed output
    # memo: dict[str, str] = {}  # Memoïze values

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


class NormalizedSection(SpipInterface, SpipRubriques):
    _fileprefix: str = "_index"
    _style = (BOLD, GREEN)  # Sections accent color is green

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = self.id_rubrique
        self._depth = self.profondeur


class NormalizedArticle(SpipInterface, SpipArticles):
    _fileprefix: str = "index"
    _style = (BOLD, YELLOW)  # Articles accent color is yellow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = self.id_article


class NormalizedDocument(SpipInterface, SpipDocuments):
    _fileprefix: str = ""
    _style = (BOLD, CYAN)  # Documents accent color is blue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = self.id_document


class WritableObject(SpipInterface):
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
                LOG.warn(
                    f"Unknown char {char} found in {self.titre[:40]} at: {context}"
                )
                if CFG.unknown_char_replacement is not None:
                    LOG.warn(
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize converted fields beginning with underscore
        self._description: str = self.convert_field(self.descriptif)
        self._status = self.statut == "publie"

    # Apply post-init conversions and cancel the export if self not of the right lang
    def convert(self) -> None:
        self._title = self.convert_field(self.titre)

    # Print one or more line(s) in which special elements are stylized
    def style_print(
        self, string: str, indent: Optional[str] = "  ", end: str = "\n"
    ) -> str:
        stylized: str = string
        for o in SPECIAL_OUTPUT:
            stylized = o.sub(esc(*self._style) + r"\1" + esc(), stylized)
        for w in WARNING_OUTPUT:
            stylized = w.sub(esc(*WARNING_STYLE) + r"\1" + esc(), stylized)
        if indent is not None and len(indent) > 0:
            stylized = indent * self._depth + stylized
        print(stylized, end=end)
        # Return the stylized string in case
        return stylized

    # Print the message telling what is going to be done
    def begin_message(self, index: int, limit: int, step: int = 100) -> list[str]:
        output: list[str] = []
        # Output the remaining number of objects to export every step object
        if index % step == 0 and limit > 0:
            output.append(f"Exporting {limit-index}")
            output[-1] += f" level {self._depth}"
            s: str = "s" if limit - index > 1 else ""
            if hasattr(self, "lang"):
                output[-1] += f" {self.lang}"
            output[-1] += f" {type(self).__name__}{s}"
            # Print the output as the program goes
            self.style_print(output[-1])
        # Output the counter & title of the object being exported
        output.append(f"{index + 1}. ")
        if len(self._title) == 0:
            output[-1] += "EMPTY NAME"
        else:
            output[-1] += self._title
        # Print the output as the program goes
        # LOG.debug(f"Begin exporting {type(self).__name__} {output[-1]}")
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
        # LOG.debug(f"Finished exporting {type(self).__name__}: {message}")
        self.style_print(output + str(message), indent=None)
        return output + str(message)

    # Perform all the write steps of this object
    def write_all(
        self, parentdepth: int, parentdir: str, index: int, total: int
    ) -> RecursiveList:
        LOG.debug(f"Writing {type(self).__name__} `{self._title}`")
        output: RecursiveList = []
        self._depth = parentdepth + 1
        self._parentdir = parentdir
        for m in self.begin_message(index, total):
            output.append(m)
        try:
            output[-1] += self.end_message(self.write())
        except Exception as err:
            output[-1] += self.end_message(err)
        return output


class Document(WritableObject, NormalizedDocument):
    class Meta:
        table_name: str = "spip_documents"

    # Get source name of this file
    def src_path(self, data_dir: Optional[str] = None) -> str:
        if data_dir is None:
            return CFG.data_dir + self.fichier
        return data_dir + self.fichier

    # Get directory of this object
    def dest_directory(self, prepend: str = "", append: str = "") -> str:
        _id: str = str(self._id) + "-" if CFG.prepend_id else ""
        return (
            self._parentdir
            + prepend
            + slugify(_id + self._title, max_length=100)
            + append
        )

    # Get destination slugified name of this file
    def dest_filename(self, prepend: str = "", append: str = "") -> str:
        name, filetype = splitext(basename(str(self.fichier)))
        return slugify(prepend + name, max_length=100) + append + filetype

    # Write document to output destination
    def write(self) -> str:
        # Copy the document from it’s SPIP location to the new location
        return copyfile(self.src_path(), self.dest_path())

    # Perform all the write steps of this object
    def write_all(
        self, parentdepth: int, parentdir: str, index: int, total: int
    ) -> RecursiveList:
        self.convert()  # Apply post-init conversions
        return super().write_all(parentdepth, parentdir, index, total)


class LangNotFoundError(Exception):
    pass


class RedactionalObject(WritableObject):
    id_trad: BigIntegerField | int
    id_rubrique: BigIntegerField | int
    # date: DateTimeField | str
    date: DateTimeField
    maj: str
    id_secteur: BigIntegerField | int
    extra: str
    langue_choisie: str
    # Converted
    _text: str

    # Get rid of other lang than forced in text and modify lang to forced if found
    def translate_field(self, forced_lang: str, text: str) -> str:
        LOG.debug(f"Translating <multi> blocks of `{self._title}`")
        # for each <multi> blocks, keep only forced lang
        lang: Optional[Match[str]] = None
        for block in MULTILANG_BLOCK.finditer(text):
            lang = CONFIGLANGS[forced_lang].search(block.group(1))
            if lang is not None:
                # Log the translation
                trans: str = lang.group(1)[:50].strip()
                LOG.debug(
                    f"Keeping {forced_lang} translation of `{self._title}`: "
                    + f"`{trans}`, becoming its new lang"
                )
                text = text.replace(block.group(), lang.group(1))
                self.lang = forced_lang  # So write-all will not be cancelled
        if lang is None:
            LOG.debug(f"{forced_lang} not found in `{self._title}`")
        return text

    def replace_links(
        self,
        text: str,
        mapping: tuple,
        obj_type: type[NormalizedSection | NormalizedArticle | NormalizedDocument],
    ) -> str:
        for id_link, path_link in mapping:
            # print(f"Looking for links like {id_link}")
            for match in id_link.finditer(text):
                LOG.debug(f"Found document link {match.group()} in {self._title}")
                try:
                    o: obj_type = obj_type.get(obj_type._id == match.group(2))
                    # TODO get relative path
                    if len(match.group(1)) > 0:
                        repl: str = path_link.format(match.group(1), o.dest_path())
                    else:
                        repl: str = path_link.format(o._title, o.dest_path())
                    LOG.debug(f"Translating link to {repl}")
                    text = text.replace(match.group(), repl)
                except DoesNotExist:
                    LOG.warn(f"No object for link {match.group()} in {self._title}")
                    text = text.replace(
                        match.group(), path_link.format("", "NOT FOUND"), 1
                    )
        return text

    # Get slugified directory of this object
    def dest_directory(self, prepend: str = "", append: str = "/") -> str:
        _id: str = str(self._id) + "-" if CFG.prepend_id else ""
        return (
            self._parentdir
            + prepend
            + slugify(_id + self._title, max_length=100)
            + append
        )

    # Get filename of this object
    def dest_filename(self) -> str:
        return self._fileprefix + "." + self.lang + "." + CFG.export_filetype

    def convert_title(self, forced_lang: str) -> None:
        LOG.debug(f"Convert title of currently untitled {type(self).__name__}")
        if hasattr(self, "_title"):
            LOG.debug(f"{type(self).__name__} {self._title} _title is already set")
            return
        if self.titre is None:
            LOG.debug(f"{type(self).__name__} title is None")
            self._title = ""
            return
        if len(self.titre) == 0:
            LOG.debug(f"{type(self).__name__} title is empty")
            self._title = ""
            return
        self._title = self.titre.strip()
        self._title = self.translate_field(forced_lang, self._title)
        LOG.debug(f"Convert document links of `{self._title}` title")
        self._title = self.replace_links(self._title, DOCUMENT_LINK, Document)
        LOG.debug(f"Convert article links of `{self._title}` title")
        self._title = self.replace_links(self._title, ARTICLE_LINK, Article)
        LOG.debug(f"Convert section links of `{self._title}` title")
        self._title = self.replace_links(self._title, SECTION_LINK, Section)
        LOG.debug(f"Apply conversions to `{self._title}` title")
        self._title = self.convert_field(self._title)

    def convert_text(self, forced_lang: str) -> None:
        LOG.debug(f"Convert text of `{self._title}`")
        if hasattr(self, "_text"):
            LOG.debug(f"{type(self).__name__} {self._title} _text is already set")
            return
        if self.texte is None:
            LOG.debug(f"{type(self).__name__} {self._title} text is None")
            self._text = ""
            return
        if len(self.texte) == 0:
            LOG.debug(f"{type(self).__name__} {self._title} text is empty")
            self._text = ""
            return
        self._text = self.translate_field(forced_lang, self.texte.strip())
        LOG.debug(f"Convert document links of `{self._title}`")
        self._text = self.replace_links(self._text, DOCUMENT_LINK, Document)
        LOG.debug(f"Convert article links of `{self._title}`")
        self._text = self.replace_links(self._text, ARTICLE_LINK, Article)
        LOG.debug(f"Convert section links of `{self._title}`")
        self._text = self.replace_links(self._text, SECTION_LINK, Section)
        self._text = self.convert_field(self._text)

    def convert_extra(self) -> None:
        LOG.debug(f"Convert extra of `{self._title}`")
        if hasattr(self, "_extra"):
            LOG.debug(f"{type(self).__name__} {self._title} _extra is already set")
            return
        if self.extra is None:
            LOG.debug(f"{type(self).__name__} {self._title} extra is None")
            self._extra = ""
            return
        if len(self.extra) == 0:
            LOG.debug(f"{type(self).__name__} {self._title} extra is empty")
            self._extra = ""
            return
        LOG.debug(f"Convert article links of `{self._title}`")
        self._extra = self.replace_links(self.extra, ARTICLE_LINK, Article)
        LOG.debug(f"Convert section links of `{self._title}`")
        self._extra = self.replace_links(self._extra, SECTION_LINK, Section)
        self._extra = self.convert_field(self._extra)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize converted fields, beginning with underscore
        self._choosen_language = self.langue_choisie == "oui"

    # Get related documents
    def documents(self) -> tuple[Document]:
        LOG.debug(f"Initialize documents of `{self._title}`")
        documents = (
            Document.select()
            .join(
                SpipDocumentsLiens,
                on=(Document.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self._id)
        )
        return documents

    # Get the YAML frontmatter string
    def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        # LOG.debug(f"Write frontmatter of `{self._title}`")
        meta: dict[str, Any] = {
            "lang": self.lang,
            "translationKey": self.id_trad,
            "title": self._title,
            "publishDate": self.date,
            "lastmod": self.maj,
            "draft": self._status,
            "description": self._description,
            # Debugging
            "spip_id_secteur": self.id_secteur,
            "spip_id": self._id,
        }
        if append is not None:
            return dump(meta | append, allow_unicode=True)
        else:
            return dump(meta, allow_unicode=True)

    # Get file text content
    def content(self) -> str:
        # LOG.debug(f"Write content of `{self._title}`")
        # Start the content with frontmatter
        body: str = "---\n" + self.frontmatter() + "---"
        # Add the title as a Markdown h1
        if len(self._title) > 0 and CFG.prepend_h1:
            body += "\n\n# " + self._title
        # If there is a text, add the text preceded by two line breaks
        if len(self._text) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self._text
        # Same with an "extra" section
        if len(self._extra) > 0:
            body += "\n\n# EXTRA\n\n" + self._extra
        return body

    # Write object to output destination
    def write(self) -> str:
        # Make a directory for this object if there isn’t
        makedirs(self.dest_directory(), exist_ok=True)
        # Write the content of this object into a file named as self.filename()
        with open(self.dest_path(), "w") as f:
            f.write(self.content())
        return self.dest_path()

    # Apply post-init conversions and cancel the export if self not of the right lang
    def convert(self, forced_lang: str) -> None:
        self.convert_title(forced_lang)
        self.convert_text(forced_lang)
        self.convert_extra()
        if self.lang != forced_lang:
            raise LangNotFoundError(
                f"`{self._title}` lang is {self.lang} instead of the wanted"
                + f" {forced_lang} and it don’t contains"
                + f" {forced_lang} translation in Markup either"
            )

    # Write all the children of this object
    def write_documents(self) -> RecursiveList:
        LOG.debug(f"Writing children of {type(self).__name__} `{self._title}`")
        output: RecursiveList = []
        children = self.documents()
        total = len(children)
        for i, obj in enumerate(children):
            try:
                output.append(
                    obj.write_all(self._depth, self.dest_directory(), i, total)
                )
            except LangNotFoundError:
                pass  # For now, do nothing
        return output


class Article(RedactionalObject, NormalizedArticle):
    class Meta:
        table_name: str = "spip_articles"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize converted fields beginning with underscore
        self._accept_forum = self.accepter_forum == "oui"
        self._surtitle = self.convert_field(str(self.surtitre))
        self._subtitle = self.convert_field(str(self.soustitre))
        self._caption = self.convert_field(str(self.chapo))
        self._ps = self.convert_field(str(self.ps))
        self._microblog = self.convert_field(str(self.microblog))

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
        if len(self._caption) > 0:
            body += "\n\n" + self._caption + "\n\n***"
        # PS
        if len(self._ps) > 0:
            body += "\n\n# POST-SCRIPTUM\n\n" + self._ps
        # Microblog
        if len(self._microblog) > 0:
            body += "\n\n# MICROBLOGGING\n\n" + self._microblog
        return body

    def authors(self) -> list[SpipAuteurs]:
        LOG.debug(f"Initialize authors of `{self._title}`")
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self._id)
        )

    # Perform all the write steps of this object
    def write_all(
        self, forced_lang: str, parentdepth: int, parentdir: str, index: int, total: int
    ) -> RecursiveList:
        self.convert(forced_lang)
        output: RecursiveList = super().write_all(parentdepth, parentdir, index, total)
        output.append(self.write_documents())
        return output


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
    def articles(self, limit: int = 10**6) -> tuple[Article]:
        LOG.debug(f"Initialize articles of `{self._title}`")
        return (
            Article.select()
            .where(Article.id_rubrique == self._id)
            .order_by(Article.date.desc())
            .limit(limit)
        )

    # Get subsections of this section
    def sections(self, limit: int = 10**6) -> tuple[Self]:
        LOG.debug(f"Initialize subsections of `{self._title}`")
        return (
            Section.select()
            .where(Section.id_parent == self._id)
            .order_by(Section.date.desc())
            .limit(limit)
        )

    # Write all the children of this object
    def write_children(self, forcedlang: str) -> RecursiveList:
        super().write_documents()
        LOG.debug(f"Writing children of {type(self).__name__} `{self._title}`")
        output: RecursiveList = []
        for children in (self.articles(), self.sections()):
            total = len(children)
            for i, obj in enumerate(children):
                try:
                    output.append(
                        obj.write_all(
                            forcedlang, self._depth, self.dest_directory(), i, total
                        )
                    )
                except LangNotFoundError:
                    pass  # For now, do nothing
        return output

    # Perform all the write steps of this object
    def write_all(
        self, forced_lang: str, parentdepth: int, parentdir: str, index: int, total: int
    ) -> RecursiveList:
        self.convert(forced_lang)
        output: RecursiveList = super().write_all(parentdepth, parentdir, index, total)
        output.append(self.write_children(forced_lang))
        return output
