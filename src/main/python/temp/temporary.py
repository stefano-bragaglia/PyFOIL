import math
from itertools import combinations
from itertools import permutations
from typing import List
from typing import Set
from typing import Tuple

from foil.learning import Example
from foil.learning import Label
from foil.learning import Problem
from foil.learning import Target
from foil.models import Atom
from foil.models import Literal
from foil.models import Mask
from foil.models import Program
from foil.unification import is_variable
from foil.unification import Variable


class Expand:
    _tabling = {}

    def __init__(self, variables: Set[Variable], arity: int):
        self._variables = tuple(variables)
        self._arity = arity

        self._combinations = combinations([v for v in range(arity + len(variables))] * arity, arity)
        self._visited = {}

    def __iter__(self):
        self._visited = {}
        return self

    def __next__(self):
        for combo in self._combinations:
            if any(i < len(self._variables) for i in combo):
                signature = self._tabling.setdefault(self._variables, {}).setdefault(combo, self._as_terms(combo))
                if signature not in self._visited:
                    return self._visited.setdefault(signature, list(signature))

        raise StopIteration()

    def _as_terms(self, combination: Tuple[int, ...]) -> Tuple[Variable]:
        terms = tuple()
        i, table = 0, {i: v for i, v in enumerate(self._variables)}
        for index in combination:
            if index not in table:
                while ('V%d' % i) in self._variables:
                    i += 1
                table[index] = 'V%d' % i
            terms = (*terms, table[index])

        return terms


# class Generate:
#     _tabling = {}
#
#     def __init__(self, variables: List[Variable], mask: Mask):
#         self._variables = variables
#         self._mask = mask
#
#         self._signatures = Expand(variables, mask.arity)
#         self._visited = {}
#
#     def __iter__(self):
#         self._visited = {}
#         return self
#
#     def __next__(self):
#         for signature in self._signatures:
#             self._tabling.setdefault(self._variables, {}).setdefault(self._mask, )
#
#         try:
#             mask = next(self._masks)
#         except
#             for mask in self._masks:
#                 for terms in Expand(variables, mask.arity):
#                     return Literal(Atom(mask.functor, terms), mask.negated)
#
#         raise StopIteration()

def complete(target: Target, program: Program) -> Target:
    variables = target.get_variables()
    constants = program.get_constants() * len(variables)

    examples = set()
    for values in permutations(constants, len(variables)):
        assignment = dict(zip(variables, values))
        if Example(assignment) not in target.examples:
            example = Example(assignment, Label.NEGATIVE)
            if example not in target.examples:
                examples.add(example)

    return Target(target.relation, sorted(examples, key=lambda x: repr(x)))


def learn(target: Literal, positives: List[Example], negatives: List[Example], masks: List[Mask]):
    hypothesis = []
    while positives:
        body = []
        while negatives:
            variables = {t for l in [target, *body] for t in l.terms if is_variable(t)}
            best, candidate = None, None
            for mask in masks:
                for terms in Expand(variables, mask.arity):
                    literal = Literal(Atom(mask.functor, terms), mask.negated)
                    if literal not in body:
                        print(candidate)
                        break

    return hypothesis


def gain(e1: List[Example], e2: List[Example]) -> float:
    return common(e1, e2) * (entropy(e1) - entropy(e2))


def max_gain(e1: List[Example], e2: List[Example]) -> float:
    return common(e1, e2) * entropy(e1)


def common(e1: List[Example], e2: List[Example]) -> int:
    return sum(1 for e in e1 if e in e2)


def entropy(examples: List[Example]) -> float:
    return -math.log2(sum(1 for e in examples if e.label is Label.POSITIVE) / len(examples))


source = 'edge(0,1). edge(0,3). edge(1,2). edge(3,2). edge(3,4). edge(4,5). edge(4,6). edge(6,8). edge(7,6). edge(7,8).'

dataset = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (1, 2), (3, 2), (3, 4), (3, 5), (3, 6), (3, 8),
           (4, 5), (4, 6), (4, 8), (6, 8), (7, 6), (7, 8)]

if __name__ == '__main__':
    program = Program.parse(source)
    relation = Literal.parse('path(X,Y)')
    examples = [Example(dict(zip([*'XY'], data))) for data in dataset]
    target = Target(relation, examples)
    problem = Problem(complete(target, program), program)
    print(problem)
    print()

    print(problem.get_masks())
    print()
