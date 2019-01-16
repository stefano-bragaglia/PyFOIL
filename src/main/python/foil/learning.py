import math
from collections import namedtuple
from itertools import combinations
from itertools import permutations
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

Hypothesis = namedtuple('Hypothesis', ['clause', 'positives'])
Candidate = namedtuple('Candidate', ['score', 'literal', 'positives', 'negatives'])


def get_closure(
        target: 'Literal',
        constants: List['Value'],
        world: List['Literal'],
        examples: List['Example'],
) -> Tuple[List['Assignment'], List['Assignment']]:
    from foil.models import Label
    from foil.unification import is_variable

    positives, negatives = [], []
    for example in examples:
        if example.label == Label.POSITIVE and example.assignment not in positives:
            positives.append(example.assignment)
        if example.label == Label.NEGATIVE and example.assignment not in negatives:
            negatives.append(example.assignment)

    variables = []
    for term in target.terms:
        if is_variable(term) and term not in variables:
            variables.append(term)
    n_variables = len(variables)

    for combination in {c for c in combinations(constants * n_variables, n_variables)}:
        assignment = dict(zip(variables, combination))
        literal = target.substitute(assignment)
        if literal in world and assignment not in positives:
            positives.append(assignment)
        if literal not in world and assignment not in positives and assignment not in negatives:
            negatives.append(assignment)

    return positives, negatives


def get_masks(literals: List['Literal']) -> List['Mask']:
    masks = []
    for literal in literals:
        mask = literal.get_mask()
        if mask not in masks:
            masks.append(mask)

    return masks


def get_constants(literals: List['Literal']) -> List['Value']:
    from foil.unification import is_ground

    constants = []
    for literal in literals:
        for term in literal.terms:
            if is_ground(term) and term not in constants:
                constants.append(term)

    return sorted(constants, key=lambda x: repr(x))


def foil(
        target: 'Literal',
        background: List['Clause'],
        masks: List['Literal'],
        constants: List['Value'],
        positives: List['Assignment'],
        negatives: List['Assignment'],
) -> List['Clause']:
    hypotheses = []
    while positives:
        hypothesis = find_clause(hypotheses, target, background, masks, constants, positives, negatives)
        if hypothesis is None:
            break

        positives = exclude(positives, hypothesis.positives)
        hypotheses.append(hypothesis.clause)

    return hypotheses


def exclude(examples: List['Assignment'], examples_i: List['Assignment']) -> List['Assignment']:
    if not examples:
        return []

    if not examples_i:
        return examples

    coverage = [{k: v for k, v in e.items() if k in examples[0]} for e in examples_i]

    return [e for e in examples if e not in coverage]


def find_clause(
        hypotheses: List['Clause'],
        target: 'Literal',
        background: List['Clause'],
        masks: List['Mask'],
        constants: List['Value'],
        positives: List['Assignment'],
        negatives: List['Assignment'],
) -> Optional[Hypothesis]:
    from foil.models import Clause

    body, positives, negatives = [], [*positives], [*negatives]
    while negatives:
        candidate = find_literal(hypotheses, target, body, background, masks, constants, positives, negatives)
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
        masks: List['Literal'],
        constants: List['Value'],
        positives: List['Assignment'],
        negatives: List['Assignment'],
) -> Optional[Candidate]:
    from foil.models import Atom
    from foil.models import Clause
    from foil.models import Literal
    from foil.models import Program

    candidate, table, bound = None, get_table([target, *body]), max_gain(positives, negatives)
    for mask in masks:
        for items in itemize(table, mask.arity):
            literal = Literal(Atom(mask.functor, items), mask.negated)
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


def get_table(literals: List['Literal']) -> Dict[int, 'Variable']:
    from foil.unification import is_variable

    variables = []
    for literal in literals:
        for term in literal.terms:
            if is_variable(term) and term not in variables:
                variables.append(term)

    return {i: v for i, v in enumerate(variables)}


def itemize(table: Dict[int, 'Variable'], arity: int) -> List[List['Variable']]:
    size = len(table)
    values = [v for v in range(arity + size)]

    signatures = []
    for combination in {c for c in combinations(values * arity, arity)}:
        if any(position < size for position in combination):
            signature = get_signature(table, combination)
            if signature not in signatures:
                signatures.append(signature)

    return signatures


def get_signature(table: Dict[int, 'Variable'], combination: Tuple[int, ...]) -> List['Variable']:
    signature, i, table = [], 0, {**table}
    for index in combination:
        if index not in table:
            while ('V%d' % i) in table.values():
                i += 1
            table[index] = 'V%d' % i
        signature.append(table[index])

    return signature


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
