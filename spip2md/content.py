from os import path

from lark import Lark

spipParser = Lark(open(path.dirname(__file__) + "/spip.lark"))


# Test
print("\n--- First test")
text = open(path.dirname(__file__) + "/../test/1.spip").read()
print(spipParser.parse(text).pretty())
print("\n--- Second test")
text = open(path.dirname(__file__) + "/../test/2.spip").read()
print(spipParser.parse(text).pretty())


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        return markdown
