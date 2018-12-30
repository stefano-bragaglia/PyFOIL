from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from foil.models import Clause
from foil.models import Literal
from foil.unification import Substitution

Payload = Tuple[List[Literal], Substitution]


class Root:

    def __init__(self):
        self.children = set()

    def notify(self, fact: Literal):
        for child in self.children:
            child.notify(fact, {}, self)


class Alpha:

    def __init__(self, pattern: 'Literal', parent: Root):
        self.parent = parent
        self.pattern = pattern
        self.name = repr(pattern)
        self.memory = []
        self.children = set()
        parent.children.add(self)

    def notify(self, fact: Literal, subst: Substitution, parent: Root):
        subst = self.pattern.unify(fact)
        if subst is not None:
            payload = ([fact], subst)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify([fact], subst, self)


Node = Union[Alpha, 'Beta']


class Beta:

    def __init__(self, parent_1: Node, parent_2: Alpha):
        self.parent_1 = parent_1
        self.parent_2 = parent_2
        self.name = '%s, %s' % (parent_1.name, parent_2.name)
        self.memory = []
        self.children = set()
        parent_1.children.add(self)
        parent_2.children.add(self)

    def notify(self, fact: List[Literal], subst: Substitution, parent: Node):
        if parent is self.parent_1:
            for ground_2, subs_2 in self.parent_2.memory:
                self._notify(fact, subst, ground_2, subs_2)
        elif parent is self.parent_2:
            for ground_1, subs_1 in self.parent_1.memory:
                self._notify(ground_1, subs_1, fact, subst)

    @staticmethod
    def _unify(subst_1: Substitution, subst_2: Substitution) -> Optional[Substitution]:
        for var in set(subst_1).intersection(subst_2):
            if subst_1[var] != subst_2[var]:
                return None

        return {**subst_1, **subst_2}

    def _notify(self, fact_1: List[Literal], subst_1: Substitution, fact_2: List['Literal'], subst_2: Substitution):
        subs = self._unify(subst_1, subst_2)
        if subs is not None:
            ground = [*fact_1, *fact_2]
            payload = (ground, subs)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify(ground, subs, self)


class Leaf:

    def __init__(self, clause: Clause, parent: Node, root: Root, agenda: List[Clause]):
        self.parent = parent
        self.clause = clause
        self.name = repr(clause)
        self.memory = []

        self.root = root
        self.agenda = agenda
        parent.children.add(self)

    def notify(self, fact: List[Literal], subst: Substitution, parent: Node):
        payload = (fact, subst)
        if payload not in self.memory:
            self.memory.append(payload)

            literal = self.clause.head.substitute(subst)
            clause = Clause(literal, fact)
            if clause not in self.agenda:
                self.agenda.append(clause)

            self.root.notify(literal)


class Engine:
    _nodes = {}
    _agenda = []
    _root = Root()

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._agenda

    @property
    def facts(self) -> Iterable[Literal]:
        return list({c.head for c in self._agenda})

    def load(self, clause: Clause):
        if clause.is_fact():
            if clause not in self._agenda:
                self._agenda.append(clause)
        else:
            beta = None
            for literal in clause.body:
                name = repr(literal)
                alpha = self._nodes.setdefault(name, Alpha(literal, self._root))
                if beta is None:
                    beta = alpha
                else:
                    name = '%s, %s' % (beta.name, alpha.name)
                    beta = self._nodes.setdefault(name, Beta(beta, alpha))
            Leaf(clause, beta, self._root, self._agenda)

    def insert(self, fact: Clause):
        if not fact.is_fact() or not fact.is_ground():
            raise ValueError('Not a ground fact: %s' % fact)

        self._root.notify(fact.head)
