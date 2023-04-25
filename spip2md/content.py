from lark import Lark

spipParser = Lark(
    r"""
    section: /\n\r?/
           ( paragraph
           | heading
           | list
           | table
           | quote
           | SEPARATOR
           ) /\n\r?/

    paragraph: format_text

    heading: "{{{" format_text "}}}"

    list: unordered_list
        | unordered_sublist
        | ordered_list
        | ordered_sublist

    unordered_list: (/\n\r?-* / format_text)+
    unordered_sublist: (/\n\r?-*{2,7} / format_text)+
    ordered_list: (\/n/r?-# / format_text)+
    ordered_sublist: (\/n/r?-#{2,7} / format_text)+

    table: row+
    row: /\n\r?\|/ cell+
    cell: format_text "|"

    quote: "<quote>" format_text "</quote>"

    format_text: (
                 | link
                 | PURE_TEXT
                 )+

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

    PURE_TEXT: /[^\s\{\-\|\<\[\}\>\]][^\n\r\{\<\[\}\]]*/

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
