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
from spip2md.style import BLUE, BOLD, CYAN, GREEN, WARNING_STYLE, YELLOW, esc

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
                    f"Unknown char {char} found in {self._title[:40]} at: {context}"
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

    def convert_title(self) -> str:
        if self.titre is None:
            self._title = ""  # Define temporary title to use in functions
        else:
            self._title = self.titre.strip()  # Define temporary title
        return self.convert_field(self.titre)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize converted fields beginning with underscore
        self._title: str = self.convert_title()
        self._description: str = self.convert_field(self.descriptif)
        self._status = self.statut == "publie"

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
    def begin_message(
        self, index: int, limit: int, prepend: str = "", step: int = 100
    ) -> list[str]:
        output: list[str] = []
        # Output the remaining number of objects to export every step object
        if index % step == 0:
            output.append(f"Exporting {limit-index}")
            output[-1] += f" level {self._depth}"
            s: str = "s" if limit - index > 1 else ""
            output[-1] += f" {type(self).__name__}{s}"
            # Print the output as the program goes
            self.style_print(output[-1])
        # Output the counter & title of the object being exported
        output.append(f"{index + 1}. ")
        output[-1] += prepend
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
        return self._parentdir + prepend + slugify(self._title, max_length=100) + append

    # Get destination slugified name of this file
    def dest_filename(self, prepend: str = "", append: str = "") -> str:
        name, filetype = splitext(basename(str(self.fichier)))
        return slugify(prepend + name, max_length=100) + append + filetype

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize converted fields beginning with underscore
        # self._src_path = self.src_path()
        # self._dest_directory = self.dest_directory()
        # self._dest_filename = self.dest_filename()

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
    # Converted
    _text: str

    # Detect every language present in <multi> blocks of text
    # For each language in <multi> block in which we want to translate, create
    # a new self-similar object in self.translations dict
    def translate_multi(self, spipattr: str, convertattr: str) -> str:
        # Function specific logger
        log = logging.getLogger(CFG.logname + ".models.translate_multi")
        text: str = getattr(self, spipattr)  # Get text of attribute
        log.debug(f"Translating <multi> blocks of `{self._title}` `{spipattr}`")
        # Handle <multi> multi language blocks
        translations: dict[str, str] = {}  # Dict such as lang: text
        original_translation: str = text
        # for each langs of <multi> blocks, add its text to the corresponding dict key
        for block in MULTILANG_BLOCK.finditer(text):
            for lang in MULTILANGS.finditer(block.group(1)):
                # To log the translation
                trans: str = lang.group(2)[:50].strip()
                if lang.group(1) == self.lang:
                    log.debug(
                        f"Discovered {lang.group(1)} translation of `{self._title}`:"
                        + f" `{trans}`, keeping it as the original lang"
                    )
                    original_translation = original_translation.replace(
                        block.group(), lang.group(2)
                    )
                elif lang.group(1) in translations:
                    log.debug(
                        f"Discovered more {lang.group(1)} translation of"
                        + f" `{self._title}`: `{trans}`"
                    )
                    translations[lang.group(1)] += lang.group(2)
                else:
                    log.debug(
                        f"Discovered {lang.group(1)} translation of `{self._title}`: "
                        + f" `{trans}`"
                    )
                    translations[lang.group(1)] = lang.group(2)
        # Iterate over translations, adding translated attributes to translations dict
        for lang, translation in translations.items():
            if lang in CFG.export_languages:
                if lang not in self._translations:
                    self._translations[lang] = {}
                self._translations[lang][convertattr] = translation
                log.debug(
                    f"{lang} `{self._title}` `{convertattr}`"
                    + f" set to `{self._translations[lang][convertattr]}`"
                )

        log.debug(
            f"Original lang `{self.lang}` `{self._title}` `{spipattr}`"
            + f" set to `{original_translation}`"
        )
        return original_translation

    def replace_links(
        self,
        text: str,
        mapping: tuple,
        obj_type: type[NormalizedSection | NormalizedArticle | NormalizedDocument],
    ) -> str:
        LOG.debug(f"Convert {type(obj_type).__name__} links of `{self._title}`")
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
        return self._parentdir + prepend + slugify(self._title, max_length=100) + append

    # Get filename of this object
    def dest_filename(self) -> str:
        return self._fileprefix + "." + self.lang + "." + CFG.export_filetype

    def convert_title(self) -> str:
        LOG.debug(f"Convert title of currently untitled {type(self).__name__}")
        if hasattr(self, "_title"):
            LOG.debug(f"{type(self).__name__} {self._title}._title is already set")
            return self._title
        if self.titre is None:
            LOG.debug(f"{type(self).__name__}.title is None")
            return ""
        if len(self.titre) == 0:
            LOG.debug(f"{type(self).__name__}.title is empty")
            return ""
        self._title = self.titre.strip()  # Define temporary title to use in functions
        self._title = self.translate_multi("titre", "_title")
        return self.convert_field(self._title)

    def convert_text(self) -> str:
        LOG.debug(f"Convert text of `{self._title}`")
        if hasattr(self, "_text"):
            LOG.debug(f"{type(self).__name__} {self._title}._text is already set")
            return self._text
        if self.texte is None:
            LOG.debug(f"{type(self).__name__} {self._title}.text is None")
            return ""
        if len(self.texte) == 0:
            LOG.debug(f"{type(self).__name__} {self._title}.text is empty")
            return ""
        text: str = self.translate_multi("texte", "_title")
        text = self.replace_links(text, DOCUMENT_LINK, Document)
        text = self.replace_links(text, ARTICLE_LINK, Article)
        text = self.replace_links(text, SECTION_LINK, Section)
        return self.convert_field(text)

    def convert_extra(self) -> str:
        LOG.debug(f"Convert extra of `{self._title}`")
        if hasattr(self, "_extra"):
            return self._extra
        if self.extra is None:
            return ""
        if len(self.extra) == 0:
            return ""
        text: str = self.extra
        text = self.replace_links(text, ARTICLE_LINK, Article)
        text = self.replace_links(text, SECTION_LINK, Section)
        return self.convert_field(text)

    def __init__(self, *args, **kwargs):
        # Initialise translation dict as empty, in the form lang: attr: value
        self._translations: dict[str, dict[str, str]] = {}
        super().__init__(*args, **kwargs)
        # Initialize converted fields beginning with underscore
        self._choosen_language = self.langue_choisie == "oui"
        self._text = self.convert_text()
        self._extra = self.convert_extra()

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

    # Output translated self objects
    def translations(self) -> list[Self]:
        translations: list[Self] = []
        LOG.debug(f"`{self._title}` contains translations: `{self._translations}`")
        for lang, translated_attrs in self._translations.items():
            LOG.debug(f"Instanciating {lang} translation of section `{self._title}`")
            # Copy itself (with every attribute) as a base for the translated object
            translation: Self = deepcopy(self)
            # Replace the lang & the translations attributes of the translated object
            translation.lang = lang
            translation._translations = {}
            # Replace the translated attributes of the translated object
            for attr, value in translated_attrs.values():
                setattr(translation, attr, value)
        return translations

    # Get the children of this object
    def children(self) -> tuple[tuple[WritableObject], ...]:
        return (self.documents(),)

    # Write all the children of this object
    def write_children(self) -> RecursiveList:
        LOG.debug(f"Writing children of {type(self).__name__} `{self._title}`")
        output: RecursiveList = []
        for children in self.children():
            total = len(children)
            for i, obj in enumerate(children):
                output.append(
                    obj.write_all(self._depth, self.dest_directory(), i, total)
                )
        return output

    # Perform all the write steps of this object
    def write_all(
        self, parentdepth: int, parentdir: str, index: int, total: int
    ) -> RecursiveList:
        output: RecursiveList = super().write_all(parentdepth, parentdir, index, total)
        output.append(self.write_children())
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
    def articles(self) -> tuple[Article]:
        LOG.debug(f"Initialize articles of `{self._title}`")
        return (
            Article.select()
            .where((Article.id_rubrique == self._id) & (Article.lang == self.lang))
            .order_by(Article.date.desc())
            # .limit(limit)
        )

    # Get subsections of this section
    def sections(self) -> tuple[Self]:
        LOG.debug(f"Initialize subsections of `{self._title}`")
        return (
            Section.select()
            .where(Section.id_parent == self._id)
            .order_by(Section.date.desc())
        )

    def children(self) -> tuple[tuple[WritableObject], ...]:
        return (self.articles(),) + super().children() + (self.sections(),)
