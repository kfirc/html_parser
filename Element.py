import re
import Exceptions
import Regex

__author__ = 'Kfir'
LB = "\n"
OPENING_TAG_FORMAT = "<{tag}{attributes}>"
CLOSING_TAG_FORMAT = "</{tag}>"
EMPTY_ELEMENT_FORMAT = "<{tag}{attributes} />"
COMMENT_FORMAT = "<!--{comment}-->"
TAG_FORMAT = "{opening_tag}{content}{lb}{closing_tag}"
ONE_LINE_TAG_FORMAT = "{opening_tag} {content}{closing_tag}"
ATTRIBUTE_FORMAT = '{attribute}="{value}"'
EMPTY_ELEMENTS_LIST = ["area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]

class Element(object):
    def __init__(self, tag=None, content=[], attributes={}, one_line=False):
        if isinstance(tag, Element):
            element = tag
            tag, content, attributes, one_line = element.tag, element.content, element.attributes, element.one_line
        self.tag = tag
        self.attributes = Attributes(attributes)
        self.one_line = one_line

        if type(content) == str:
            content = [content]
        elif type(content) != list:
            raise Exceptions.ContentError
        self.content = content


    @property
    def _opening_tag(self):
        return OPENING_TAG_FORMAT.format(tag=self.tag, attributes=self.attributes)

    @property
    def _closing_tag(self):
        return CLOSING_TAG_FORMAT.format(tag=self.tag)

    def __str__(self):
        content = ""
        if self.one_line:
            if self.content:
                content = " ".join([str(tag) for tag in self.content]) + " "
            return ONE_LINE_TAG_FORMAT.format(opening_tag=self._opening_tag, content=content, closing_tag=self._closing_tag)
        elif self.content:
            tab_lines = lambda element: "\t" + (LB + "\t").join(str(element).split(LB))
            content = LB + LB.join([tab_lines(element) for element in self.content])
        return TAG_FORMAT.format(opening_tag=self._opening_tag, content=content, lb=LB, closing_tag=self._closing_tag)


    def __getitem__(self, key):
        """
        retrieve all the elements from the parent element that from the 'key' type.
        for example - if the key was 'p' the function retrieve all the 'p' elements from the parent (self) element.
        """
        element_filter = lambda element: type(element) in [Element, EmptyElement] and element.tag == key
        element_list = filter(element_filter, self.content)

        if len(element_list) == 0: return
        if len(element_list) == 1: return element_list[0]
        return element_list


    def _add(self, to_add):
        self.content = list(self.content + [to_add])


    def add(self, tag=None, content=[], attributes={}, one_line=False, empty=False):
        if type(tag) in [Element, EmptyElement]:
            element = tag
        else:
            element = create_element(tag, content, attributes, one_line, empty)

        self._add(element)


    def add_text(self, text):
        self._add(text)


    def add_comment(self, comment):
        self._add(Comment(comment))


class EmptyElement(object):
    def __init__(self, tag, attributes):
        self.tag = tag
        self.attributes = Attributes(attributes)

    def __str__(self):
        return EMPTY_ELEMENT_FORMAT.format(tag=self.tag, attributes=self.attributes)


class Comment(object):
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return COMMENT_FORMAT.format(comment=self.comment)


class Attributes(object):
    def __init__(self, attributes={}):
        if type(attributes) == dict:
            self.attribute_dict = attributes

        elif isinstance(attributes, Attributes):
            self.attribute_dict = attributes.attribute_dict

        elif type(attributes) == str:
            if not attributes:
                self.attribute_dict = {}
            else:
                if attributes.startswith(" "):
                    attributes = attributes[1:] #remove the leading space

                self.attribute_dict = {}
                attribute_search = re.search("(?P<attribute>\w*)\=\"(?P<value>.*?)\"", attributes)

                while attributes and attribute_search:

                    group_dict = attribute_search.groupdict()
                    self.attribute_dict[group_dict["attribute"]] = group_dict["value"]
                    attributes = attributes[attribute_search.end():]

                    attribute_search = re.search("(?P<attribute>\w*)\=\"(?P<value>.*?)\"", attributes)


                """
                attributes = attributes.split(" ") # split the attributes by the " "
                attributes = [item.split("=") for item in attributes] # split each attribute item to its attribute, value
                self.attribute_dict = {attribute:value for attribute, value in attributes}
                """

    def __str__(self):
        if self.attribute_dict:
            return " " + " ".join([ATTRIBUTE_FORMAT.format(attribute=attribute, value=value) for (attribute, value) in self.attribute_dict.items()])
        return ""


def create_element(tag=None, content=[], attributes={}, one_line=False, empty=False):
    if empty or is_empty(tag):
        if content:
            raise Exceptions.ContentError
        return EmptyElement(tag, attributes)
    else:
        return Element(tag, content, attributes, one_line)


def is_empty(tag):
    return any([type(tag) == EmptyElement, tag in EMPTY_ELEMENTS_LIST])


def main():
    pass


if __name__ == "__main__":
    main()