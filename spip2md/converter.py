from re import I, S, compile

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
        compile("â€™"),
        r"’",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        compile("â€˜"),
        r"‘",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        compile("eÌ\u0081"),
        r"é",
    ),
    (  # Fix UTF-8 è that was interpreted as ISO 8859-1
        compile("eÌ€"),
        r"è",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        compile("eÌ‚"),
        r"ê",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        compile("oÌ‚"),
        r"ô",
    ),
    (  # Fix UTF-8 î that was interpreted as ISO 8859-1
        compile("iÌ‚"),
        r"î",
    ),
    (  # Fix UTF-8 ï that was interpreted as ISO 8859-1
        compile("iÌˆ"),
        r"ï",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        compile("oÌˆ"),
        r"ö",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        compile("uÌˆ"),
        r"ü",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        compile("aÌ€"),
        r"à",
    ),
    (  # Fix UTF-8 … that was interpreted as ISO 8859-1
        compile("â€¦"),
        r"…",
    ),
    (  # Fix UTF-8 “ that was interpreted as ISO 8859-1
        compile("â€œ"),
        r"“",
    ),
    (  # Fix UTF-8 ” that was interpreted as ISO 8859-1
        compile("â€\u009d"),
        r"”",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        compile("â€“"),
        r"–",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        compile("â€”"),
        r"—",
    ),
    (  # Fix UTF-8 − that was interpreted as ISO 8859-1
        compile("â€\u0090"),
        r"−",
    ),
    (  # Fix UTF-8 • that was interpreted as ISO 8859-1
        compile("â€¢"),
        r"•",
    ),
    (  # Fix UTF-8 ç that was interpreted as ISO 8859-1
        compile("Ã§"),
        r"ç",
    ),
    (  # Fix UTF-8 í that was interpreted as ISO 8859-1
        compile("iÌ\u0081"),
        r"í",
    ),
    # WARNING not sure
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        compile("eÌ "),
        r"é",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        compile("â€ "),
        r"† ",
    ),
)

## WARNING unknown broken encoding
unknownIso = (compile(r"\w*â€¨.*\r?\n"),)  # unknown â€¨ + surroundings


def convertBody(spipBody):
    text = spipBody
    for spip, markdown in spipToMarkdown:
        text = spip.sub(markdown, text)
    for iso, utf in isoToUtf:
        text = iso.sub(utf, text)
    for iso in unknownIso:
        for match in iso.finditer(text):
            print(f"    UNKNOWN CHARACTER {match.group()}")
    return text


def convertMeta(spipMeta):
    text = spipMeta
    for spip, metadata in spipToText:
        text = spip.sub(metadata, text)
    for iso, utf in isoToUtf:
        text = iso.sub(utf, text)
    for iso in unknownIso:
        for match in iso.finditer(text):
            print(f"    UNKNOWN CHARACTER {match.group()}")
    return text
