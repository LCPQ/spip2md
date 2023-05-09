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
