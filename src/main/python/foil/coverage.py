import math
from itertools import combinations
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from foil.learning import Example
from foil.learning import Label
from foil.models import Atom
from foil.models import Clause
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


def foil(
        background: List[Clause],
        target: Literal,
        masks: List[Mask],
        positives: List[Example],
        negatives: List[Example],
) -> List[Clause]:
    hypothesis = []
    while positives:
        clause, positives, negatives = learn(background, hypothesis, target, masks, positives, negatives)
        hypothesis.append(clause)

    return hypothesis


def learn(
        background: List[Clause],
        hypothesis: List[Clause],
        target: Literal,
        masks: List[Mask],
        positives: List[Example],
        negatives: List[Example],
) -> Tuple[Clause, List[Example], List[Example]]:
    body = []
    while negatives:
        selection = choose(background, hypothesis, target, body, masks, positives, negatives)
        if selection is None:
            return Clause(target, body), positives, negatives

        candidate, positives, negatives = selection
        body.append(candidate)

    return Clause(target, body), positives, negatives


def choose(
        background: List[Clause],
        hypothesis: List[Clause],
        target: Literal,
        body: List[Literal],
        masks: List[Mask],
        positives: List[Example],
        negatives: List[Example],
) -> Optional[Tuple[Literal, List[Example], List[Example]]]:
    best_score, best_candidate, best_positives, best_negatives = None, None, None, None

    variables = {t for l in [target, *body] for t in l.terms if is_variable(t)}
    for mask in masks:
        for terms in Expand(variables, mask.arity):
            candidate = Literal(Atom(mask.functor, terms), mask.negated)
            if candidate not in body:
                positives_i = uncovers(background, hypothesis, target, [*body, candidate], positives)
                if best_score is not None and max_gain(positives, negatives, positives_i) < best_score:
                    continue

                negatives_i = uncovers(background, hypothesis, target, [*body, candidate], negatives)
                score = gain(positives, negatives, positives_i, negatives_i)
                if best_score is None or score > best_score:
                    best_score, best_candidate, best_positives, best_negatives = \
                        score, candidate, positives_i, negatives_i

    if best_score is None:
        return None

    # TODO check what is returned for positives and negatives (change again uncovers to covers?)
    return best_candidate, best_positives, best_negatives


def uncovers(
        background: List[Clause],
        hypothesis: List[Clause],
        target: Literal,
        body: List[Literal],
        examples: List[Example],
) -> List[Example]:
    program = Program(list({*background, *hypothesis, Clause(target, body)}))
    world = program.get_world()

    uncovered = []
    for example in examples:
        fact = target.substitute(example.assignment)
        if example in uncovered \
                or example.label is Label.NEGATIVE and fact in world \
                or example.label is Label.POSITIVE and fact not in world:
            uncovered.append(example)

    return uncovered


def gain(
        positives: List[Example],
        negatives: List[Example],
        new_positives: List[Example],
        new_negatives: List[Example],
) -> float:
    return common(positives, new_positives) * (entropy(positives, negatives) - entropy(new_positives, new_negatives))


def max_gain(
        positives: List[Example],
        negatives: List[Example],
        new_positives: List[Example],
) -> float:
    return common(positives, new_positives) * entropy(positives, negatives)


def common(positives: List[Example], new_positives: List[Example]) -> int:
    return sum(1 for e in new_positives if e in positives)


def entropy(positives: List[Example], negatives: List[Example]) -> float:
    return -math.log2(len(positives) / (len(positives) + len(negatives)))


def _background() -> List[Clause]:
    return [Clause(Literal(Atom('edge', t))) for t in [[0, 1], [0, 3], [1, 2], [3, 2], [3, 4],
                                                       [4, 5], [4, 6], [6, 8], [7, 6], [7, 8]]]


def _target() -> Literal:
    return Literal.parse('path(X,Y)')


def _masks() -> List[Mask]:
    return [Mask(False, 'edge', 2), Mask(False, 'path', 2)]


def _positives() -> List[Example]:
    return [Example({'X': x, 'Y': y}, Label.POSITIVE)
            for x, y in [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (1, 2), (3, 2), (3, 4),
                         (3, 5), (3, 6), (3, 8), (4, 5), (4, 6), (4, 8), (6, 8), (7, 6), (7, 8)]]


def _negatives() -> List[Example]:
    return [Example({'X': x, 'Y': y}, Label.NEGATIVE)
            for x in range(9) for y in range(9)
            if (x, y) not in [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (1, 2), (3, 2), (3, 4),
                              (3, 5), (3, 6), (3, 8), (4, 5), (4, 6), (4, 8), (6, 8), (7, 6), (7, 8)]]


if __name__ == '__main__':
    result = foil(_background(), _target(), _masks(), _positives(), _negatives())
    print(len(result), result)
    print()

    print('Done.')
