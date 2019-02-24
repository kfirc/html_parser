import webbrowser, re, urllib2
from html_regex import *

LB = "\n"
OPENING_TAG_FORMAT = "<{tag}{attributes}>"
CLOSING_TAG_FORMAT = "</{tag}>"
EMPTY_ELEMENT_FORMAT = "<{tag}{attributes} />"
COMMENT_FORMAT = "<!--{comment}-->"
TAG_FORMAT = "{opening_tag}{content}{lb}{closing_tag}"
ONE_LINE_TAG_FORMAT = "{opening_tag} {content}{closing_tag}"
ATTRIBUTE_FORMAT = '{attribute}="{value}"'
EMPTY_ELEMENTS_LIST = ["area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]


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
		opening_tag_match = re.match(OPENING_TAG_P, text)
		
		if opening_tag_match:
			# this is a start of an opening tag
			element_dict = opening_tag_match.groupdict()
			if is_empty(element_dict["tag"]):
				return self._parse_empty_element_match(opening_tag_match)
			else:
				return self._parse_opening_tag_match(opening_tag_match, text)
		else:
			empty_element_match = re.match(EMPTY_ELEMENT_P, text)
			if empty_element_match: # this is a start of an empty element
				return self._parse_empty_element_match(empty_element_match)
			else:
				comment_match = re.match(COMMENT_P, text)
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
		return Comment(comment_dict["comment"]), end_pos

	def _parse_empty_element_match(self, empty_element_match):
		element_dict = empty_element_match.groupdict()

		if is_empty(element_dict["tag"]):
			end_pos = empty_element_match.end()
			empty_element = EmptyElement(element_dict["tag"], element_dict["attributes"])
			return empty_element, end_pos
		else:
			# invalid empty tag
			raise NonVoidSelfClosingTagError

	def _parse_opening_tag_match(self, opening_tag_match, text):

		tag_closed_count = 1
		end_pos = opening_tag_match.end()
		tag_dict = opening_tag_match.groupdict()
		tag, attributes = tag_dict["tag"], tag_dict["attributes"]

		opening_tag_p = OPENING_TAG_P_FORMAT.format(tag=tag)
		closing_tag_p = CLOSING_TAG_P_FORMAT.format(tag=tag)

		while tag_closed_count != 0:
			opening_tag = re.compile(opening_tag_p).search(text, end_pos)
			closing_tag = re.compile(closing_tag_p).search(text, end_pos)

			nearest_match_tag = nearest_match(opening_tag, closing_tag)
			if nearest_match_tag is None:
				raise NoMatchingClosingTagError(tag_dict["opening_tag"])
			elif nearest_match_tag == opening_tag:
				tag_closed_count += 1
			elif nearest_match_tag == closing_tag:
				tag_closed_count -= 1
			
			end_pos = nearest_match_tag.end()

		content = self._create_content(text[opening_tag_match.end(): closing_tag.start()])
		element = Element(tag, content, attributes)
		return element, end_pos

	def _next_end_pos(self, text):
		end_pos = text.find("<", 1)
		if end_pos == -1: return None
		return end_pos


class Element(object):
	def __init__(self, tag=None, content=[], attributes={}, one_line=False):
		if type(tag) == type(self):
			self = Element(tag.tag, tag.content, tag.attributes, tag.one_line)
		else:
			self.tag = tag
			self.attributes = Attributes(attributes)
			self.one_line = one_line

			if type(content) == list:
				self.content = content
			elif type(content) == str:
				self.content = [content]
			else:
				raise ContentError

	@property
	def _opening_tag(self):
		return OPENING_TAG_FORMAT.format(tag=self.tag, attributes=self.attributes)

	@property
	def _closing_tag(self):
		return CLOSING_TAG_FORMAT.format(tag=self.tag)

	def _tab_lines(self, text):
		return "\t" + (LB + "\t").join(text.split(LB))

	def _one_line_str(self):

		if self.content:
			content = " ".join([str(tag) for tag in self.content]) + " "
		else:
			content = ""
 		
		return_str = ONE_LINE_TAG_FORMAT.format(opening_tag=self._opening_tag, content=content, closing_tag=self._closing_tag)
		return return_str 
	

	def __str__(self):
		if self.one_line:
			return self._one_line_str()
		if self.content:
			content = LB + LB.join([self._tab_lines(str(element)) for element in self.content])
		else:
			content = ""		
		return_str = TAG_FORMAT.format(opening_tag=self._opening_tag, content=content, lb=LB, closing_tag=self._closing_tag)
		return return_str


	def __getitem__(self, key):
		"""
		retrieve all the elements from the parent element that from the 'key' type.
		for example - if the key was 'p' the function retrieve all the 'p' elements from the parent (self) element.
		"""
		element_filter = lambda element: type(element) in [Element, EmptyElement] and element.tag == key
		element_list = filter(element_filter, self.content)

		if len(element_list) == 0:
			return
		if len(element_list) == 1:
			return element_list[0]
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

		elif type(attributes) == type(self):
			self.attribute_dict = attributes.attribute_dict

		elif type(attributes) == str:
			if not attributes:
				self.attribute_dict = {}
			else:
				if attributes[0] == " ":
					attributes = attributes[1:] #remove the leading space

				self.attribute_dict = {}
				attribute_search = re.search("(?P<attribute>\w*)\=\"(?P<value>.*?)\"", attributes)

				while attributes and attribute_search:

					groupdict = attribute_search.groupdict()
					self.attribute_dict[groupdict["attribute"]] = groupdict["value"]
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


class HTML_File(object):
	def __init__(self, path, content=[]):
		self.path = path
		
		if content:
			self.content = content
			if not self.is_html_file(): raise ContentError
		else:
			self.content = content

	def __str__(self):
		return LB.join([str(element) for element in self.content])

	def __getitem__(self, key):
		return self.content[1][key]

	def is_html_file(self):
		if type(self.content) == list:
			return len(self.content) >= 2 and self.content[0] == "<!DOCTYPE html>" and type(self.content[1]) == Element and self.content[1].tag == "html"
		elif type(self.content) == str:
			return bool(re.match(HTML_FILE_P, self.content))
		return False

	def save(self):
		with open(self.path, "w") as f:
			f.write(str(self))

	def add(self, tag=None, content=[], attributes={}, one_line=False, empty=False):
		if not self.content:
			raise HTMLTagError
		self.content[1].add(tag, content, attributes, one_line, empty)

	def open(self):
		webbrowser.open(self.path)

	def read(self):
		response = urllib2.urlopen(self.path)
		html = response.read()
		return html


class ContentError(Exception):
	pass

class HTMLTagError(Exception):
	pass

class NoMatchingOpeningTagError(Exception):
	pass

class NoMatchingClosingTagError(Exception):
	pass

class NonVoidSelfClosingTagError(Exception):
	pass

def is_empty(tag):
	return any([type(tag) == EmptyElement, tag in EMPTY_ELEMENTS_LIST])

def create_file(path, content=["<!DOCTYPE html>", Element("html")]):
	return HTML_File(path, content)

def create_element(tag=None, content=[], attributes={}, one_line=False, empty=False):
	if empty or is_empty(tag):
		if content:
			raise ContentError
		return EmptyElement(tag, attributes)
	else:
		return Element(tag, content, attributes, one_line)

def main():
	pass

if __name__ == '__main__':
	main()