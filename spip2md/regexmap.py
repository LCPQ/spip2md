# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# pyright: strict
from re import I, S, compile

# ((SPIP syntax, Replacement Markdown syntax), …)
SPIP_MARKDOWN = (
    (  # horizontal rule
        compile(r"- ?- ?- ?- ?[\- ]*|<hr ?.*?>", S | I),
        # r"---",
        r"***",
    ),
    (  # line break
        compile(r"\r?\n_ *(?=\r?\n)|<br ?.*?>", S | I),
        "\n",
    ),
    (  # heading
        compile(r"\{\{\{ *(.*?) *\}\}\}", S | I),
        r"## \1",  # Translate SPIP headings to h2
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
    (  # images
        compile(r"<(img|image)([0-9]+)(\|.*?)*>", S | I),
        r"![](\2)",  # Needs to be further processed to replace ID with filename
    ),
    (  # documents & embeds
        compile(r"<(doc|document|emb)([0-9]+)(\|.*?)*>", S | I),
        r"[](\2)",  # Needs to be further processed to replace ID with filename
    ),
    (  # internal links
        compile(r"<(art|article)([0-9]+)(\|.*?)*>", S | I),
        r"[](\2)",  # Needs to be further processed to replace ID with filename
    ),
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
        r"",
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

# Match against documents ID found in links, ID can be inserted with .format()
# Name and path can be further replaced with .format()
DOCUMENT_LINK = r"(!)?\[(.*?)\]\(({})\)"
DOCUMENT_LINK_REPL = r"\1[\2{}]({})"

# Multi language block, to be further processed per lang
MULTILANG_BLOCK = compile(r"<multi>(.+?)<\/multi>", S | I)
MULTILANGS = compile(r"\[([a-zA-Z\-]{2,6})\]\s*(.+?)(?=\[[a-zA-Z\-]{2,6}\]|$)", S | I)

# WARNING probably useless text in metadata fields, to be removed
BLOAT = (
    compile(r"^>+ +", S | I),  # Remove beginning with angle bracket(s)
    compile(r"^\d+\. +", S | I),  # Remove beginning with a number followed by a dot
)

# Matches against every HTML tag
HTMLTAG = compile(r"<\/?.*?>\s*", S | I)


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
)

# Warning elements in terminal output to highlight
WARNING_OUTPUT = (
    compile(r"(ERROR)"),  # ERROR
    compile(r"(MISSING NAME)"),  # MISSING NAME
    compile(r"(NOT FOUND)"),  # NOT FOUND
)