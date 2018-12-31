from typing import List

from foil.learning import learn
from foil.models import Atom
from foil.models import Clause
from foil.models import Example
from foil.models import Label
from foil.models import Literal
from foil.models import Mask


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
    result = learn(_background(), _target(), _masks(), _positives(), _negatives())
    for i, clause in enumerate(result):
        print(i + 1, '\t', clause)
    print()

    print('Done.')
