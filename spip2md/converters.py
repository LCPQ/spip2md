# SPIP website to plain Markdown files converter, Copyright (C) 2023 Guilhem Fauré
# pyright: strict
from re import I, S, compile, finditer, sub
from typing import Optional

# SPIP syntax to Markdown
SPIP_TO_MARKDOWN = (
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
        r"![](\1\2)",
    ),
    (  # documents & embeds
        compile(r"<(doc|document|emb)([0-9]+)(\|.*?)*>", S | I),
        r"[](\1\2)",
    ),
    (  # internal links
        compile(r"<(art|article)([0-9]+)(\|.*?)*>", S | I),
        r"[](\1\2)",
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
    (  # WARNING Keep only the first language in multi-language blocks
        compile(
            r"<multi>\s*(?:\[.{2,4}\])?\s*(.*?)\s*(?:\s*\[.{2,4}\].*)*<\/multi>",
            S | I,
        ),
        r"\1",
    ),
    (  # WARNING remove every html tag
        compile(r"<\/?.*?>\s*", S | I),
        r"",
    ),
)

# Further cleaning for metadata texts such as titles or descriptions
SPIP_META_BLOAT = (
    compile(r"^>+ +", S | I),  # Remove beginning with angle bracket(s)
    compile(r"^\d+\. +", S | I),  # Remove beginning with a number followed by a dot
)

# Broken ISO encoding to proper UTF-8
ISO_TO_UTF = (
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
    # WARNING not sure
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

# WARNING unknown broken encoding
UNKNOWN_ISO = (
    r"â€¨",
    r"âˆ†",
)


# Apply SPIP to Markdown & ISO to UTF conversions to a text, & eventually clean meta
def convert(text: Optional[str], clean_meta: bool = False) -> str:
    if text is None:
        return ""
    for spip, markdown in SPIP_TO_MARKDOWN:
        text = spip.sub(markdown, text)
    if clean_meta:
        for bloat in SPIP_META_BLOAT:
            text = bloat.sub("", text)
    for iso, utf in ISO_TO_UTF:
        text = text.replace(iso, utf)
    return text


# Replace images & files links in Markdown with real slugs of the actually linked files
def link_document(text: str, id: int, name: str, slug: str) -> str:
    # Replace images that dont have a title written in text
    text = sub(
        r"!\[]\((?:img|image)" + str(id) + r"(\|.*?)*\)",
        f"![{name}]({slug})",
        text,
    )
    # Replace images that dont have a title written in text
    text = sub(
        r"\[]\((?:doc|document|emb)" + str(id) + r"(\|.*?)*\)",
        f"[{name}]({slug})",
        text,
    )
    # Replace images that already had a title in Markdown style link
    text = sub(
        r"!\[(.+?)\]\((?:img|image)" + str(id) + r"(\|.*?)*\)",
        f"![\\1]({slug})",
        text,
    )
    # Replace documents that already had a title in Markdown style link
    text = sub(
        r"\[(.+?)\]\((?:doc|document|emb)" + str(id) + r"(\|.*?)*\)",
        f"[\\1]({slug})",
        text,
    )
    return text


# Return a list of tuples giving the start and end of unknown substring in text
def unknown_chars(text: str) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for char in UNKNOWN_ISO:
        for match in finditer("(" + char + ")+", text):
            positions.append((match.start(), match.end()))
    return positions


# Return strings with unknown chards found in text, surrounded by context_length chars
def unknown_chars_context(text: str, context_length: int = 24) -> list[str]:
    errors: list[str] = []
    context: str = r".{0," + str(context_length) + r"}"
    for char in UNKNOWN_ISO:
        matches = finditer(
            context + r"(?=" + char + r")" + char + context,
            text,
        )
        for match in matches:
            errors.append(match.group())
    return errors
