from typing import Iterable

from foil.learning import covers
from foil.learning import gain
from foil.learning import itemize
from foil.models import Atom
from foil.models import Clause
from foil.models import Example
from foil.models import Label
from foil.models import Literal
from foil.models import Mask
from foil.unification import is_variable

background = [Clause(Literal(Atom('edge', t)))
              for t in [[0, 1], [0, 3], [1, 2], [3, 2], [3, 4], [4, 5], [4, 6], [6, 8], [7, 6], [7, 8]]]

masks = [Mask(False, 'edge', 2), Mask(False, 'path', 2)]

target = Literal.parse('path(X,Y)')

positives = [Example({'X': x, 'Y': y}, Label.POSITIVE)
             for x, y in [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (1, 2), (3, 2), (3, 4),
                          (3, 5), (3, 6), (3, 8), (4, 5), (4, 6), (4, 8), (6, 8), (7, 6), (7, 8)]]

negatives = [Example({'X': x, 'Y': y}, Label.NEGATIVE)
             for x in range(9) for y in range(9)
             if (x, y) not in [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (1, 2), (3, 2), (3, 4),
                               (3, 5), (3, 6), (3, 8), (4, 5), (4, 6), (4, 8), (6, 8), (7, 6), (7, 8)]]


def found(hypothesis: Iterable['Clause'], body: Iterable['Literal']) -> bool:
    return covers(background, hypothesis, target, body, positives) == positives \
           and covers(background, hypothesis, target, body, negatives) == []


if __name__ == '__main__':
    hypothesis = []

    for content in ['edge(X,X)', 'edge(X,Y)', 'edge(X,V0)', 'edge(Y,V0)']:
        positives_i = covers(background, [], target, [Literal.parse(content)], positives)
        negatives_i = covers(background, [], target, [Literal.parse(content)], negatives)
        print('%s :- %s.' % (target, content), len(positives_i), len(negatives_i))

    while True:
        # body = [Literal.parse('edge(X,V0)')]

        variables = []
        for literal in [target, *body]:
            for term in literal.terms:
                if is_variable(term) and term not in variables:
                    variables.append(term)


        body = []
        while negatives:

            best, selected = None, None
            for mask in masks:
                for terms in itemize(variables, mask.arity):
                    candidate = Literal(Atom(mask.functor, terms), mask.negated)
                    positives_i = covers(background, hypothesis, target, [*body, candidate], positives)
                    negatives_i = covers(background, hypothesis, target, [*body, candidate], negatives)
                    score = gain(positives, negatives, positives_i, negatives_i)
                    if best is None or score > best:
                        best, selected = score, candidate

            print('%.3f %s' % (best, selected))

            break

        break

    print('Done.')
