from os import path

from lark import Lark

spipParser = Lark(open(path.dirname(__file__) + "/spip.lark"))


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        # Parses the body & display parse tree
        try:
            parsed = spipParser.parse(self.spip)
            print(f"    parse tree :\n", parsed.pretty(), "\n")
        except Exception as e:
            print("    PARSING FAILED :\n", e)
        return markdown

# Parses a file & display its parse tree
def test(filename):
    print(f"--- Parsing of {filename} ---\n")
    parsed = spipParser.parse(open(path.dirname(__file__) + "/" + filename).read())
    print(parsed, "\n")
    print(f"--- Parse tree of {filename} ---\n\n", parsed.pretty(), "\n")

if __name__ == "__main__":
    # Test
    test("../test/0.spip")
    test("../test/1.spip")
    test("../test/2.spip")
    test("../test/3.spip")
    test("../test/4.spip")
