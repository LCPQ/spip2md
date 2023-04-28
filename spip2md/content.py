from os import path

from lark import Lark

# spipParser = Lark(open(path.dirname(__file__) + "/spip.lark"))
spipParser = Lark(open(path.dirname(__file__) + "/spip.flex.lark"))


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        return markdown


# Parses a file & display its parse tree
def test(filename):
    print(f"--- Parsing of {filename} ---\n")
    parsed = spipParser.parse(open(path.dirname(__file__) + "/" + filename).read())
    print(parsed, "\n")
    print("--- Pretty print : ---\n\n", parsed.pretty(), "\n")


# Test
test("../test/1.spip")
test("../test/2.spip")
test("../test/3.spip")
test("../test/4.spip")
