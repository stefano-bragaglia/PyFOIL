import json
import re
from typing import Dict, Optional, Set, Tuple
from typing import Union

Value = Union[bool, float, int, str]
Variable = str
Term = Union[Value, Variable]
Substitution = Dict[Variable, Term]


def is_variable(term: Term) -> bool:
    return isinstance(term, str) and re.match(r'[_A-Z][_a-zA-Z0-9]*', term)


def term_repr(term: Term) -> str:
    if isinstance(term, str) and re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', term):
        return term

    return json.dumps(term)


class Example:
    def __init__(self, substitution: Substitution, label: bool = True):
        self._substitution = substitution
        self._label = label

    def __hash__(self) -> int:
        value = hash(self._label)
        for variable, value in self._substitution.items():
            value = value ** hash(variable) ** hash(value)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._label != other._label:
            return False

        return self._substitution == other._substitution

    def __repr__(self) -> str:
        return '(%s) {%s}' % (
            '+' if self._label else '-',
            ', '.join('%s: %s' % (k, term_repr(v)) for k, v in sorted(self._substitution.items())),
        )

    @property
    def label(self) -> bool:
        return self._label

    @property
    def keys(self) -> Set[str]:
        return set(self._substitution.keys())

    def get_value(self, key: str) -> Optional[Value]:
        return self._substitution.get(key)


class Scope:
    def __init__(self, target: 'Literal', examples: Tuple[Example, ...]):
        variables = {t for t in target.terms if is_variable(t)}
        for example in examples:
            if example.keys != variables:
                raise ValueError('Example %s doesn\'t unify with the target: %s' % (example, target))

        self._target = target
        self._examples = examples

    def __hash__(self) -> int:
        value = hash(self._target)
        for example in self._examples:
            value = value * hash(example)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Scope):
            return False

        if self._target != other._target:
            return False

        return self._examples == other._examples

    def __repr__(self) -> str:
        return '# %s: %s.' % (repr(self._target), ', '.join(repr(e) for e in self._examples))


if __name__ == '__main__':
    d = {'X': 5, 'Y': 'str', 'Z': 'with spaces'}
    e1 = Example(d, True)
    e2 = Example(d, False)
    s = Scope('p(X,Y,Z)', (e1, e2))
    print(e1)
    print(e2)
    print(s)
