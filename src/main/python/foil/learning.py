from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from foil.models import Clause
from foil.models import Literal
from foil.models import Program
from foil.unification import normalize
from foil.unification import Term
from foil.unification import Value
from foil.unification import Variable

Assignment = Dict[Variable, Value]


class Label(Enum):
    NEGATIVE = '-'
    POSITIVE = '+'


class Example:
    def __init__(self, assignment: Assignment, label: Label = Label.POSITIVE):
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
            ', '.join('%s=%s' % (normalize(v), normalize(t)) for v, t in sorted(self._assignment.items())),
            self._label.value
        )

    @property
    def assignment(self) -> Assignment:
        return self._assignment

    @property
    def label(self) -> Label:
        return self._label

    @property
    def variables(self) -> Iterable[Variable]:
        return self._assignment.keys()

    def get_value(self, variable: Variable) -> Optional[Value]:
        return self._assignment.get(variable)


class Target:
    def __init__(self, relation: Literal, examples: List[Example] = None):
        self._relation = relation
        self._examples = examples or []

    def __hash__(self) -> int:
        return hash((self._relation, *self._examples))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Target):
            return False

        if self._relation != other._relation:
            return False

        if len(self._examples) != len(other._examples):
            return False

        for example in self._examples:
            if example not in other._examples:
                return False

        return True

    def __repr__(self) -> str:
        if not self._examples:
            return '#%s.' % repr(self._relation)

        return '#%s: %s.' % (repr(self._relation), ', '.join(repr(e) for e in self._examples))

    @property
    def relation(self) -> Literal:
        return self._relation

    @property
    def examples(self) -> Iterable[Example]:
        return self._examples


class Problem:

    def __init__(self, target: Target, program: Program):
        self._target = target
        self._program = program

    def __hash__(self) -> int:
        return hash((self._target, self._program))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Problem):
            return False

        if self._target != other._target:
            return False

        return self._program == other._program

    def __repr__(self) -> str:
        return '%s\n\n%s' % (repr(self._target), repr(self._program))

    @property
    def target(self) -> Target:
        return self.target

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._program.clauses

    @property
    def program(self) -> Program:
        return self._program

    def get_clause(self, index: int) -> Optional[Clause]:
        return self._program.get_clause(index)

    def get_constants(self) -> List[Term]:
        return self._program.get_constants()

    def get_facts(self) -> Iterable[Clause]:
        return self._program.get_facts()

    def get_rules(self) -> Iterable[Clause]:
        return self._program.get_rules()

    def is_ground(self) -> bool:
        return self._program.is_ground()


if __name__ == '__main__':
    e1 = Example({'A': 0, 'B': 1}, Label.POSITIVE)
    e2 = Example({'A': 2, 'B': 1}, Label.NEGATIVE)
    t = Target(Literal.parse('pred(A, B)'), [e1, e2])
    print(t)

    print(hash(e1), hash(e2))