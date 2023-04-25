from os import path

from lark import Lark

spipParser = Lark(open(path.dirname(__file__) + "/spip.lark"), start="section")


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        return markdown
