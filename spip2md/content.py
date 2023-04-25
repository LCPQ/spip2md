from lark import Lark

spipParser = Lark(
    r"""
    section: /\n\r?/
           ( heading
           | list
           | table
           | separator
           | quote
           | paragraph
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

    separator: /-{4,}/

    quote: "<quote>" paragraph "</quote>"

    paragraph: text+

    text: format_text
        | link
        | /[^\n\r]+/

    format_text: italic
               | bold
               | bold_italic

    italic: "{" /[^\n\r]+/ "}"
    bold: "{{" /[^\n\r]+/ "}}"
    bold_italic: "{{ {" /[^\n\r]+/ "} }}" | "{ {{" /[^\n\r]+/ "}} }"

    link: internal_link
        | external_link
        | footnote
        | glossary

    internal_link: "[" /[^\n\r]+/ "->" /[^\n\r]+/ "]"
    external_link: "[" /[^\n\r]+/ "->" /[a-z]{3,6}://[^\n\r]+/ "]"
    footnote: "[[" /[^\n\r]+/ "]]"
    footnote: "[?" /[^\n\r]+/ "]"
""",
    start="section",
)


class content:
    def __init__(self, content):
        self.spip = content

    def get_markdown(self):
        markdown = self.spip
        return markdown
