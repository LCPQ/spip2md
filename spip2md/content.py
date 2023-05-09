import re
from os import path

# from lark import Lark
# from pyparsing import Word, alphas

# larkParser = Lark(open(path.dirname(__file__) + "/spip.lark"))


class content:
    _mappings = (
        (re.compile(r"\{\{\{(.*?)\}\}\}", re.S | re.I), r"## \1"),
        (re.compile(r"\{\{ \{(.*?)\} \}\}", re.S | re.I), r"***\1***"),
        (re.compile(r"\{ \{\{(.*?)\}\} \}", re.S | re.I), r"***\1***"),
        (re.compile(r"\{\{(.*?)\}\}", re.S | re.I), r"**\1**"),
        (re.compile(r"\{(.*?)\}", re.S | re.I), r"*\1*"),
    )

    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        for spip, md in self._mappings:
            markdown = spip.sub(md, markdown)
        return markdown
        # Parses the body & display parse tree
        try:
            print(f"    parse tree :\n")
            print(larkParser.parse(self.spip).pretty())
        except Exception as e:
            print("    PARSING FAILED :\n", e)
        return markdown


# Parses a file & display its parse tree
def test(filename):
    raw = open(path.dirname(__file__) + "/" + filename).read()

    print(f"--- Conversion of {filename} ---\n\n")
    c = content(raw)
    print(c.get_markdown())
    # print(f"--- Parse tree of {filename} ---\n\n")
    # print(larkParser.parse(raw))


if __name__ == "__main__":
    # Test
    test("../test/0.spip")
    # test("../test/1.spip")
    # test("../test/2.spip")
    # test("../test/3.spip")
    # test("../test/4.spip")
