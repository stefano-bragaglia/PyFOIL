import math
from collections import namedtuple
from itertools import permutations
from typing import List
from typing import Optional

Hypothesis = namedtuple('Hypothesis', ['clause', 'positives'])
Candidate = namedtuple('Candidate', ['score', 'literal', 'positives', 'negatives'])


def find_clause(
        hypotheses: List['Clause'],
        target: 'Literal',
        background: List['Clause'],
        literals: List['Literal'],
        constants: List['Value'],
        positives: List['Assignment'],
        negatives: List['Assignment'],
) -> Optional[Hypothesis]:
    from foil.models import Clause

    body, positives, negatives = [], [*positives], [*negatives]
    while negatives:
        candidate = find_literal(hypotheses, target, body, background, literals, constants, positives, negatives)
        if candidate is None:
            break

        positives = candidate.positives
        negatives = candidate.negatives
        body.append(candidate.literal)

    if not body:
        return None  # TODO Needed?

    return Hypothesis(Clause(target, body), positives)


def find_literal(
        hypotheses: List['Clause'],
        target: 'Literal',
        body: List['Literal'],
        background: List['Clause'],
        literals: List['Literal'],
        constants: List['Value'],
        positives: List['Assignment'],
        negatives: List['Assignment'],
) -> Optional['Candidate']:
    from foil.models import Clause
    from foil.models import Program

    candidate, bound = None, max_gain(positives, negatives)
    for literal in literals:
        world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
        positives_i = extend(positives, literal, constants, world)
        negatives_i = extend(negatives, literal, constants, world)
        score = gain(positives, negatives, positives_i, negatives_i)
        if candidate and bound < candidate.score:
            break

        if candidate is None or score > candidate.score:
            candidate = Candidate(score, literal, positives_i, negatives_i)

    return candidate


def max_gain(pos: List['Assignment'], neg: List['Assignment']) -> float:
    if not pos and not neg:
        return -1

    t = len(pos)
    e = entropy(len(pos), len(neg))

    return t * e


def extend(
        examples: List['Assignment'],
        literal: 'Literal',
        constants: List['Value'],
        world: List['Literal'],
) -> List['Assignment']:
    from foil.unification import is_variable

    if not examples:
        return []

    variables = {v for v in literal.terms if is_variable(v) and v not in examples[0]}
    if not variables:
        return [e for e in examples if literal.substitute(e) in world]

    size = len(variables)
    additions = [dict(zip(variables, v)) for v in set(permutations(constants * size, size))]

    return [{**e, **a} for e in examples for a in additions if literal.substitute({**e, **a}) in world]


def gain(
        pos: List['Assignment'], neg: List['Assignment'],
        pos_i: List['Assignment'], neg_i: List['Assignment'],
) -> float:
    if not pos and not neg or not pos_i and not neg_i:
        return -1

    t = len(covers(pos, pos_i))
    e = entropy(len(pos), len(neg))
    e_i = entropy(len(pos_i), len(neg_i), True)

    return t * (e - e_i)


def covers(examples: List['Assignment'], examples_i: List['Assignment']) -> List['Assignment']:
    if not examples:
        return []

    if not examples_i:
        return examples

    variables = examples[0].keys()
    coverage = [{k: v for k, v in e.items() if k in variables} for e in examples_i]

    return [e for e in examples if e in coverage]


def entropy(pos: int, neg: int, extra: bool = False) -> float:
    if pos == 0:
        return math.inf

    ratio = pos / (pos + neg)
    if extra:
        ratio += 1e-12

    return -math.log2(ratio)
