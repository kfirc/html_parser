from urllib.request import urlopen
import webbrowser, re
import Regex
import Exceptions
import Element

LB = "\n"


class HTML_Parser(object):
    def __init__(self, path):
        self.html_file = HTML_File(path)
        self.parse()

    def parse(self):
        text = self.html_file.read()
        content = self._create_content(text)
        self.html_file.content = content

    def _create_content(self, text):
        pos, content = 0, []
        while pos is not None:
            text = text[pos:]
            next_element, pos = self._next_element(text)
            if next_element: content.append(next_element)
        return content

    def _next_element(self, text):
        opening_tag_match = re.match(Regex.OPENING_TAG_P, text)

        if opening_tag_match:
            # this is a start of an opening tag
            element_dict = opening_tag_match.groupdict()
            if Element.is_empty(element_dict["tag"]):
                return self._parse_empty_element_match(opening_tag_match)
            else:
                return self._parse_opening_tag_match(opening_tag_match, text)
        else:
            empty_element_match = re.match(Regex.EMPTY_ELEMENT_P, text)
            if empty_element_match: # this is a start of an empty element
                return self._parse_empty_element_match(empty_element_match)
            else:
                comment_match = re.match(Regex.COMMENT_P, text)
                if comment_match: # this is a start of a comment
                    return self._parse_comment_match(comment_match)
                else: # this is a start of a text
                    return self._parse_text(text)

    def _parse_text(self, text):
        end_pos = self._next_end_pos(text)
        return text[:end_pos].replace(LB, '').replace('\t', ''), end_pos

    def _parse_comment_match(self, comment_match):
        comment_dict = comment_match.groupdict()
        end_pos = comment_match.end()
        return Element.Comment(comment_dict["comment"]), end_pos

    def _parse_empty_element_match(self, empty_element_match):
        element_dict = empty_element_match.groupdict()

        if Element.is_empty(element_dict["tag"]):
            end_pos = empty_element_match.end()
            empty_element = Element.EmptyElement(element_dict["tag"], element_dict["attributes"])
            return empty_element, end_pos
        else:
            # invalid empty tag
            raise Exceptions.NonVoidSelfClosingTagError

    def _parse_opening_tag_match(self, opening_tag_match, text):

        tag_closed_count = 1
        end_pos = opening_tag_match.end()
        tag_dict = opening_tag_match.groupdict()
        tag, attributes = tag_dict["tag"], tag_dict["attributes"]

        opening_tag_p = Regex.OPENING_TAG_P_FORMAT.format(tag=tag)
        closing_tag_p = Regex.CLOSING_TAG_P_FORMAT.format(tag=tag)

        while tag_closed_count != 0:
            opening_tag = re.compile(opening_tag_p).search(text, end_pos)
            closing_tag = re.compile(closing_tag_p).search(text, end_pos)

            nearest_match_tag = Regex.nearest_match(opening_tag, closing_tag)
            if nearest_match_tag is None:
                raise Exceptions.NoMatchingClosingTagError(tag_dict["opening_tag"])
            elif nearest_match_tag == opening_tag:
                tag_closed_count += 1
            elif nearest_match_tag == closing_tag:
                tag_closed_count -= 1

            end_pos = nearest_match_tag.end()

        content = self._create_content(text[opening_tag_match.end(): closing_tag.start()])
        element = Element.Element(tag, content, attributes)
        return element, end_pos

    def _next_end_pos(self, text):
        end_pos = text.find("<", 1)
        if end_pos == -1: return None
        return end_pos


class HTML_File(object):
    def __init__(self, path, content=[]):
        self.path = path

        if content:
            self.content = content
            if not self.is_html_file(): raise Exceptions.ContentError
        else:
            self.content = content

    def __str__(self):
        return LB.join([str(element) for element in self.content])

    def __getitem__(self, key):
        return self.content[1][key]

    def is_html_file(self):
        if type(self.content) == list:
            return len(self.content) >= 2 and self.content[0] == "<!DOCTYPE html>" and type(self.content[1]) == Element.Element and self.content[1].tag == "html"
        elif type(self.content) == str:
            return bool(re.match(Regex.HTML_FILE_P, self.content))
        return False

    def save(self):
        with open(self.path, "w") as f:
            f.write(str(self))

    def add(self, tag=None, content=[], attributes={}, one_line=False, empty=False):
        if not self.content:
            raise Exceptions.HTMLTagError
        self.content[1].add(tag, content, attributes, one_line, empty)

    def open(self):
        webbrowser.open(self.path)

    def read(self):
        response = urlopen(self.path)
        html = response.read().decode('utf-8')
        return html


def create_file(path, content=["<!DOCTYPE html>", Element.Element("html")]):
    return HTML_File(path, content)


def main():
    pass

if __name__ == '__main__':
    main()