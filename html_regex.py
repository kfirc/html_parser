import re

EXAMPLE_HTML = """rgpieregjer<!DOCTYPE html>
<html>
	<head p=hello j=gk>
		<title> Kfir's site </title>
	</head>
	<body>
		hello world and welcome!
		please feel free as home
		<p a:5 b:4>
			this is my first paragraph
			<br />
			another line
			<!--this is a comment-->
			<br />
			another line
			<p> paragraph inside paragraph! </p>
		</p>
		<p>
			this is my second paragraph!!!
		</p>
		<hr />
	</body>
</html>"""

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
	print res

if __name__ == '__main__':
	main()
