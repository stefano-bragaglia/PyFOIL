from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from foil.models import Literal
from foil.models import Program
from foil.unification import normalize
from foil.unification import Value
from foil.unification import Variable

Assignment = Dict[Variable, Value]


class Label(Enum):
    NEGATIVE = 0
    POSITIVE = 1


class Example:
    def __init__(self, assignment: Assignment, label: Label = Label.POSITIVE):
        self._assignment = assignment
        self._label = label

    @property
    def assignment(self) -> Assignment:
        return self._assignment

    @property
    def label(self) -> Label:
        return self._label

    @property
    def variables(self) -> Iterable[Variable]:
        return self._assignment.keys()

    def __hash__(self) -> int:
        value = hash(self._label)
        for var, val in self._assignment.items():
            value = value ** hash(var) ** hash(val)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._label != other._label:
            return False

        return self._assignment == other._assignment

    def __repr__(self) -> str:
        return '<%s>(%s)' % (
            ', '.join('%s=%s' % (normalize(v), normalize(t)) for v, t in sorted(self._assignment.items())),
            '-' if self._label == Label.NEGATIVE else '+'
        )

    def get_value(self, variable: Variable) -> Optional[Value]:
        return self._assignment.get(variable)


class Target:
    def __init__(self, relation: Literal, examples: List[Example] = None):
        self._relation = relation
        self._examples = examples or []

    @property
    def relation(self) -> Literal:
        return self._relation

    @property
    def examples(self) -> Iterable[Example]:
        return self._examples

    def __hash__(self) -> int:
        value = hash(self._relation)
        for example in self._examples:
            value = value ** hash(example)

        return value

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


class Problem:

    def __init__(self, program: Program, targets: List[Target] = None):
        self._program = program
        self._targets = targets or []

    def __hash__(self) -> int:
        value = hash(self._program)
        for target in self._targets:
            value = value ** hash(target)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Problem):
            return False

        if self._program != other._program:
            return False

        if len(self._targets) != len(other._clauses):
            return False

        return all(c in other._clauses for c in self._clauses)

    def __repr__(self) -> str:
        return '\n'.join(repr(c) for c in self._clauses)


if __name__ == '__main__':
    e1 = Example({'A': 0, 'B': 1}, Label.POSITIVE)
    e2 = Example({'A': 2, 'B': 1}, Label.NEGATIVE)
    t = Target(Literal.parse('pred(A, B)'), [e1, e2])
    print(t)


    # print(hash(e1), hash(e2))
