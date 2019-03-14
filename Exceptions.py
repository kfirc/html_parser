__author__ = 'Kfir'

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