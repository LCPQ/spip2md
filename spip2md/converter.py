from re import I, S, compile, finditer

# SPIP syntax to Markdown
spipToMarkdown = (
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
        r"# \1",
        # r"## \1",
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

spipToText = (
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

isoToUtf = (
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
unknownIso = (
    r"â€¨",  # unknown â€¨ + surroundings
    r"âˆ†",  # unknown â^† + surroundings
)


def convertBody(spipBody):
    text: str = spipBody
    for spip, markdown in spipToMarkdown:
        text = spip.sub(markdown, text)
    for iso, utf in isoToUtf:
        text.replace(iso, utf)
    return text


def convertMeta(spipMeta):
    text: str = spipMeta
    for spip, metadata in spipToText:
        text = spip.sub(metadata, text)
    for iso, utf in isoToUtf:
        text.replace(iso, utf)
    return text

def highlightUnknownChars(text):
    # Define terminal escape sequences to stylize output, regex escaped
    COLOR = "\033[91m" + "\033[1m"  # Red + Bold
    RESET = "\033[0m"
    # Highlight in COLOR unknown chars in text
    for char in unknownIso:
        for match in finditer(char, text):
            text = (
                text[: match.start()]
                + COLOR
                + match.group()
                + RESET
                + text[match.end() :]
            )
    return text
