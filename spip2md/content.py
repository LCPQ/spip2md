from lark import Lark

spipParser = Lark(
    r"""
    section: /\n\r?/
           ( heading
           | list
           | table
           | quote
           | paragraph
           | SEPARATOR
           ) /\n\r?/

    heading: "{{{" paragraph "}}}"

    list: unordered_list
        | unordered_sublist
        | ordered_list
        | ordered_sublist

    unordered_list: (/\n\r?-* / paragraph)+
    unordered_sublist: (/\n\r?-*{2,7} / paragraph)+
    ordered_list: (\/n/r?-# / paragraph)+
    ordered_sublist: (\/n/r?-#{2,7} / paragraph)+

    table: row+
    row: /\n\r?\|/ cell+
    cell: paragraph "|"

    quote: "<quote>" paragraph "</quote>"

    paragraph: text+

    text: format_text
        | link
        | PURE_TEXT

    format_text: italic
               | bold
               | bold_italic

    italic: "{" PURE_TEXT "}"
    bold: "{{" PURE_TEXT "}}"
    bold_italic: "{{ {"  PURE_TEXT "} }}" | "{ {{"  PURE_TEXT "}} }"

    link: internal_link
        | external_link
        | footnote
        | glossary

    internal_link: "[" PURE_TEXT "->" PURE_TEXT "]"
    external_link: "[" PURE_TEXT "->" /[a-z]{3,6}:\/\// PURE_TEXT "]"
    footnote: "[[" PURE_TEXT "]]"
    footnote: "[?" PURE_TEXT "]"

    PURE_TEXT: /[^\n\r]+/

    SEPARATOR: /-{4,}/
""",
    start="section",
)


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        return markdown
