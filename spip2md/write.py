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


This file adds write to disk capabilities to spip objects
"""
from spip2md.convert import ConvertableSite


class WritableSite(ConvertableSite):
    def write(self):
        pass


# # Write the root sections and their subtrees
# def write_root(parent_dir: str, parent_id: int = 0) -> DeepDict:
#     # Print starting message
#     print(
#         f"""\
# Begin exporting {esc(BOLD)}{CFG.db}@{CFG.db_host}{esc()} SPIP database to plain \
# Markdown+YAML files,
# into the directory {esc(BOLD)}{parent_dir}{esc()}, \
# as database user {esc(BOLD)}{CFG.db_user}{esc()}
# """
#     )
#     buffer: list[DeepDict] = []  # Define temporary storage for output
#     # Write each sections (write their entire subtree) for each export language
#     # Language specified in database can differ from markup, se we force a language
#     #   and remove irrelevant ones at each looping
#     for lang in CFG.export_languages:
#         ROOTLOG.debug("Initialize root sections")
#         # Get all sections of parentID ROOTID
#         child_sections: tuple[Section, ...] = (
#             Section.select()
#             .where(Section.id_parent == parent_id)
#             .order_by(Section.date.desc())
#         )
#         nb: int = len(child_sections)
#         for i, s in enumerate(child_sections):
#             ROOTLOG.debug(f"Begin exporting {lang} root section {i}/{nb}")
#             try:
#                 buffer.append(s.write_all(-1, CFG.output_dir, i, nb, lang))
#             except LangNotFoundError as err:
#                 ROOTLOG.debug(err)  # Log the message
#             except DontExportDraftError as err:  # If not CFG.export_drafts
#                 ROOTLOG.debug(err)  # Log the message
#             except IgnoredPatternError as err:
#                 ROOTLOG.debug(err)  # Log the message
#             print()  # Break line between level 0 sections in output
#             ROOTLOG.debug(
#                 f"Finished exporting {lang} root section {i}/{nb} {s._url_title}"
#             )
#     return {"sections": buffer}
