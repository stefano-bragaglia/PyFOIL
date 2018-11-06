from arpeggio import EOF
from arpeggio import OneOrMore
from arpeggio import Optional
from arpeggio import RegExMatch
from arpeggio import ZeroOrMore


def comment():
    return RegExMatch(r"%.*")


def program():
    return ZeroOrMore(clause), Optional(scope), ZeroOrMore(clause), EOF


def scope():
    return '#', literal, Optional(':', Optional(examples)), '.'


def examples():
    return example, ZeroOrMore(',', example)


def example():
    return Optional(label), substitution


def label():
    return ['(+)', '(-)']


def substitution():
    return '{', Optional(assignments), '}'


def assignments():
    return assignment, ZeroOrMore(',', assignment)


def assignment():
    return variable, ':', value


def value():
    return [boolean, number, string, identifier]


def clause():
    return literal, Optional(':-', Optional(literals)), '.'


def literals():
    return literal, ZeroOrMore(',', literal)


def literal():
    return Optional(negation), atom


def negation():
    return OneOrMore('~')


def atom():
    return functor, Optional('(', Optional(terms), ')')


def functor():
    return [double_quote, single_quote, identifier]


def terms():
    return term, ZeroOrMore(',', term)


def term():
    return [boolean, number, string, identifier, variable]


def boolean():
    return [false, true]


def false():
    return RegExMatch(r"FALSE", ignore_case=True)


def true():
    return RegExMatch(r"TRUE", ignore_case=True)


def number():
    return [real, integer]


def real():
    return RegExMatch(r"-?\d*\.\d+(E-?\d+)?")


def integer():
    return RegExMatch(r"-?\d+")


def string():
    return [double_quote, single_quote]


def double_quote():
    return '"', RegExMatch(r'[^"]*'), '"'


def single_quote():
    return "'", RegExMatch(r"[^']*"), "'"


def identifier():
    return RegExMatch(r'[a-z][a-zA-Z_0-9]*')


def variable():
    return RegExMatch(r'[_A-Z][a-zA-Z_0-9]*')
