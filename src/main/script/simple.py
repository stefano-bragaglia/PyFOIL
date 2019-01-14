import datetime
import math
from itertools import permutations
from typing import List
from typing import Optional

from foil.old.learning import Candidate
from foil.old.learning import Hypothesis
from foil.models import Assignment
from foil.models import Clause
from foil.models import Literal
from foil.models import Program
from foil.unification import is_variable
from foil.unification import Value



def foil(
        target: Literal,
        background: List[Clause],
        positives: List[Assignment],
        negatives: List[Assignment],
) -> List[Clause]:
    hypotheses = []
    while positives:
        hypothesis = find_clause(hypotheses, target, background, positives, negatives)
        if hypothesis is None:
            break

        positives = exclude(positives, covers(positives, hypothesis.pos))
        hypotheses.append(hypothesis.clause)

    return hypotheses



def find_clause(
        hypotheses: List[Clause],
        target: Literal,
        background: List[Clause],
        positives: List[Assignment],
        negatives: List[Assignment],
) -> Optional[Hypothesis]:
    body, positives, negatives = [], [*positives], [*negatives]
    while negatives:
        candidate = find_literal(hypotheses, target, body, background, positives, negatives)
        if candidate is None:
            break

        positives = candidate.pos
        negatives = candidate.neg
        body.append(candidate.literal)

    if not body:
        return None  # TODO Needed?

    return Hypothesis(Clause(target, body), positives)



def find_literal(
        hypotheses: List[Clause],
        target: Literal,
        body: List[Literal],
        background: List[Clause],
        positives: List[Assignment],
        negatives: List[Assignment],
) -> Optional[Candidate]:
    candidate = None
    for literal in get_literals():
        world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
        positives_i = extend(positives, literal, world)
        negatives_i = extend(negatives, literal, world)
        score = gain(positives, negatives, positives_i, negatives_i)
        if candidate is None or score > candidate.score:
            candidate = Candidate(score, literal, positives_i, negatives_i)

    return candidate



def get_literals() -> List[Literal]:
    return [
        Literal.parse('edge(X,V0)'), Literal.parse('edge(V0,Y)'),
        Literal.parse('edge(V0,X)'), Literal.parse('edge(Y,V0)'),
        Literal.parse('edge(Y,X)'), Literal.parse('edge(X,Y)'),
        Literal.parse('edge(X,X)'), Literal.parse('edge(Y,Y)'),
        Literal.parse('path(X,V0)'), Literal.parse('path(V0,Y)'),
        Literal.parse('path(V0,X)'), Literal.parse('path(Y,V0)'),
        Literal.parse('path(Y,X)'), Literal.parse('path(X,Y)'),
        Literal.parse('path(X,X)'), Literal.parse('path(Y,Y)'),
    ]


def get_constants() -> List[Value]:
    return [0, 1, 2, 3, 4, 5, 6, 7, 8]



def extend(examples: List[Assignment], literal: Literal, world: List[Literal]) -> List[Assignment]:
    if not examples:
        return []

    variables = {v for v in literal.terms if is_variable(v) and v not in examples[0]}
    if not variables:
        return [e for e in examples if literal.substitute(e) in world]

    size = len(variables)
    additions = [dict(zip(variables, v)) for v in set(permutations(get_constants() * size, size))]

    return [{**e, **a} for e in examples for a in additions if literal.substitute({**e, **a}) in world]



def covers(examples: List[Assignment], examples_i: List[Assignment]) -> List[Assignment]:
    reference = [pi.items() for pi in examples_i]

    return [e for e in examples if any(all(item in items for item in e.items()) for items in reference)]



def exclude(examples: List[Assignment], coverage: List[Assignment]) -> List[Assignment]:
    return [p for p in examples if p not in coverage]



def gain(pos: List[Assignment], neg: List[Assignment], pos_i: List[Assignment], neg_i: List[Assignment]) -> float:
    if not pos and not neg or not pos_i and not neg_i:
        return -1

    t = len(covers(pos, pos_i))
    e = entropy(pos, neg)
    e_i = entropy(pos_i, neg_i, True)

    return t * (e - e_i)



def entropy(pos: List[Assignment], neg: List[Assignment], extra: bool = False) -> float:
    num = len(pos)
    den = num + len(neg)
    ratio = num / den
    if extra:
        ratio += 1e-12

    if ratio == 0:
        return -math.inf

    return -math.log2(ratio)


class Measure:
    def __init__(self):
        self.elapsed = None

    def __enter__(self):
        self.elapsed = datetime.datetime.now()

    def __exit__(self, ty, val, tb):
        print('\nElapsed time: %s sec.\n' % (datetime.datetime.now() - self.elapsed))


if __name__ == '__main__':
    target = Literal.parse('path(X,Y)')
    positives = [
        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
    ]
    negatives = [
        {'X': 0, 'Y': 0}, {'X': 0, 'Y': 7}, {'X': 1, 'Y': 0}, {'X': 1, 'Y': 1}, {'X': 1, 'Y': 3},
        {'X': 1, 'Y': 4}, {'X': 1, 'Y': 5}, {'X': 1, 'Y': 6}, {'X': 1, 'Y': 7}, {'X': 1, 'Y': 8},
        {'X': 2, 'Y': 0}, {'X': 2, 'Y': 1}, {'X': 2, 'Y': 2}, {'X': 2, 'Y': 3}, {'X': 2, 'Y': 4},
        {'X': 2, 'Y': 5}, {'X': 2, 'Y': 6}, {'X': 2, 'Y': 7}, {'X': 2, 'Y': 8}, {'X': 3, 'Y': 0},
        {'X': 3, 'Y': 1}, {'X': 3, 'Y': 3}, {'X': 3, 'Y': 7}, {'X': 4, 'Y': 0}, {'X': 4, 'Y': 1},
        {'X': 4, 'Y': 2}, {'X': 4, 'Y': 3}, {'X': 4, 'Y': 4}, {'X': 4, 'Y': 7}, {'X': 5, 'Y': 0},
        {'X': 5, 'Y': 1}, {'X': 5, 'Y': 2}, {'X': 5, 'Y': 3}, {'X': 5, 'Y': 4}, {'X': 5, 'Y': 5},
        {'X': 5, 'Y': 6}, {'X': 5, 'Y': 7}, {'X': 5, 'Y': 8}, {'X': 6, 'Y': 0}, {'X': 6, 'Y': 1},
        {'X': 6, 'Y': 2}, {'X': 6, 'Y': 3}, {'X': 6, 'Y': 4}, {'X': 6, 'Y': 5}, {'X': 6, 'Y': 6},
        {'X': 6, 'Y': 7}, {'X': 7, 'Y': 0}, {'X': 7, 'Y': 1}, {'X': 7, 'Y': 2}, {'X': 7, 'Y': 3},
        {'X': 7, 'Y': 4}, {'X': 7, 'Y': 5}, {'X': 7, 'Y': 7}, {'X': 8, 'Y': 0}, {'X': 8, 'Y': 1},
        {'X': 8, 'Y': 2}, {'X': 8, 'Y': 3}, {'X': 8, 'Y': 4}, {'X': 8, 'Y': 5}, {'X': 8, 'Y': 6},
        {'X': 8, 'Y': 7}, {'X': 8, 'Y': 8},
    ]
    background = [
        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
        Clause.parse('edge(7,8).'),
    ]

    for i in range(5):
        with Measure():
            for clause in foil(target, background, positives, negatives):
                print(clause)
