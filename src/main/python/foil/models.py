from typing import Iterable
from typing import List
from typing import Optional

from arpeggio import ParserPython
from arpeggio import visit_parse_tree

from foil.unification import Derivation
from foil.unification import is_ground
from foil.unification import is_variable
from foil.unification import normalize
from foil.unification import simplify
from foil.unification import Step
from foil.unification import Substitution
from foil.unification import Term
from foil.unification import unify
from foil.language.visitor import FoilVisitor


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
        value = hash((self._head, *self._body))

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
        return not self._body

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
        self._tabling = {}

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

    def get_constants(self) -> List[Term]:
        return sorted({t for c in self._clauses for l in c.literals for t in l.terms if not is_variable(t)})

    def get_facts(self) -> Iterable[Clause]:
        return [c for c in self._clauses if c.is_fact()]

    def get_rules(self) -> Iterable[Clause]:
        return (c for c in self._clauses if not c.is_fact())

    def is_ground(self) -> bool:
        return all(c.is_ground() for c in self._clauses)

    def resolve(self, query: Literal) -> Optional[Derivation]:
        if not query.is_ground():
            raise ValueError("'query' must be ground: %s" % query)

        return self._tabling.setdefault(query, self._resolve(query))

    def _resolve(self, query: Literal) -> Optional[Derivation]:
        for i, clause in enumerate(self._clauses):
            substitution = clause.head.unify(query)
            if substitution is None:
                continue

            derivation = [Step(i, query, substitution)]
            if not clause.body:
                return derivation

            for query in clause.body:
                substituted = query.substitute(substitution)
                sub_goal = self.resolve(substituted)
                if not sub_goal:
                    return None

                derivation = [*derivation, *sub_goal]

            return derivation

        return None

    def get_world(self) -> List[Literal]:
        return self._tabling.setdefault(None, self._get_world())

    def _get_world(self) -> List[Literal]:
        from foil.rete import Alpha
        from foil.rete import Beta
        from foil.rete import Leaf
        from foil.rete import Root

        table = {}
        clauses = []
        root = Root()
        for rule in self._clauses:
            if rule.is_fact():
                clauses.append(rule)
            else:
                beta = None
                for literal in rule.body:
                    name = repr(literal)
                    alpha = table.setdefault(name, Alpha(literal, root))
                    if beta is None:
                        beta = alpha
                    else:
                        name = '%s, %s' % (beta.name, alpha.name)
                        beta = table.setdefault(name, Beta(beta, alpha))
                Leaf(rule, beta, root, clauses)

        for fact in self.get_facts():
            root.notify(fact.head)

        return list({c.head for c in clauses})
