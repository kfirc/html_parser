import Parser

DIR_PATH = "C:\\Users\\Kfir\\Desktop\\script\\html\\"
FILE_NAME = "pyplay"
FILE_FORMAT = "html"
FULL_PATH = "{dir}{file}.{format}".format(dir=DIR_PATH, file=FILE_NAME, format=FILE_FORMAT)


def parse_file(path=FULL_PATH):
    parser = Parser.HTMLParser(path)
    return parser

def create_file_test(path=FULL_PATH):
    html_file = Parser.create_file(path)
    html_file.add("head")
    html_file.add("body", "hello world and welcome!\nplease feel free as home")
    html_file["head"].add("title", "Kfir's site", one_line=True)
    html_file["body"].add("p", "this is my first paragraph")
    html_file["body"]["p"].add("br")
    html_file["body"]["p"].add_text("another line")
    html_file["body"]["p"].add_comment("this is a comment")
    html_file["body"]["p"].add("br")
    html_file["body"]["p"].add_text("another line")
    html_file["body"].add("hr")

    html_file.save()
    html_file.open()
    print(html_file)

def main():
    create_file_test()
    parser = parse_file(r"https://www.google.com/")
    print(parser.html_file)


if __name__ == "__main__":
    main()
