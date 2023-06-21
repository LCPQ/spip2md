"""
This file is part of spip2md.
Copyright (C) 2023 LCPQ/Guilhem Fauré

spip2md is free software: you can redistribute it and/or modify it under the terms of
the GNU General Public License version 2 as published by the Free Software Foundation.

spip2md is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with spip2md.
If not, see <https://www.gnu.org/licenses/>.


This file contains the core classes of spip2md that models internal objects of spip
and methods to convert them to Markdown + YAML, static site structure
"""
import logging
from os import listdir, mkdir
from os.path import basename, isfile, splitext
from re import I, Match, Pattern, finditer, match, search
from re import error as re_error
from shutil import copyfile
from typing import Any, Optional

from peewee import (
    BigAutoField,
    BigIntegerField,
    DateTimeField,
    DoesNotExist,
)
from slugify import slugify
from yaml import dump

from spip2md.config import Configuration
from spip2md.regexmaps import (
    ARTICLE_LINK,
    BLOAT,
    CONFIG_LANGS,
    DOCUMENT_LINK,
    HTMLTAGS,
    IMAGE_LINK,
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


# Declare exceptions
class IgnoredPatternError(Exception):
    pass


class LangNotFoundError(Exception):
    pass


class DontExportDraftError(Exception):
    pass


class DontExportEmptyError(Exception):
    pass


# class ConvertableObject:
#     # From SPIP database
#     texte: str
#     lang: str
#     titre: str
#     descriptif: str
#     statut: str
#     profondeur: int
#     # Converted fields
#     _storage_title: str  # Title with which directories names are built
#     _draft: bool
#     # Additional fields
#     _id: BigAutoField | int = 0  # same ID attribute name for all objects
#     _depth: int  # Equals `profondeur` for sections
#     _fileprefix: str  # String to prepend to written files
#     _storage_parentdir: str  # Path from output dir to direct parent
#     _style: tuple[int, ...]  # _styles to apply to some elements of printed output
#     _storage_title_append: int = 0  # Append a number to storage title if > 0
#
#     # Warn about unknown chars & replace them with config defined replacement
#     def warn_unknown(self, text: str, unknown_mapping: tuple) -> str:
#         # Return unknown char surrounded by context_length chars
#         def unknown_chars_context(text: str, char: str, context_len: int = 24) -> str:
#             context: str = r".{0," + str(context_len) + r"}"
#             m = search(
#                 context + r"(?=" + char + r")" + char + context,
#                 text,
#             )
#             if m is not None:
#                 return m.group()
#             else:
#                 return char
#
#         for char in unknown_mapping:
#             lastend: int = 0
#             for m in finditer("(" + char + ")+", text):
#                 context: str = unknown_chars_context(text[lastend:], char)
#                 LOG.warn(
#                     f"Unknown char {char} in file {self.dest_path()} at: {context}"
#                 )
#                 if CFG.unknown_char_replacement is not None:
#                     LOG.warn(
#                         f"Replacing {m.group()} with {CFG.unknown_char_replacement}"
#                     )
#                     text = text.replace(m.group(), CFG.unknown_char_replacement, 1)
#                 lastend = m.end()
#         return text
#
#     # Apply post-init conversions and cancel the export if self not of the right lang
#     def convert(self, forced_lang: Optional[str] = None) -> None:
#         self._storage_title = self.convert_field(self.titre)
#         # Warn about unknown chars
#         self._storage_title = self.warn_unknown(self._storage_title, UNKNOWN_ISO)
#         if not CFG.export_drafts and self._draft:
#             raise DontExportDraftError(f"{self.titre} is a draft, cancelling export")
#
#     def dest_directory(self) -> str:
#         raise NotImplementedError("Subclasses need to implement directory()")
#
#     def dest_filename(self, prepend: str = "", append: str = "") -> str:
#         raise NotImplementedError(
#             f"Subclasses need to implement dest_filename(), params:{prepend}{append}"
#         )
#
#     def dest_path(self) -> str:
#         return self.dest_directory() + self.dest_filename()
#
#     # Print one or more line(s) in which special elements are stylized
#     def style_print(
#         self, string: str, indent: Optional[str] = "  ", end: str = "\n"
#     ) -> str:
#         stylized: str = string
#         for o in SPECIAL_OUTPUT:
#             stylized = o.sub(esc(*self._style) + r"\1" + esc(), stylized)
#         for w in WARNING_OUTPUT:
#             stylized = w.sub(esc(*WARNING_STYLE) + r"\1" + esc(), stylized)
#         if indent is not None and len(indent) > 0:
#             stylized = indent * self._depth + stylized
#         print(stylized, end=end)
#         # Return the stylized string in case
#         return stylized
#
#     # Print the message telling what is going to be done
#     def begin_message(self, index: int, limit: int, step: int = 100) -> str:
#         # Output the remaining number of objects to export every step object
#         if index % step == 0 and limit > 0:
#             counter: str = f"Exporting {limit-index} level {self._depth}"
#             s: str = "s" if limit - index > 1 else ""
#             if hasattr(self, "lang"):
#                 counter += f" {self.lang}"
#             counter += f" {type(self).__name__}{s}"
#             # Print the output as the program goes
#             self.style_print(counter)
#         # Output the counter & title of the object being exported
#         msg: str = f"{index + 1}. "
#         if len(self._storage_title) == 0:
#             msg += "EMPTY NAME"
#         else:
#             msg += self._storage_title
#         # Print the output as the program goes
#         # LOG.debug(f"Begin exporting {type(self).__name__} {output[-1]}")
#         self.style_print(msg, end="")
#         return msg
#
#     # Write object to output destination
#     def write(self) -> str:
#         raise NotImplementedError("Subclasses need to implement write()")
#
#     # Output information about file that was just exported
#     def end_message(self, message: str | Exception) -> str:
#         output: str = " -> "
#         if type(message) is FileNotFoundError:
#             output += "ERROR: NOT FOUND: "
#         elif type(message) is DoesNotExist:
#             output += "ERROR: NO DESTINATION DIR: "
#         elif type(message) is DontExportDraftError:
#             output += "ERROR: NOT EXPORTING DRAFT: "
#         elif type(message) is DontExportEmptyError:
#             output += "ERROR: NOT EXPORTING EMPTY: "
#         elif type(message) is not str:
#             output += "ERROR: UNKNOWN: "
#         # Print the output as the program goes
#         # LOG.debug(f"Finished exporting {type(self).__name__}: {message}")
#         self.style_print(output + str(message), indent=None)
#         return output + str(message)
#
#     # Perform all the write steps of this object
#     def write_all(
#         self,
#         parentdepth: int,
#         storage_parentdir: str,
#         index: int,
#         total: int,
#         parenturl: str,
#         forced_lang: Optional[str] = None,
#     ) -> str:
#         self._depth = parentdepth + 1
#         self._storage_parentdir = storage_parentdir
#         self._parenturl = parenturl
#         self.convert(forced_lang)  # Post init convertions
#         LOG.debug(f"Writing {type(self).__name__} `{self._storage_title}`")
#         output: str = self.begin_message(index, total)
#         try:
#             output += self.end_message(self.write())
#         except (
#             LangNotFoundError,
#             DontExportDraftError,
#             DontExportEmptyError,
#             IgnoredPatternError,
#             FileNotFoundError,
#         ) as err:
#             output += self.end_message(err)
#         return output


class ConvertableDocument:
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _spip_obj: SpipDocuments  # The Spip Article this is representing
    # Converted fields
    _src: str  # URL
    _slug: str = ""  # URL

    # _fileprefix: str = ""
    # _style = (BOLD, CYAN)  # Documents accent color is blue

    def __init__(self, spip_obj: SpipDocuments, cfg: Configuration):
        self._log_c = logging.getLogger(cfg.name + ".convert.document")
        self._spip_obj = spip_obj
        self._id = spip_obj.id_document
        # Define source name of this file
        self._src = cfg.data_dir + spip_obj.fichier
        # Define destination name of this file
        name, filetype = splitext(basename(str(spip_obj.fichier)))
        prepend: str = str(spip_obj.id_document) + "-" if self._cfg.prepend_id else ""
        return slugify(prepend + name, max_length=cfg.title_max_length) + filetype

    # Get directory of this object
    # def dest_directory(self, prepend: str = "", append: str = "") -> str:
    #     _id: str = str(self._id) + "-" if self._cfg.prepend_id else ""
    #     return (
    #         self._storage_parentdir
    #         + prepend
    #         + slugify(_id + self._storage_title, max_length=100)
    #         + append
    #     )

    # Get destination slugified name of this file
    # def dest_filename(self, prepend: str = "", append: str = "") -> str:
    #     name, filetype = splitext(basename(str(self._src)))
    #     return slugify(prepend + name, max_length=100) + append + filetype

    # Write document to output destination
    # def write(self) -> str:
    #     # Copy the document from it’s SPIP location to the new location
    #     return copyfile(self.src_path(), self.dest_path())

    # Perform all the write steps of this object
    # def write_all(
    #     self,
    #     parentdepth: int,
    #     storage_parentdir: str,
    #     index: int,
    #     total: int,
    #     forcedlang: Optional[str] = None,
    #     parenturl: str = "",
    # ) -> str:
    #     # self.convert()  # Apply post-init conversions
    #     LOG.debug(
    #         f"Document {self._storage_title} don’t care about forcedlang {forcedlang}"
    #     )
    #     LOG.debug(
    #         f"Document {self._storage_title} doesn’t care about parenturl {parenturl}"
    #     )
    #     return super().write_all(
    #         parentdepth, storage_parentdir, index, total, parenturl
    #     )


class ConvertableArticle:
    # id_trad: BigIntegerField | BigAutoField | int
    # id_rubrique: BigAutoField | int
    # date: DateTimeField | str
    # date: DateTimeField
    # maj: str
    # id_secteur: BigIntegerField | int
    # extra: str
    # langue_choisie: str
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _children: tuple[
        "ConvertableSection | ConvertableArticle | ConvertableDocument", ...
    ]  # sub-sections, documents, articles
    _spip_obj: SpipArticles  # The Spip Article this is representing
    _lang: str
    _fileprefix: str = "index"
    # Converted fields
    _surtitle: str  # Content
    _title: str  # Content
    _subtitle: str  # Content
    _description: str  # Content
    _caption: str  # Content
    _extra: str  # Content
    _text: str  # Content
    _slug: str  # URL
    _meta: dict[str, str | int | bool | None]  # Metadata dictionary

    # _style = (BOLD, YELLOW)  # Articles accent color is yellow

    def documents(self, limit: int = 10**3):
        self._log_c.debug("Initialize documents")
        return (
            SpipDocuments.select()
            .join(
                SpipDocumentsLiens,
                on=(SpipDocuments.id_document == SpipDocumentsLiens.id_document),
            )
            .where(SpipDocumentsLiens.id_objet == self._id)
            .limit(limit)
        )

    def children(self):
        self._children = tuple(
            ConvertableDocument(d, self._cfg) for d in self.documents()
        )

    def __init__(self, spip_obj: SpipArticles, forced_lang: str, cfg: Configuration):
        self._log_c = logging.getLogger(cfg.name + ".convert.article")
        self._spip_obj = spip_obj
        self._id = spip_obj.id_article
        self._lang = forced_lang
        self._draft = spip_obj.statut != "publie"
        self.children()

    def authors(self) -> tuple[SpipAuteurs, ...]:
        self._log_c.debug("Initialize authors")
        return (
            SpipAuteurs.select()
            .join(
                SpipAuteursLiens,
                on=(SpipAuteurs.id_auteur == SpipAuteursLiens.id_auteur),
            )
            .where(SpipAuteursLiens.id_objet == self._id)
        )

    # # Get the YAML frontmatter string
    # def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
    #     # LOG.debug(f"Write frontmatter of `{self._title}`")
    #     meta: dict[str, Any] = {
    #         "lang": self.lang,
    #         "translationKey": self.id_trad if self.id_trad != 0 else self._id,
    #         "title": self._url_title,
    #         "publishDate": self.date,
    #         "lastmod": self.maj,
    #         "draft": self._draft,
    #         "description": self._description,
    #     }
    #     # Add debugging meta if needed
    #     if CFG.debug_meta:
    #         meta = meta | {
    #             "spip_id": self._id,
    #             "spip_id_secteur": self.id_secteur,
    #         }
    #     # Add url if different of directory
    #     if self.url() not in self.dest_directory():
    #         meta = meta | {"url": self.url()}
    #     if append is not None:
    #         return dump(meta | append, allow_unicode=True)
    #     else:
    #         return dump(meta, allow_unicode=True)

    # Build metadata dictionary that can be outputted as YAML
    def metadata(self):
        self._meta = {
            "lang": str(self.lang),
            "translationKey": int(
                self._spip_obj.id_trad if self._spip_obj.id_trad != 0 else self._id
            ),
            "title": str(self._title),
            "publishDate": str(self._spip_obj.date),
            "lastmod": str(self._spip_obj.maj),
            "draft": self._draft,
            "description": self._description,
        }
        # Add debugging meta if needed
        if self._cfg.debug:
            self._meta |= {
                "id": int(self._id),
                "spip_id_secteur": int(self._spip_obj.id_secteur),
            }

    # Apply a mapping from regex maps
    @staticmethod
    def apply_mapping(text: str, mapping: tuple, keep_markup: bool = True) -> str:
        if type(mapping) == tuple and len(mapping) > 0:
            if type(mapping[0]) == tuple and len(mapping[0]) > 0:
                if type(mapping[0][0]) == Pattern:  # Mostly for syntax conversion
                    for old, new in mapping:
                        if keep_markup:
                            text = old.sub(new, text)
                        else:
                            try:
                                text = old.sub(r"\1", text)
                            except re_error:
                                text = old.sub("", text)
                else:
                    for old, new in mapping:  # Mostly for broken encoding
                        text = text.replace(old, new)
            elif type(mapping[0]) == Pattern:
                for old in mapping:
                    text = old.sub("", text)
            else:
                for old in mapping:
                    text = text.replace(old, "")
        return text

    # Apply needed methods on text fields
    def convert_field(self, field: str) -> str:
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
        return field.strip()  # Strip whitespaces around text

    # Convert Spip syntax to Markdown on self then each children
    def convert(self):
        self._title = self.convert_field(str(self._spip_obj.titre))
        self._surtitle = self.convert_field(str(self._spip_obj.surtitre))
        self._subtitle = self.convert_field(str(self._spip_obj.soustitre))
        self._caption = self.convert_field(str(self._spip_obj.chapo))
        self._description = self.convert_field(str(self._spip_obj.descriptif))
        self._text = self.convert_field(str(self._spip_obj.texte))
        self._extra = self.convert_field(str(self._spip_obj.extra))
        # Useless but keep them
        # self._ps = self.convert_field(str(self._spip_obj.ps))
        # self._microblog = self.convert_field(str(self._spip_obj.microblog))
        # self._accept_forum = self._spip_obj.accepter_forum == "oui"
        # self._choosen_language = self._spip_obj.langue_choisie == "oui"

    # Get rid of other lang than forced in text and modify lang to forced if found
    def translate_multi(
        self, forced_lang: str, text: str, change_lang: bool = True
    ) -> str:
        # LOG.debug(f"Translating <multi> blocks of `{self._url_title}`")
        # for each <multi> blocks, keep only forced lang
        lang: Optional[Match[str]] = None
        for block in MULTILANG_BLOCK.finditer(text):
            lang = CONFIG_LANGS[forced_lang].search(block.group(1))
            if lang is not None:
                # Log the translation
                trans: str = lang.group(1)[:50].strip()
                self._log_c.debug(
                    f"Keeping {forced_lang} translation of `{self._url_title}`: "
                    + f"`{trans}`"
                )
                if change_lang:
                    self.lang = forced_lang  # So write-all will not be cancelled
                # Replace the mutli blocks with the text in the proper lang
                text = text.replace(block.group(), lang.group(1))
        if lang is None:
            self._log_c.debug(f"{forced_lang} not found")
        return text

    # Keep only one relevant language for self then each children
    def translate(self):
        if self._lang != self._spip_obj.lang:  # WARNING not the solution
            raise LangNotFoundError(
                f"`{self._url_title}` lang is {self.lang} instead of the wanted"
                + f" {self._lang} and it don’t contains"
                + f" {self._lang} translation in Markup either"
            )
        # Define slug
        self._slug = (
            slugify(self._title, max_length=self._cfg.title_max_length)
            + "/"
            + self._fileprefix
            + "."
            + self.lang
            + "."
            + self._cfg.export_filetype
        )

    # WARNING symplify a lot this
    def replace_links(self, text: str) -> str:
        class LinkMappings:
            _link_types = IMAGE_LINK, DOCUMENT_LINK, SECTION_LINK, ARTICLE_LINK

            def __iter__(self):
                self._type_cursor = 0
                self._link_cursor = -1
                return self

            @staticmethod
            def getdocument(obj_id: int) -> Document:
                doc: Document = Document.get(Document.id_document == obj_id)
                doc.convert()
                return doc

            @staticmethod
            def getsection(obj_id: int) -> Section:
                sec: Section = Section.get(Section.id_rubrique == obj_id)
                sec.convert(self.lang)
                return sec

            @staticmethod
            def getarticle(obj_id: int) -> Article:
                art: Article = Article.get(Article.id_article == obj_id)
                art.convert(self.lang)
                return art

            _obj_getters = getdocument, getdocument, getsection, getarticle

            def __next__(self):
                self._link_cursor += 1
                # If we reach end of current link type, pass to the beginning of next
                if self._link_cursor >= len(self._link_types[self._type_cursor]):
                    self._link_cursor = 0
                    self._type_cursor += 1

                if self._type_cursor >= len(self._link_types):
                    raise StopIteration

                return (
                    self._link_types[self._type_cursor][self._link_cursor],
                    self._obj_getters[self._type_cursor],
                    "!" if self._type_cursor == 0 else "",
                )

        for link, getobj, prepend in LinkMappings():
            # LOG.debug(f"Looking for {link} in {text}")
            for m in link.finditer(text):
                LOG.debug(f"Found internal link {m.group()} in {self._url_title}")
                try:
                    LOG.debug(
                        f"Searching for object of id {m.group(2)} with "
                        + getobj.__name__
                    )
                    o: "Document | Article | Section" = getobj(int(m.group(2)))
                    # TODO get full relative path for sections and articles
                    # TODO rewrite links markup (bold/italic) after stripping
                    if len(m.group(1)) > 0:
                        repl = f"{prepend}[{m.group(1)}]({o.dest_filename()})"
                    else:
                        repl = f"{prepend}[{o._storage_title}]({o.dest_filename()})"
                    LOG.debug(
                        f"Translate link {m.group()} to {repl} in {self._url_title}"
                    )
                    text = text.replace(m.group(), repl)
                except DoesNotExist:
                    LOG.warn(f"No object for link {m.group()} in {self._url_title}")
                    text = text.replace(m.group(), prepend + "[](NOT FOUND)", 1)
        return text

    # Repair internal links & embeds for self then each children
    def link(self):
        pass

    # Get file text content
    def content(self) -> str:
        # LOG.debug(f"Write content of `{self._title}`")
        # Start the content with frontmatter
        body: str = "---\n" + self.frontmatter() + "---"
        # Add the title as a Markdown h1
        if self._url_title is not None and len(self._url_title) > 0 and CFG.prepend_h1:
            body += "\n\n# " + self._url_title
        # If there is a text, add the text preceded by two line breaks
        if len(self._text) > 0:
            # Remove remaining HTML after & append to body
            body += "\n\n" + self._text
        elif not CFG.export_empty:
            raise DontExportEmptyError
        # Same with an "extra" section
        if len(self._extra) > 0:
            body += "\n\n# EXTRA\n\n" + self._extra
        return body

    def clean(self):
        # Delete remaining HTML tags if needed
        if self._cfg.remove_html:
            self._title = self.apply_mapping(
                self._title, HTMLTAGS, self._cfg.metadata_markup
            )
            self._surtitle = self.apply_mapping(
                self._surtitle, HTMLTAGS, self._cfg.metadata_markup
            )
            self._subtitle = self.apply_mapping(
                self._subtitle, HTMLTAGS, self._cfg.metadata_markup
            )
            self._caption = self.apply_mapping(self._caption, HTMLTAGS)
            self._text = self.apply_mapping(self._text, HTMLTAGS)
            self._extra = self.apply_mapping(self._extra, HTMLTAGS)

    def convert_title(self, forced_lang: str) -> None:
        LOG.debug(f"Convert title of currently untitled {type(self).__name__}")
        if hasattr(self, "_title"):
            LOG.debug(f"{type(self).__name__} {self._url_title} _title is already set")
            return
        if self.titre is None:
            LOG.debug(f"{type(self).__name__} title is None")
            self._url_title = ""
            return
        if len(self.titre) == 0:
            LOG.debug(f"{type(self).__name__} title is empty")
            self._url_title = ""
            return
        self._url_title = self.titre.strip()
        # Set storage title to language of storage lang if different
        storage_lang: str = (
            CFG.storage_language if CFG.storage_language is not None else forced_lang
        )
        LOG.debug(
            f"Searching for {storage_lang} in <multi> blocks of `{self._url_title}`"
            + " storage title"
        )
        self._storage_title = self.translate_multi(
            storage_lang,
            self._url_title,
            False,
        )
        LOG.debug(
            f"Searching for {forced_lang} in <multi> blocks of `{self._url_title}`"
            + " URL title"
        )
        self._url_title = self.translate_multi(forced_lang, self._url_title)
        LOG.debug(f"Convert internal links of {self.lang} `{self._url_title}` title")
        self._storage_title = self.replace_links(self._storage_title)
        self._url_title = self.replace_links(self._url_title)
        LOG.debug(f"Apply conversions to {self.lang} `{self._url_title}` title")
        self._storage_title = self.convert_field(self._storage_title)
        self._url_title = self.convert_field(self._url_title, CFG.metadata_markup)
        for p in CFG.ignore_patterns:
            for title in (self._storage_title, self._url_title):
                m = match(p, title, I)
                if m is not None:
                    raise IgnoredPatternError(
                        f"{self._url_title} matches with ignore pattern {p}, ignoring"
                    )
        # Warn about unknown chars
        self._storage_title = self.warn_unknown(self._storage_title, UNKNOWN_ISO)
        self._url_title = self.warn_unknown(self._url_title, UNKNOWN_ISO)

    def convert_text(self, forced_lang: str) -> None:
        LOG.debug(f"Convert text of `{self._url_title}`")
        if hasattr(self, "_text"):
            LOG.debug(f"{type(self).__name__} {self._url_title} _text is already set")
            return
        if self.texte is None:
            LOG.debug(f"{type(self).__name__} {self._url_title} text is None")
            self._text = ""
            return
        if len(self.texte) == 0:
            LOG.debug(f"{type(self).__name__} {self._url_title} text is empty")
            self._text = ""
            return
        self._text = self.translate_multi(forced_lang, self.texte.strip())
        LOG.debug(f"Convert internal links of {self.lang} `{self._url_title}` text")
        self._text = self.replace_links(self._text)
        LOG.debug(f"Apply conversions to {self.lang} `{self._url_title}` text")
        self._text = self.convert_field(self._text)
        # Warn about unknown chars
        self._text = self.warn_unknown(self._text, UNKNOWN_ISO)

    def convert_extra(self) -> None:
        LOG.debug(f"Convert extra of `{self._url_title}`")
        if hasattr(self, "_extra"):
            LOG.debug(f"{type(self).__name__} {self._url_title} _extra is already set")
            return
        if self.extra is None:
            LOG.debug(f"{type(self).__name__} {self._url_title} extra is None")
            self._extra = ""
            return
        if len(self.extra) == 0:
            LOG.debug(f"{type(self).__name__} {self._url_title} extra is empty")
            self._extra = ""
            return
        LOG.debug(f"Convert internal links of {self.lang} `{self._url_title}` extra")
        self._extra = self.replace_links(self._extra)
        LOG.debug(f"Apply conversions to {self.lang} `{self._url_title}` extra")
        self._extra = self.convert_field(self._extra, CFG.metadata_markup)
        # Warn about unknown chars
        self._extra = self.warn_unknown(self._extra, UNKNOWN_ISO)

    # # Get this object url, or none if it’s the same as directory
    # def url(self) -> str:
    #     _id: str = str(self._id) + "-" if CFG.prepend_id else ""
    #     counter: str = (
    #         "_" + str(self._storage_title_append)
    #         if self._storage_title_append > 0
    #         else ""
    #     )
    #     # Return none if url will be the same as directory
    #     return (
    #         self._parenturl
    #         + slugify(_id + self._url_title, max_length=CFG.title_max_length)
    #         + counter
    #         + r"/"
    #     )

    # # Get slugified directory of this object
    # def dest_directory(self) -> str:
    #     _id: str = str(self._id) + "-" if CFG.prepend_id else ""
    #     counter: str = (
    #         "_" + str(self._storage_title_append)
    #         if self._storage_title_append > 0
    #         else ""
    #     )
    #     directory: str = self._storage_parentdir + slugify(
    #         _id + self._storage_title,
    #         max_length=CFG.title_max_length,
    #     )
    #     return directory + counter + r"/"
    #
    # # Get filename of this object
    # def dest_filename(self) -> str:
    #     return self._fileprefix + "." + self.lang + "." + CFG.export_filetype

    # # Write all the documents of this object
    # def write_children(
    #     self,
    #     children: tuple[Document] | tuple[Any],
    #     forcedlang: str,
    # ) -> list[str]:
    #     LOG.debug(f"Writing documents of {type(self).__name__} `{self._url_title}`")
    #     output: list[str] = []
    #     total = len(children)
    #     i = 0
    #     for obj in children:
    #         try:
    #             output.append(
    #                 obj.write_all(
    #                     self._depth,
    #                     self.dest_directory(),
    #                     i,
    #                     total,
    #                     forcedlang,
    #                     self.url(),
    #                 )
    #             )
    #             i += 1
    #         except (
    #             LangNotFoundError,
    #             DontExportDraftError,
    #             DontExportEmptyError,
    #             IgnoredPatternError,
    #         ) as err:
    #             LOG.debug(err)
    #     return output

    # # Write object to output destination
    # def write(self) -> str:
    #     # Make a directory for this object if there isn’t
    #     # If it cannot for incompatibility, try until it can
    #     incompatible: bool = True
    #     while incompatible:
    #         directory: str = self.dest_directory()
    #         try:
    #             mkdir(directory)
    #             break
    #         except FileExistsError:
    #             # If not stated incompatible with the following, will write in this dir
    #             incompatible = False
    #             # Create a new directory if write is about to overwrite an existing file
    #             # or to write into a directory without the same fileprefix
    #             for file in listdir(directory):
    #                 if isfile(directory + file):
    #                     LOG.debug(
    #                         f"Can {type(self).__name__} `{self.dest_path()}` of prefix "
    #                         + f"{self._fileprefix} and suffix {CFG.export_filetype}"
    #                         + f" be written along with `{file}` of prefix "
    #                         + f"`{file.split('.')[0]}` and suffix {file.split('.')[-1]}"
    #                         + f"` in {self.dest_directory()}` ?"
    #                     )
    #                     # Resolve conflict at first incompatible file encountered
    #                     if directory + file == self.dest_path() or (
    #                         file.split(".")[-1] == CFG.export_filetype
    #                         and file.split(".")[0] != self._fileprefix
    #                     ):
    #                         LOG.debug(
    #                             f"No, incrementing counter of {self.dest_directory()}"
    #                         )
    #                         self._storage_title_append += 1
    #                         incompatible = True
    #                         break
    #
    #     # Write the content of this object into a file named as self.filename()
    #     with open(self.dest_path(), "w") as f:
    #         f.write(self.content())
    #     return self.dest_path()

    def frontmatter(self, append: Optional[dict[str, Any]] = None) -> str:
        meta: dict[str, Any] = {
            # Article specific
            "summary": self.chapo,
            "surtitle": self.surtitre,
            "subtitle": self.soustitre,
            "date": self.date_redac,
            "authors": [author.nom for author in self.authors()],
        }
        # Add debugging meta if needed
        if CFG.debug_meta:
            meta = meta | {"spip_id_rubrique": self.id_rubrique}
        if append is not None:
            return super().frontmatter(meta | append)
        else:
            return super().frontmatter(meta)

    # def content(self) -> str:
    #     body: str = super().content()
    #     # If there is a caption, add the caption followed by a hr
    #     if len(self._caption) > 0:
    #         body += "\n\n" + self._caption + "\n\n***"
    #     # PS
    #     if len(self._ps) > 0:
    #         body += "\n\n# POST-SCRIPTUM\n\n" + self._ps
    #     # Microblog
    #     if len(self._microblog) > 0:
    #         body += "\n\n# MICROBLOGGING\n\n" + self._microblog
    #     return body

    # Perform all the write steps of this object
    # def write_all(
    #     self,
    #     parentdepth: int,
    #     storage_parentdir: str,
    #     index: int,
    #     total: int,
    #     forced_lang: str,
    #     parenturl: str,
    # ) -> DeepDict:
    #     # self.convert(forced_lang)
    #     return {
    #         "msg": super().write_all(
    #             parentdepth, storage_parentdir, index, total, parenturl
    #         ),
    #         "documents": self.write_children(self.documents(), forced_lang),
    #     }


# Define Section as an Article that can contain other Articles or Sections
class ConvertableSection(ConvertableArticle):
    # _fileprefix: str = "_index"
    # _style = (BOLD, GREEN)  # Sections accent color is green

    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _children: tuple[
        "ConvertableSection | ConvertableArticle | ConvertableDocument", ...
    ]  # sub-sections, documents, articles
    _section: SpipRubriques
    _lang: str

    # Get articles of this section
    def articles(self, limit: int = 10**6) -> tuple[SpipArticles, ...]:
        self._log_c.debug("Initialize articles")
        return (
            SpipArticles.select()
            .where(SpipArticles.id_rubrique == self._id)
            .order_by(SpipArticles.date.desc())
            .limit(limit)
        )

    # Get subsections of this section
    def sections(self, limit: int = 10**6) -> tuple[SpipRubriques, ...]:
        self._log_c.debug("Initialize subsections")
        return (
            SpipRubriques.select()
            .where(SpipRubriques.id_parent == self._id)
            .order_by(SpipRubriques.date.desc())
            .limit(limit)
        )

    # Initialize children
    def children(self):
        self._children = tuple(
            ConvertableArticle(a, self._lang, self._cfg) for a in self.articles()
        ) + tuple(ConvertableSection(s, self._lang, self._cfg) for s in self.sections())

    def __init__(self, section: SpipRubriques, forced_lang: str, cfg: Configuration):
        self._log_c = logging.getLogger(cfg.name + ".convert.section")
        self._section = section
        self._id = section.id_rubrique
        self._lang = forced_lang
        self.children()

    # Get relational metadata in a static form for self then earch children
    def metadata(self):
        super().metadata()
        for c in self._children:
            c.metadata()

    # Convert Spip syntax to Markdown on self then each children
    def convert(self):
        super().convert()
        for c in self._children:
            c.convert()

    # Keep only one relevant language for self then each children
    def translate(self):
        super().translate()
        for c in self._children:
            c.translate()

    # Repair internal links & embeds for self then each children
    def link(self):
        super().link()
        for c in self._children:
            c.link()

    # Perform last cleaning steps
    def clean(self):
        # Add documents to children
        self._children = self._children + tuple(
            ConvertableDocument(d, self._cfg) for d in self.documents()
        )
        super().clean()
        for c in self._children:
            c.clean()

    # def frontmatter(self, add: Optional[dict[str, Any]] = None) -> str:
    #     meta: dict[str, Any] = {}
    #     # Add debugging meta if needed
    #     if CFG.debug_meta:
    #         meta = meta | {
    #             "spip_id_parent": self.id_parent,
    #             "spip_profondeur": self.profondeur,
    #         }
    #     if add is not None:
    #         meta = meta | add
    #     return super().frontmatter(meta)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._id = self.id_rubrique
    #     self._depth = self.profondeur

    # Perform all the write steps of this object
    # def write_all(
    #     self,
    #     parentdepth: int,
    #     storage_parentdir: str,
    #     index: int,
    #     total: int,
    #     forced_lang: str,
    #     parenturl: str = "",
    # ) -> DeepDict:
    #     # self.convert(forced_lang)
    #     return {
    #         "msg": super().write_all(
    #             parentdepth, storage_parentdir, index, total, parenturl
    #         ),
    #         "documents": self.write_children(self.documents(), forced_lang),
    #         "articles": self.write_children(self.articles(), forced_lang),
    #         "sections": self.write_children(self.sections(), forced_lang),
    #     }


# The "root" element representing the whole converted site
class ConvertableSite:
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _children: tuple[ConvertableSection, ...]  # Root sections
    # _children: list[SpipDocuments | SpipArticles | SpipRubriques]

    _root_id: int = 0  # Parent ID of root sections

    def children(self):
        self._log_c.debug("Initialize root sections")
        # Store each level 0 sections
        # Language specified in database can differ from markup, se we force a language
        #   (we will remove irrelevant ones further)
        for lang in self._cfg.export_languages:
            # Get all sections of parentID root_id
            sections: tuple[SpipRubriques, ...] = (
                SpipRubriques.select()
                .where(SpipRubriques.id_parent == self._root_id)
                .order_by(SpipRubriques.date.desc())
            )
            self._children = tuple(
                ConvertableSection(s, lang, self._cfg) for s in sections
            )

    def __init__(self, cfg: Configuration) -> None:
        self._log_c = logging.getLogger(cfg.name + ".convert.site")
        self._cfg = cfg
        self.children()

    # Get relational metadata in a static form for earch children
    def metadata(self):
        for c in self._children:
            c.metadata()

    # Convert Spip syntax to Markdown on each children
    def convert(self):
        for c in self._children:
            c.convert()

    # Keep only one relevant language for each children
    def translate(self):
        for c in self._children:
            c.translate()

    # Repair internal links & embeds for each children
    def link(self):
        for c in self._children:
            c.link()

    # Perform last cleaning steps
    def clean(self):
        for c in self._children:
            c.clean()
