import re
from os import path


class content:
    _mappings = {
        "horizontal-rule": (
            re.compile(r"- ?- ?- ?- ?[\- ]*|<hr ?.*?>", re.S | re.I),
            r"---",
        ),
        "line-break": (
            re.compile(r"\r?\n_ *(?=\r?\n)|<br ?.*?>", re.S | re.I),
            "\n",
        ),
        "heading": (
            re.compile(r"\{\{\{ *(.*?) *\}\}\}", re.S | re.I),
            r"## \1",
        ),
        "strong": (
            re.compile(r"\{\{ *(.*?) *\}\}", re.S | re.I),
            r"**\1**",
        ),
        "emphasis": (
            re.compile(r"\{ *(.*?) *\}", re.S | re.I),
            r"*\1*",
        ),
        "strikethrough": (
            re.compile(
                r"<del>\s*(.*?)\s*(?:(\r?\n){2,}|<\/del>)",
                re.S | re.I,
            ),
            r"~\1~",
        ),
        "anchor": (
            re.compile(r"\[ *(.*?) *-> *(.*?) *\]", re.S | re.I),
            r"[\1](\2)",
        ),
        "image": (
            re.compile(r"<(?:img|image)(.*?)(\|.*?)*>", re.S | re.I),
            r"![image](\1)",
        ),
        "document-anchors": (
            re.compile(r"<(?:doc|emb)(.*?)(\|.*?)*>", re.S | re.I),
            r"[document](\1)",
        ),
        "wikilink": (
            re.compile(r"\[\? *(.*?) *\]", re.S | re.I),
            r"[\1](https://wikipedia.org/wiki/\1)",
        ),
        "footnote": (
            re.compile(r"\[\[ *(.*?) *\]\]", re.S | re.I),
            r"",
        ),
        "unordered-list": (
            re.compile(r"(\r?\n)-(?!#|-)\*? *", re.S | re.I),
            r"\1- ",
        ),
        "wrong-unordered-list": (
            re.compile(r"(\r?\n)\* +", re.S | re.I),
            r"\1- ",
        ),
        "ordered-list": (
            re.compile(r"(\r?\n)-# *", re.S | re.I),
            r"\g<1>1. ",
        ),
        "table-metadata": (
            re.compile(r"(\r?\n)\|\|(.*?)\|(.*?)\|\|", re.S | re.I),
            r"",
        ),
        "quote": (
            re.compile(
                r"<(?:quote|poesie)>\s*(.*?)\s*(?:(\r?\n){2,}|<\/(?:quote|poesie)>)",
                re.S | re.I,
            ),
            r"> \1\2\2",
        ),
        "box": (
            re.compile(
                r"<code>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/code>)",
                re.S | re.I,
            ),
            "`\\1`",
        ),
        "fence": (
            re.compile(
                r"<cadre>\s*(.*?)\s*(?:(?:\r?\n){2,}|<\/cadre>)",
                re.S | re.I,
            ),
            "```\n\\1\n\n```",
        ),
        "multi-language": (  # Keep only the first language
            re.compile(
                r"<multi>\s*\[.{2,4}\]\s*(.*?)\s*(?:\s*\[.{2,4}\].*)*<\/multi>",
                re.S | re.I,
            ),
            r"\1",
        ),
    }

    def __init__(self, spip):
        self.markup = spip

    def get_markdown(self):
        for spip, markdown in self._mappings.values():
            self.markup = spip.sub(markdown, self.markup)
        return self.markup


# Parses a file & display its parse tree
def test(filename):
    raw = open(path.dirname(__file__) + "/" + filename).read()

    print(f"--- Conversion of {filename} ---\n\n")
    c = content(raw)
    print(c.get_markdown())


if __name__ == "__main__":
    # Test
    test("../test/0.spip")
    test("../test/1.spip")
    test("../test/2.spip")
    test("../test/3.spip")
    test("../test/4.spip")
