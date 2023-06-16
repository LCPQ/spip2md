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
"""
# pyright: strict
from re import I, S, compile

from spip2md.config import CFG

# ((SPIP syntax, Replacement Markdown syntax), …)
SPIP_MARKDOWN = (
    (  # horizontal rule
        compile(r"\r?\n?\r?\n?- ?- ?- ?- ?[\- ]*\r?\n?\r?\n?|<hr ?.*?>", I),
        # r"---",
        "\n\n***\n\n",
    ),
    (  # line break
        compile(r"\r?\n_ *(?=\r?\n)|<br ?.*?>", I),
        "\n",  # WARNING May not be the real translation
    ),
    (  # heading
        compile(r"\r?\n?\r?\n?\{\{\{ *(.*?) *\}\}\}\r?\n?\r?\n?", S | I),
        "\n\n## \\1\n\n",  # Translate headings to h2
    ),
    (  # strong
        compile(r"\{\{ *(.*?) *\}\} ?", S | I),
        r"**\1** ",
    ),
    (  # html strong
        compile(r"<strong> *(.*?) *</strong>", S | I),
        r"**\1**",
    ),
    (  # emphasis
        compile(r"\{ *(.*?) *\} ?", S | I),
        r"*\1* ",
    ),
    (  # html emphasis
        compile(r"<i> *(.*?) *<\/i>", S | I),
        r"*\1*",
    ),
    (  # strikethrough
        compile(
            r"<del>\s*(.*?)\s*(?:(\r?\n){2,}|<\/del>)",
            S | I,
        ),
        r"~\1~",
    ),
    # (  # images # processed by a specific function
    #     compile(r"<(img|image)([0-9]+)(\|.*?)*>", S | I),
    #     r"![](\2)",
    # ),
    # (  # documents & embeds # processed by a specific function
    #     compile(r"<(doc|document|emb)([0-9]+)(\|.*?)*>", S | I),
    #     r"[](\2)",
    # ),
    # (  # internal links # processed by a specific function
    #     compile(r"<(art|article)([0-9]+)(\|.*?)*>", S | I),
    #     r"[](\2)",
    # ),
    (  # anchor
        compile(r"\[ *(.*?) *-> *(.*?) *\]", S | I),
        r"[\1](\2)",
    ),
    (  # wikilink
        compile(r"\[\? *(.*?) *\]", S | I),
        r"[\1](https://wikipedia.org/wiki/\1)",
    ),
    (  # footnote
        compile(r"\[\[ *(.*?) *\]\]", S | I),
        r"",  # WARNING remove it
    ),
    (  # unordered list
        compile(r"(\r?\n)-(?!#|-)\*? *", S | I),
        r"\1- ",
    ),
    (  # wrong unordered list
        compile(r"(\r?\n)\* +", S | I),
        r"\1- ",
    ),
    (  # wrong unordered list WARNING suppresses preceding tag
        compile(r"(\r?\n)<.*?>\* +", I),
        r"\1- ",
    ),
    (  # ordered-list
        compile(r"(\r?\n)-# *", S | I),
        r"\g<1>1. ",
    ),
    (  # table-metadata
        compile(r"(\r?\n)\|\|(.*?)\|(.*?)\|\|", S | I),
        r"",  # Remove it
    ),
    (  # quote
        compile(
            r"<(?:quote|poesie)>\s*(.*?)\s*(?:(\r?\n){2,}|<\/(?:quote|poesie)>)",
            S | I,
        ),
        r"> \1\2\2",
    ),
    (  # box
        compile(
            r"<code>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/code>)",
            S | I,
        ),
        "`\\1`",
    ),
    (  # fence
        compile(
            r"<cadre>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/cadre>)",
            S | I,
        ),
        "```\n\\1\n\n```",
    ),
)

DOCUMENT_LINK = (
    # SPIP style embeds
    compile(r"<()(?:doc|document|emb|embed)([0-9]+)(?:\|(.*?))?>", S | I),
    # SPIP style documents & embeds links
    compile(r"\[ *([^\]]*?) *-> *(?:doc|document|emb|embed)([0-9]+) *\]", S | I),
    # Markdown style documents & embeds links
    compile(r"\[(.*?)\]\((?:doc|document|emb|embed)([0-9]+)(?:\|(.*?))?\)", S | I),
    # SPIP style image links
    compile(r"\[ *([^\]]*?) *-> *(?:img|image)([0-9]+) *\]", S | I),
)

IMAGE_LINK = (
    # SPIP style images embeds
    compile(r"<()(?:img|image)([0-9]+)(?:\|(.*?))?>", S | I),
    # Markdown style images links
    compile(r"!?\[(.*?)\]\((?:img|image)([0-9]+)(?:\|(.*?))?\)", S | I),
)

ARTICLE_LINK = (
    # SPIP style article embeds
    compile(r"<()(?:art|article)([0-9]+)(?:\|(.*?))?>", S | I),
    # SPIP style article links
    compile(r"\[ *([^\]]*?) *-> *(?:art|article)([0-9]+) *\]", S | I),
    # Markdown style internal links
    compile(r"\[(.*?)\]\((?:art|article)([0-9]+)(?:\|(.*?))?\)", S | I),
)

SECTION_LINK = (
    # SPIP style sections embeds
    compile(r"<()(?:rub|rubrique)([0-9]+)(?:\|(.*?))?>", S | I),
    # SPIP style sections links
    compile(r"\[ *([^\]]*?) *-> *(?:rub|rubrique)([0-9]+) *\]", S | I),
    # Markdown style internal links
    compile(r"\[(.*?)\]\((?:rub|rubrique)([0-9]+)(?:\|(.*?))?\)", S | I),
)

# LINK_REPL = r"[{}]({})"  # Name and path can be further replaced with .format()
# IMAGE_REPL = r"![{}]({})"  # Name and path can be further replaced with .format()


# Multi language block, to be further processed per lang
MULTILANG_BLOCK = compile(r"<multi>(.+?)<\/multi>", S | I)
CONFIG_LANGS = {  # lang of configuration: (match against this lang)
    lang: compile(r"\[ *" + lang + r" *\]\s*(.+?)\s*(?=\[[a-zA-Z\-]{2,6}\]|$)", S | I)
    for lang in CFG.export_languages
}
# MULTILANGS = compile(  # Matches agains all langs of multi blocks
#     r"\[([a-zA-Z\-]{2,6})\]\s*(.+?)\s*(?=\[[a-zA-Z\-]{2,6}\]|$)", S | I
# )

# WARNING probably useless text in metadata fields, to be removed
BLOAT = (
    compile(r"^>+ +"),  # Remove beginning with angle bracket(s)
    compile(r"^\d+\. +"),  # Remove beginning with a number followed by a dot
)

# Matches against every HTML tag
HTMLTAGS = (compile(r"<\/?.*?>\s*", S),)


# ((Broken ISO 8859-1 encoding, Proper UTF equivalent encoding), …)
ISO_UTF = (
    (  # Fix UTF-8 appostrophe that was interpreted as ISO 8859-1
        "â€™",
        r"’",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        "â€˜",
        r"‘",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        "eÌ\u0081",
        r"é",
    ),
    (  # Fix UTF-8 è that was interpreted as ISO 8859-1
        "eÌ€",
        r"è",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        "eÌ‚",
        r"ê",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        "oÌ‚",
        r"ô",
    ),
    (  # Fix UTF-8 î that was interpreted as ISO 8859-1
        "iÌ‚",
        r"î",
    ),
    (  # Fix UTF-8 ï that was interpreted as ISO 8859-1
        "iÌˆ",
        r"ï",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        "oÌˆ",
        r"ö",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        "uÌˆ",
        r"ü",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        "aÌ€",
        r"à",
    ),
    (  # Fix UTF-8 … that was interpreted as ISO 8859-1
        "â€¦",
        r"…",
    ),
    (  # Fix UTF-8 “ that was interpreted as ISO 8859-1
        "â€œ",
        r"“",
    ),
    (  # Fix UTF-8 ” that was interpreted as ISO 8859-1
        "â€\u009d",
        r"”",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        "â€“",
        r"–",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        "â€”",
        r"—",
    ),
    (  # Fix UTF-8 − that was interpreted as ISO 8859-1
        "â€\u0090",
        r"−",
    ),
    (  # Fix UTF-8 • that was interpreted as ISO 8859-1
        "â€¢",
        r"•",
    ),
    (  # Fix UTF-8 ç that was interpreted as ISO 8859-1
        "Ã§",
        r"ç",
    ),
    (  # Fix UTF-8 î that was interpreted as ISO 8859-1
        "Ã®",
        r"î",
    ),
    (  # Fix UTF-8 « that was interpreted as ISO 8859-1
        "Â«",
        r"«",
    ),
    (  # Fix UTF-8 » that was interpreted as ISO 8859-1
        "Â»",
        r"»",
    ),
    (  # Fix UTF-8 ° that was interpreted as ISO 8859-1
        "Â°",
        r"°",
    ),
    (  # Fix UTF-8 û that was interpreted as ISO 8859-1
        "Ã»",
        r"û",
    ),
    (  # Fix UTF-8 nbsp that was interpreted as ISO 8859-1
        "Â ",
        r" ",
    ),
    (  # Fix UTF-8 í that was interpreted as ISO 8859-1
        "iÌ\u0081",
        r"í",
    ),
    # WARNING not sure below
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        "eÌ ",
        r"é",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        "â€ ",
        r"† ",
    ),
    (  # Remove Windows style line feed
        "\r",
        r"",
    ),
)

# WARNING broken ISO 8859-1 encoding which I don’t know the UTF equivalent
UNKNOWN_ISO = (
    "â€¨",
    "âˆ†",
)


# Special elements in terminal output to surround
SPECIAL_OUTPUT = (
    compile(r"^([0-9]+?\.)(?= )"),  # Counter
    compile(r"(?<= )(->)(?= )"),  # Arrow
    compile(r"(?<=^Exporting )([0-9]+?)(?= )"),  # Total
) + tuple(
    compile(r"(?<=level [0-9] )(" + language + r" )")
    for language in CFG.export_languages
)

# Warning elements in terminal output to highlight
WARNING_OUTPUT = (
    compile(r"(EMPTY NAME)"),  # EMPTY
    compile(r"(?<= )(ERROR: [A-Z ]+:)(?= )"),  # ERRORS (CAPS)
)
