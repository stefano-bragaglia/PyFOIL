from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from arpeggio import ParserPython
from arpeggio import visit_parse_tree

from foil.language.visitor import FoilVisitor
from foil.unification import Derivation
from foil.unification import is_ground
from foil.unification import is_variable
from foil.unification import normalize
from foil.unification import simplify
from foil.unification import Substitution
from foil.unification import Term
from foil.unification import unify
from foil.unification import Value
from foil.unification import Variable


class Mask:

    def __init__(self, negated: bool, functor: str, arity: int):
        self._negated = negated
        self._functor = functor
        self._arity = arity

    def __hash__(self) -> int:
        return hash((self._negated, self._functor, self._arity))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Mask):
            return False

        if self._negated is not other._negated:
            return False

        if self._arity is not other._arity:
            return False

        return self._functor == other._functor

    def __repr__(self) -> str:
        if self._negated:
            return '~%s/%d' % (self._functor, self._arity)

        return '%s/%d' % (self._functor, self._arity)

    @property
    def negated(self) -> bool:
        return self._negated

    @property
    def functor(self) -> str:
        return self._functor

    @property
    def arity(self) -> int:
        return self._arity


class Atom:

    @staticmethod
    def parse(content: str) -> 'Atom':
        from foil.language.grammar import atom
        from foil.language.grammar import comment

        parser = ParserPython(atom, comment_def=comment)
        parse_tree = parser.parse(content)
        return visit_parse_tree(parse_tree, FoilVisitor())

    def __init__(self, functor: str, terms: List[Term] = None):
        self._functor = functor
        self._terms = terms or []

    def __hash__(self) -> int:
        return hash((self._functor, *self._terms))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Atom):
            return False

        if normalize(self._functor) != normalize(other._functor):
            return False

        if len(self._terms) != len(other._terms):
            return False

        for i, term in enumerate(self._terms):
            if normalize(term) != normalize(other._terms[i]):
                return False

        return True

    def __repr__(self) -> str:
        if not self._terms:
            return normalize(self._functor)

        return '%s(%s)' % (normalize(self._functor), ','.join(normalize(term) for term in self._terms))

    @property
    def functor(self) -> str:
        return self._functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._terms

    def get_arity(self) -> int:
        return len(self._terms)

    def is_ground(self) -> bool:
        return all(is_ground(t) for t in self._terms)

    def unify(self, other: 'Atom') -> Optional[Substitution]:
        if not isinstance(other, Atom):
            return None

        if normalize(self._functor) != normalize(other._functor):
            return None

        if len(self._terms) != len(other._terms):
            return None

        subst = {}
        for var, term in zip(self._terms, other._terms):
            subst = unify(var, term, subst)
            if subst is None:
                return None

        return simplify(subst)

    def substitute(self, subst: Substitution) -> 'Atom':
        terms = [subst.get(term, term) if is_variable(term) else term for term in self._terms]

        return Atom(self._functor, terms)


class Literal:

    @staticmethod
    def parse(content: str) -> 'Literal':
        from foil.language.grammar import literal
        from foil.language.grammar import comment

        parser = ParserPython(literal, comment_def=comment)
        parse_tree = parser.parse(content)
        return visit_parse_tree(parse_tree, FoilVisitor())

    def __init__(self, atom: Atom, negated: bool = False):
        self._negated = negated
        self._atom = atom

    def __hash__(self) -> int:
        return hash((self._negated, self._atom))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Literal):
            return False

        if self._negated != other._negated:
            return False

        return self._atom == other._atom

    def __repr__(self) -> str:
        if self._negated:
            return '~%s' % repr(self._atom)

        return repr(self._atom)

    @property
    def negated(self) -> bool:
        return self._negated

    @property
    def functor(self) -> str:
        return self._atom.functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._atom.terms

    def get_arity(self) -> int:
        return self._atom.get_arity()

    def get_complement(self) -> 'Literal':
        return Literal(self._atom, not self._negated)

    def get_mask(self) -> Mask:
        return Mask(self._negated, self.functor, self.get_arity())

    def is_ground(self) -> bool:
        return self._atom.is_ground()

    def unify(self, other: 'Literal') -> Optional[Substitution]:
        if not isinstance(other, Literal):
            return None

        if self.negated != other.negated:
            return None

        return self._atom.unify(other._atom)

    def substitute(self, substitution: Substitution) -> 'Literal':
        return Literal(self._atom.substitute(substitution), self._negated)


class Clause:

    @staticmethod
    def parse(content: str) -> 'Clause':
        from foil.language.grammar import clause
        from foil.language.grammar import comment

        parser = ParserPython(clause, comment_def=comment)
        parse_tree = parser.parse(content)
        return visit_parse_tree(parse_tree, FoilVisitor())

    def __init__(self, head: Literal, body: List[Literal] = None):
        self._head = head
        self._body = body or []

    def __hash__(self) -> int:
        return hash((self._head, *self._body))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Clause):
            return False

        if self._head != other._head:
            return False

        if len(self._body) != len(other._body):
            return False

        for i, literal in enumerate(self._body):
            if literal != other._body[i]:
                return False

        return True

    def __repr__(self) -> str:
        if self._body:
            return '%s :- %s.' % (repr(self._head), ', '.join(repr(l) for l in self._body))

        return '%s.' % repr(self._head)

    @property
    def head(self) -> Literal:
        return self._head

    @property
    def body(self) -> Iterable[Literal]:
        return self._body

    @property
    def literals(self) -> Iterable[Literal]:
        return [self._head, *self._body]

    def get_arity(self) -> int:
        return len(self._body)

    def is_fact(self) -> bool:
        return not self._body and self._head.is_ground()

    def is_ground(self) -> bool:
        return all(l.is_ground() for l in self.literals)

    def substitute(self, substitution: Substitution) -> 'Clause':
        return Clause(self._head.substitute(substitution), [l.substitute(substitution) for l in self._body])


class Program:

    @staticmethod
    def parse(content: str) -> 'Program':
        from foil.language.grammar import program
        from foil.language.grammar import comment

        parser = ParserPython(program, comment_def=comment)
        parse_tree = parser.parse(content)
        return visit_parse_tree(parse_tree, FoilVisitor())

    def __init__(self, clauses: List[Clause] = None):
        self._clauses = clauses or []

    def __hash__(self) -> int:
        return hash(tuple(self._clauses))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Program):
            return False

        if len(self._clauses) != len(other._clauses):
            return False

        return all(c in other._clauses for c in self._clauses)

    def __repr__(self) -> str:
        return '\n'.join(repr(c) for c in self._clauses)

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._clauses

    def get_clause(self, index: int) -> Optional[Clause]:
        return self._clauses[index] if 0 <= index < len(self._clauses) else None

    def get_facts(self) -> Iterable[Clause]:
        return [c for c in self._clauses if c.is_fact()]

    def get_rules(self) -> Iterable[Clause]:
        return (c for c in self._clauses if not c.is_fact())

    def is_empty(self) -> bool:
        return not self._clauses

    def is_ground(self) -> bool:
        return all(c.is_ground() for c in self._clauses)

    def resolve(self, query: Literal) -> Optional[Derivation]:
        if not query.is_ground():
            raise ValueError("'query' must be ground: %s" % query)

        from foil.unification import resolve

        return resolve(self, query)

    def ground(self) -> List[Literal]:
        from foil.rete import ground

        return ground(self)


class Label(Enum):
    NEGATIVE = '-'
    POSITIVE = '+'


Assignment = Dict[Variable, Value]


class Example:

    # TODO Add parse

    def __init__(self, assignment: Assignment, label: Label = Label.POSITIVE):
        # TODO Check that assignment is correct?
        self._assignment = assignment
        self._label = label

    def __hash__(self) -> int:
        return hash((*self._assignment.items(), self._label))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._label != other._label:
            return False

        return self._assignment == other._assignment

    def __repr__(self) -> str:
        return '<%s>(%s)' % (
            ','.join('%s=%s' % (normalize(v), normalize(t)) for v, t in sorted(self._assignment.items())),
            self._label.value
        )

    @property
    def label(self) -> Label:
        return self._label

    @property
    def assignment(self) -> Assignment:
        return self._assignment

    @property
    def variables(self) -> Iterable[Variable]:
        return self._assignment.keys()

    def get_value(self, variable: Variable) -> Optional[Value]:
        return self._assignment.get(variable)


class Problem:

    # TODO Add parse

    def __init__(self, program: Program, target: Literal, examples: List[Example] = None):
        self._program = program
        self._target = target
        self._examples = sorted(examples, key=lambda x: repr(x))

    def __hash__(self) -> int:
        return hash((self._target, self._program))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Problem):
            return False

        if self._target != other._target:
            return False

        return self._program == other._program

    def __repr__(self) -> str:
        dataset = ', '.join(repr(e) for e in self._examples)
        descriptor = '#%s%s.' % (repr(self._target), ':\n  %s' % dataset)
        if self._program.is_empty():
            return descriptor

        return '%s\n\n%s' % (descriptor, '\n'.join(repr(c) for c in self._program.clauses))

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._program.clauses

    @property
    def target(self) -> Literal:
        return self._target

    @property
    def examples(self) -> Iterable[Example]:
        return self._examples

    @property
    def program(self) -> Program:
        return self._program

    def get_clause(self, index: int) -> Optional[Clause]:
        return self._program.get_clause(index)

    def get_facts(self) -> Iterable[Clause]:
        return self._program.get_facts()

    def get_rules(self) -> Iterable[Clause]:
        return self._program.get_rules()

    def is_empty(self) -> bool:
        return self._program.is_empty()

    def is_ground(self) -> bool:
        return self._program.is_ground()

    def resolve(self, query: Literal) -> Optional[Derivation]:
        return self._program.resolve(query)

    def ground(self) -> List[Literal]:
        return self._program.ground()

    def learn(self) -> List[Clause]:
        from foil.learning import learn_hypotheses

        return learn_hypotheses(self._target, list(self.program.clauses), list(self._examples))
