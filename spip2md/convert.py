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
from os.path import basename, splitext
from typing_extensions import Self

from slugify import slugify

from spip2md.config import Configuration
from spip2md.spip_models import (
    SpipArticles,
    SpipAuteurs,
    SpipAuteursLiens,
    SpipDocuments,
    SpipDocumentsLiens,
    SpipMots,
    SpipMotsLiens,
    SpipRubriques,
)


class ConvertableDocument:
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _spip_obj: SpipDocuments  # The Spip Article this is representing
    # Converted fields
    _src: str  # URL
    _slug: str = ""  # URL
    _id: int

    class Meta:
        table_name: str = "spip_document"  # Define the name of the Spip DB table

    def __init__(self, spip_obj: SpipDocuments, cfg: Configuration):
        self._log_c = logging.getLogger(cfg.name + ".convert.document")
        self._cfg = cfg
        self._spip_obj = spip_obj
        self._id = int(spip_obj.id_document)  # type: ignore
        # Define source name of this file
        self._src = cfg.data_dir + spip_obj.fichier
        # Define destination name of this file
        name, filetype = splitext(basename(str(spip_obj.fichier)))
        prepend: str = str(spip_obj.id_document) + "-" if self._cfg.prepend_id else ""
        self._slug = slugify(prepend + name, max_length=cfg.title_max_length) + filetype


class ConvertableRedactional:
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _spip_obj: SpipArticles | SpipRubriques  # The Spip Article this is representing
    _depth: int  # Depth
    _children: dict[tuple[str, int], ConvertableDocument] = {}  # Children
    _id: int
    _lang: str
    _authors: tuple[SpipAuteurs, ...]
    _tags: tuple[SpipMots, ...]

    # Initialize documents related to self
    def documents(
        self, limit: int = 10**3
    ) -> dict[tuple[str, int], ConvertableDocument]:
        self._log_c.debug(
            "Initialize documents.\n"
            + f"Section: {self._spip_obj.titre}, Depth : {self._depth}"
        )
        documents = [
            ConvertableDocument(doc, self._cfg)
            for doc in (
                SpipDocuments.select()
                .join(
                    SpipDocumentsLiens,
                    on=(SpipDocuments.id_document == SpipDocumentsLiens.id_document),
                )
                .where(SpipDocumentsLiens.id_objet == self._id)
                .limit(limit)
            )
        ]
        # Store them mutably
        return {("document", d._id): d for d in documents}

    # Initialize self authors
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

    # Initialize self tags
    def tags(self) -> tuple[SpipMots]:
        self._log_c.debug("Initialize tags")
        return (
            SpipMots.select()
            .join(
                SpipMotsLiens,
                on=(SpipMots.id_mot == SpipMotsLiens.id_mot),
            )
            .where(SpipMotsLiens.id_objet == self._id)
        )


class ConvertableArticle(ConvertableRedactional):
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

    class Meta:
        table_name: str = "spip_articles"  # Define the name of the Spip DB table

    def __init__(self, spip_obj: SpipArticles, cfg: Configuration, depth: int):
        self._log_c = logging.getLogger(cfg.name + ".convert.article")
        self._cfg = cfg
        self._spip_obj = spip_obj
        self._id = int(spip_obj.id_article)  # type: ignore # Peewee types not defined
        self._lang = str(spip_obj.lang)
        self._depth = depth
        self._draft = spip_obj.statut != "publie"
        self._children |= self.documents()  # Retreive documents & add them to the index

    # Return children and itself in order to be indexed by the parent
    def index(
        self,
    ) -> dict[tuple[str, int], tuple[str, int]]:
        return {child_key: ("article", self._id) for child_key in self._children}


# Define Section as an Article that can contain other Articles or Sections
class ConvertableSection(ConvertableRedactional):
    _fileprefix: str = "_index"  # Prefix of written Markdown files
    # sub-sections, documents, articles
    _children: dict[
        tuple[str, int], "ConvertableSection | ConvertableArticle | ConvertableDocument"
    ] = {}
    # Routing table to objects
    _index: dict[tuple[str, int], tuple[str, int]] = {}

    class Meta:
        table_name: str = "spip_rubriques"  # Define the name of the Spip DB table

    # Get articles of this section
    def articles(self, limit: int = 10**6):
        self._log_c.debug(
            "Initialize articles.\n"
            + f"Section: {self._spip_obj.titre}, Depth : {self._depth}"
        )
        articles = [
            ConvertableArticle(art, self._cfg, self._depth)
            for art in (
                SpipArticles.select()
                .where(SpipArticles.id_rubrique == self._id)
                .order_by(SpipArticles.date.desc())
                .limit(limit)
            )
        ]
        # Add these articles and their children to self index
        for article in articles:
            self._index |= article.index()
        # Store them mutably
        return {("article", art._id): art for art in articles}

    # Get subsections of this section
    def sections(self, limit: int = 10**6):
        self._log_c.debug(
            "Initialize subsections of\n"
            + f"section {self._spip_obj.titre} of depth {self._depth}"
        )
        sections = [
            ConvertableSection(sec, self._cfg, self._depth)
            for sec in (
                SpipRubriques.select()
                .where(SpipRubriques.id_parent == self._id)
                .order_by(SpipRubriques.date.desc())
                .limit(limit)
            )
        ]
        # Add these sections’s indexes to self index, replacing next hop with section
        for section in sections:
            self._index |= {
                obj_key: ("section", section._id) for obj_key in section._index
            }
        # Store them mutably
        return {("section", sec._id): sec for sec in sections}

    def __init__(self, spip_obj: SpipRubriques, cfg: Configuration, parent_depth: int):
        self._log_c = logging.getLogger(cfg.name + ".convert.section")
        self._cfg = cfg
        self._spip_obj = spip_obj
        self._id = int(spip_obj.id_rubrique)  # type: ignore
        self._lang = str(spip_obj.lang)
        self._depth = parent_depth + 1
        self._children |= self.documents()
        self._children |= self.articles()
        self._children |= self.sections()


# The "root" element representing the whole converted site
class ConvertableSite:
    _log_c: logging.Logger  # Logger for conversion operations
    _cfg: Configuration  # Global configuration
    _children: dict[tuple[str, int], ConvertableSection] = {}  # Root sections
    _index: dict[tuple[str, int], tuple[str, int]] = {}  # Routing table to objects

    _id: int = 0  # Parent ID of root sections
    _depth: int = 0  # Depth

    def sections(self) -> dict[tuple[str, int], ConvertableSection]:
        self._log_c.debug("Initialize ROOT sections")
        # Get all sections of parentID root_id
        sections = [
            ConvertableSection(sec, self._cfg, self._depth)
            for sec in (
                SpipRubriques.select()
                .where(SpipRubriques.id_parent == self._id)
                .order_by(SpipRubriques.date.desc())
            )
        ]

        # Add these sections’s indexes to self index, replacing next hop with section
        # do this while outputting it as the children
        def sec_to_index(section: ConvertableSection):
            for obj_key in section._index:
                self._index[obj_key] = ("section", section._id)
            return ("section", section._id)

        return {sec_to_index(subsection): subsection for subsection in sections}

    def __init__(self, cfg: Configuration) -> None:
        self._log_c = logging.getLogger(cfg.name + ".convert.site")
        self._cfg = cfg
        self._children |= self.sections()
