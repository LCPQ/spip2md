import re


def italic(text):
    # convert SPIP italic to markdown italic
    # return re.sub(r"([^\{]*)([^\{\}]*)([^\{]*)", r"\1\*\2\*\3", text)
    pass


def bold(text):
    # convert SPIP bold to markdown bold
    pass


def headings(text):
    # convert SPIP headings to markdown headings
    pass


def code_blocks(text):
    # convert SPIP code blocks to markdown code blocks
    pass


def links(text):
    # convert SPIP links to markdown links
    pass


def paragraphs(text):
    # convert SPIP paragraphs to markdown paragraphs
    pass


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        markdown = paragraphs(markdown)
        markdown = italic(markdown)
        markdown = bold(markdown)
        markdown = headings(markdown)
        markdown = links(markdown)
        markdown = code_blocks(markdown)
        return markdown
