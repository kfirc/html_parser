import re

EXAMPLE_HTML = """"""

WORD = "\w*"

EMPTY_ELEMENTS_LIST = ["area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]

OPENING_TAG_P_FORMAT = "(?m)(?s)(?P<opening_tag>\<(?P<tag>{tag})(?P<attributes>( \w*\=\".*?\")*?)\>)"
CLOSING_TAG_P_FORMAT = "(?m)(?s)(?P<closing_tag>\</{tag}\>)"
EMPTY_ELEMENT_P_FORMAT = "(?P<empty_element>\<(?P<tag>{tag})(?P<attributes>( \w*\=\".*?\")*?) ?\/\>)"
COMMENT_P_FORMAT = "(?m)(?s)(?P<comment_element>\<\!\-\-(?P<comment>{comment})\-\-\>)"

OPENING_TAG_P = OPENING_TAG_P_FORMAT.format(tag=WORD)
CLOSING_TAG_P = CLOSING_TAG_P_FORMAT.format(tag=WORD)
EMPTY_ELEMENT_P = EMPTY_ELEMENT_P_FORMAT.format(tag=WORD)
COMMENT_P = COMMENT_P_FORMAT.format(comment=".*?")

HTML_FILE_P = "(?m)(?s)(\<\!DOCTYPE html\>)\s*(\<html(?: \w*\:\w*)*\>)(.*)(\<\/html\>)$"


def nearest_match(*searches):
    legit_searches = [search for search in searches if search is not None]
    if legit_searches:
        return min(legit_searches, key=lambda search: search.start())
    return None

def main():
    res = re.search(HTML_FILE_P, EXAMPLE_HTML)
    print(res)

if __name__ == '__main__':
    main()
