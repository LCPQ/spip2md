import re

mappings = (
    (  # horizontal-rule
        re.compile(r"- ?- ?- ?- ?[\- ]*|<hr ?.*?>", re.S | re.I),
        # r"---",
        r"***",
    ),
    (  # line-break
        re.compile(r"\r?\n_ *(?=\r?\n)|<br ?.*?>", re.S | re.I),
        "\n",
    ),
    (  # heading
        re.compile(r"\{\{\{ *(.*?) *\}\}\}", re.S | re.I),
        r"## \1",
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
    (  # document-anchors
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


def convert(markup):
    for spip, markdown in mappings:
        markup = spip.sub(markdown, markup)
    return markup.encode("utf-8").decode("utf-8")
