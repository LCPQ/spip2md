# pyright: strict
from re import I, S, compile, finditer
from typing import Optional

# SPIP syntax to Markdown
spip_to_markdown = (
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
        compile(r"\{\{ *(.*?) *\}\}", S | I),
        r"**\1**",
    ),
    (  # html strong
        compile(r"<strong> *(.*?) *</strong>", S | I),
        r"**\1**",
    ),
    (  # emphasis
        compile(r"\{ *(.*?) *\}", S | I),
        r"*\1*",
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
    (  # anchor
        compile(r"\[ *(.*?) *-> *(.*?) *\]", S | I),
        r"[\1](\2)",
    ),
    (  # image
        compile(r"<(?:img|image)(.*?)(\|.*?)*>", S | I),
        r"![image](\1)",
    ),
    (  # document anchor
        compile(r"<(?:doc|emb)(.*?)(\|.*?)*>", S | I),
        r"[document](\1)",
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
        r"",
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
    (  # Keep only the first language in multi-language blocks
        compile(
            r"<multi>\s*(?:\[.{2,4}\])?\s*(.*?)\s*(?:\s*\[.{2,4}\].*)*<\/multi>",
            S | I,
        ),
        r"\1",
    ),
    (  # WARNING remove every html tag
        compile(r"<\/?.*?> *", S | I),
        r"",
    ),
)

spip_to_text = (
    (  # strong
        compile(r"\{\{ *(.*?) *\}\}", S | I),
        r"\1",
    ),
    (  # html strong
        compile(r"<strong> *(.*?) *</strong>", S | I),
        r"\1",
    ),
    (  # emphasis
        compile(r"\{ *(.*?) *\}", S | I),
        r"\1",
    ),
    (  # html emphasis
        compile(r"<i> *(.*?) *<\/i>", S | I),
        r"\1",
    ),
    (  # strikethrough
        compile(
            r"<del>\s*(.*?)\s*(?:(\r?\n){2,}|<\/del>)",
            S | I,
        ),
        r"\1",
    ),
    (  # Keep only the first language in multi-language blocks
        compile(
            r"<multi>\s*(?:\[.{2,4}\])?\s*(.*?)\s*(?:\s*\[.{2,4}\].*)*<\/multi>",
            S | I,
        ),
        r"\1",
    ),
    (  # remove every html tag
        compile(r"<\/?.*?> *", S | I),
        r"",
    ),
    (  # beginning with angle bracket(s)
        compile(r"^>+ +", S | I),
        r"",
    ),
    (  # beginning with a number followed by a dot
        compile(r"^\d+\. +", S | I),
        r"",
    ),
)

iso_to_utf = (
    # Broken encoding
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
)

## WARNING unknown broken encoding
unknown_iso = (
    r"â€¨",  # unknown â€¨
    r"âˆ†",  # unknown â^†
)


# Apply spip_to_markdown conversions to a text
def convert_body(text: Optional[str]) -> str:
    if text is None:
        return ""
    for spip, markdown in spip_to_markdown:
        text = spip.sub(markdown, text)
    for iso, utf in iso_to_utf:
        text = text.replace(iso, utf)
    return text


# Apply spip_to_text conversions to a text
def convert_meta(text: Optional[str]) -> str:
    if text is None:
        return ""
    for spip, metadata in spip_to_text:
        text = spip.sub(metadata, text)
    for iso, utf in iso_to_utf:
        text = text.replace(iso, utf)
    return text


# Replace unknown chars with empty strings (delete them)
def remove_unknown_chars(text: str) -> str:
    for char in unknown_iso:
        text.replace(char, "")
    return text


# Return a list of tuples giving the start and end of unknown substring in text
def unknown_chars(text: str) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for char in unknown_iso:
        for match in finditer("(" + char + ")+", text):
            positions.append((match.start(), match.end()))
    return positions


# Return strings with unknown chards found in text, surrounded by context_length chars
def get_unknown_chars(text: str, context_length: int = 20) -> list[str]:
    errors: list[str] = []
    context: str = r".{0," + str(context_length) + r"}"
    for char in unknown_iso:
        matches = finditer(
            context + r"(?=" + char + r")" + char + r".*?(?=\r?\n|$)",
            text,
        )
        for match in matches:
            errors.append(match.group())
    return errors
