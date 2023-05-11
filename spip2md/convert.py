import re

# SPIP syntax to Markdown
spipToMarkdown = (
    (  # horizontal rule
        re.compile(r"- ?- ?- ?- ?[\- ]*|<hr ?.*?>", re.S | re.I),
        # r"---",
        r"***",
    ),
    (  # line break
        re.compile(r"\r?\n_ *(?=\r?\n)|<br ?.*?>", re.S | re.I),
        "\n",
    ),
    (  # heading
        re.compile(r"\{\{\{ *(.*?) *\}\}\}", re.S | re.I),
        r"# \1",
        # r"## \1",
    ),
    (  # strong
        re.compile(r"\{\{ *(.*?) *\}\}", re.S | re.I),
        r"**\1**",
    ),
    (  # emphasis
        re.compile(r"\{ *(.*?) *\}", re.S | re.I),
        r"*\1*",
    ),
    (  # strikethrough
        re.compile(
            r"<del>\s*(.*?)\s*(?:(\r?\n){2,}|<\/del>)",
            re.S | re.I,
        ),
        r"~\1~",
    ),
    (  # anchor
        re.compile(r"\[ *(.*?) *-> *(.*?) *\]", re.S | re.I),
        r"[\1](\2)",
    ),
    (  # image
        re.compile(r"<(?:img|image)(.*?)(\|.*?)*>", re.S | re.I),
        r"![image](\1)",
    ),
    (  # document anchor
        re.compile(r"<(?:doc|emb)(.*?)(\|.*?)*>", re.S | re.I),
        r"[document](\1)",
    ),
    (  # wikilink
        re.compile(r"\[\? *(.*?) *\]", re.S | re.I),
        r"[\1](https://wikipedia.org/wiki/\1)",
    ),
    (  # footnote
        re.compile(r"\[\[ *(.*?) *\]\]", re.S | re.I),
        r"",
    ),
    (  # unordered list
        re.compile(r"(\r?\n)-(?!#|-)\*? *", re.S | re.I),
        r"\1- ",
    ),
    (  # wrong unordered list
        re.compile(r"(\r?\n)\* +", re.S | re.I),
        r"\1- ",
    ),
    (  # wrong unordered list WARNING suppresses preceding tag
        re.compile(r"(\r?\n)<.*?>\* +", re.I),
        r"\1- ",
    ),
    (  # ordered-list
        re.compile(r"(\r?\n)-# *", re.S | re.I),
        r"\g<1>1. ",
    ),
    (  # table-metadata
        re.compile(r"(\r?\n)\|\|(.*?)\|(.*?)\|\|", re.S | re.I),
        r"",
    ),
    (  # quote
        re.compile(
            r"<(?:quote|poesie)>\s*(.*?)\s*(?:(\r?\n){2,}|<\/(?:quote|poesie)>)",
            re.S | re.I,
        ),
        r"> \1\2\2",
    ),
    (  # box
        re.compile(
            r"<code>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/code>)",
            re.S | re.I,
        ),
        "`\\1`",
    ),
    (  # fence
        re.compile(
            r"<cadre>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/cadre>)",
            re.S | re.I,
        ),
        "```\n\\1\n\n```",
    ),
    (  # Keep only the first language in multi-language blocks
        re.compile(
            r"<multi>\s*\[.{2,4}\]\s*(.*?)\s*(?:\s*\[.{2,4}\].*)*<\/multi>",
            re.S | re.I,
        ),
        r"\1",
    ),
)

isoToUtf = (
    # Broken encoding
    (  # Fix UTF-8 appostrophe that was interpreted as ISO 8859-1
        re.compile("â€™"),
        r"’",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        re.compile("â€˜"),
        r"‘",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        re.compile("eÌ\u0081"),
        r"é",
    ),
    (  # Fix UTF-8 è that was interpreted as ISO 8859-1
        re.compile("eÌ€"),
        r"è",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        re.compile("eÌ‚"),
        r"ê",
    ),
    (  # Fix UTF-8 ê that was interpreted as ISO 8859-1
        re.compile("oÌ‚"),
        r"ô",
    ),
    (  # Fix UTF-8 î that was interpreted as ISO 8859-1
        re.compile("iÌ‚"),
        r"î",
    ),
    (  # Fix UTF-8 ï that was interpreted as ISO 8859-1
        re.compile("iÌˆ"),
        r"ï",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        re.compile("oÌˆ"),
        r"ö",
    ),
    (  # Fix UTF-8 ö that was interpreted as ISO 8859-1
        re.compile("uÌˆ"),
        r"ü",
    ),
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        re.compile("aÌ€"),
        r"à",
    ),
    (  # Fix UTF-8 … that was interpreted as ISO 8859-1
        re.compile("â€¦"),
        r"…",
    ),
    (  # Fix UTF-8 “ that was interpreted as ISO 8859-1
        re.compile("â€œ"),
        r"“",
    ),
    (  # Fix UTF-8 ” that was interpreted as ISO 8859-1
        re.compile("â€\u009d"),
        r"”",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        re.compile("â€“"),
        r"–",
    ),
    (  # Fix UTF-8 – that was interpreted as ISO 8859-1
        re.compile("â€”"),
        r"—",
    ),
    (  # Fix UTF-8 − that was interpreted as ISO 8859-1
        re.compile("â€\u0090"),
        r"−",
    ),
    (  # Fix UTF-8 • that was interpreted as ISO 8859-1
        re.compile("â€¢"),
        r"•",
    ),
    (  # Fix UTF-8 í that was interpreted as ISO 8859-1
        re.compile("iÌ\u0081"),
        r"í",
    ),
    # WARNING not sure
    (  # Fix UTF-8 é that was interpreted as ISO 8859-1
        re.compile("eÌ "),
        r"é",
    ),
    (  # Fix UTF-8 † that was interpreted as ISO 8859-1
        re.compile("â€ "),
        r"† ",
    ),
)

## WARNING unknown broken encoding
unknownIso = (re.compile(r"\w*â€¨.*\r?\n"),)  # unknown â€¨ + surroundings


def convert(markup):
    for spip, markdown in spipToMarkdown:
        markup = spip.sub(markdown, markup)
    for iso, utf in isoToUtf:
        markup = iso.sub(utf, markup)
    for iso in unknownIso:
        for match in iso.finditer(markup):
            print(f"    UNKNOWN CHARACTER {match.group()}")
    return markup
