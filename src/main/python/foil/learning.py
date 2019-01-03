import math
from collections import namedtuple
from itertools import combinations
from itertools import permutations
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

Hypothesis = namedtuple('Hypothesis', ['clause', 'positives'])

_tabling_learn_hypotheses = {}


def learn_hypotheses(
        background: List['Clause'],
        target: 'Literal',
        masks: List['Mask'],
        positives: List['Literal'],
        negatives: List['Literal'],
        cache: bool = True,
) -> List['Clause']:
    global _tabling_learn_hypotheses

    key = (tuple(background), target, tuple(masks), tuple(positives), tuple(negatives))
    if cache and key in _tabling_learn_hypotheses:
        return _tabling_learn_hypotheses[key]

    excluded = []
    hypotheses = []
    while positives:
        result = learn_clause(background, hypotheses, excluded, target, masks, positives, negatives)
        if result is None:
            break

        if result.positives == positives:
            excluded.append(result.clause)
            continue

        print(result.clause)
        hypotheses.append(result.clause)
        positives = result.positives
        excluded = []

    if not cache:
        return hypotheses
    return _tabling_learn_hypotheses.setdefault(key, hypotheses)


Candidate = namedtuple('LiteralEntry', ['score', 'candidate', 'positives', 'negatives'])

_tabling_learn_clause = {}


def learn_clause(
        background: List['Clause'],
        hypotheses: List['Clause'],
        excluded: List['Clause'],
        target: 'Literal',
        masks: List['Mask'],
        positives: List['Literal'],
        negatives: List['Literal'],
        cache: bool = True
) -> Optional[Hypothesis]:
    from foil.models import Clause

    global _tabling_learn_clause

    key = (
        tuple(background), tuple(hypotheses), tuple(excluded), target, tuple(masks), tuple(positives), tuple(negatives))
    if cache and key in _tabling_learn_clause:
        return _tabling_learn_clause[key]

    body = []
    while negatives and not is_over(target, body):
        result = find_literal(background, hypotheses, excluded, target, body, masks, positives, negatives)
        if result is None:
            break

        print('\t', body, result.candidate, '%.3f' % result.score)
        body.append(result.candidate)
        positives = result.positives
        negatives = result.negatives

    print(len(positives), len(negatives))
    hypothesis = Hypothesis(Clause(target, body), positives)
    if not cache:
        return hypothesis
    return _tabling_learn_clause.setdefault(key, hypothesis)


_tabling_over = {}


def is_over(
        target: 'Literal',
        body: List['Literal'],
        cache: bool = True,
) -> bool:
    global _tabling_over

    key = (target, tuple(body))
    if cache and key in _tabling_over:
        return _tabling_over[key]

    if not body:
        if not cache:
            return False
        return _tabling_over.setdefault(key, False)

    frequencies = get_frequencies([target, *body], cache)

    if not cache:
        return 1 not in frequencies.values()
    return _tabling_over.setdefault(key, 1 not in frequencies.values())


_tabling_literal = {}


def find_literal(
        background: List['Clause'],
        hypotheses: List['Clause'],
        excluded: List['Clause'],
        target: 'Literal', body: List['Literal'],
        masks: List['Mask'],
        positives: List['Literal'],
        negatives: List['Literal'],
        cache: bool = True,
) -> Optional[Candidate]:
    from foil.models import Atom
    from foil.models import Literal
    from foil.models import Program

    global _tabling_literal

    key = (tuple(background), tuple(hypotheses), tuple(excluded), target, tuple(body), tuple(masks), tuple(positives),
           tuple(negatives))
    if cache and key in _tabling_literal:
        return _tabling_literal[key]

    candidate = None
    variables = get_variables(target, body)
    for mask in masks:
        for items in itemize(variables, mask.arity):
            literal = Literal(Atom(mask.functor, items), mask.negated)
            if not is_valid(hypotheses, excluded, target, body, literal):
                continue

            clauses = get_clauses(background, hypotheses, target, [*body, literal])
            program = Program(clauses)
            world = program.ground()

            positives_i = [p for p in positives if p in world]
            negatives_i = [n for n in negatives if n not in world]
            # if negatives_i == negatives:
            #     continue

            score = gain(positives, negatives, positives_i, negatives_i)
            print('\t\t', '%.3f' % score, len(positives_i), len(negatives_i), body, literal)
            if candidate is None or score > candidate.score:
                candidate = Candidate(score, literal, positives_i, negatives_i)

    if not cache:
        return candidate
    return _tabling_literal.setdefault(key, candidate)


_tabling_valid = {}


def is_valid(
        hypotheses: List['Clause'],
        excluded: List['Clause'],
        target: 'Literal',
        body: List['Literal'],
        literal: 'Literal',
        cache: bool = True,
) -> bool:
    from foil.models import Clause

    global _tabling_valid

    key = (tuple(hypotheses), tuple(excluded), target, tuple(body), literal)
    if cache and key in _tabling_valid:
        return _tabling_valid[key]

    if literal == target or simplify(target, body, literal) in simplify(target, body):
        if not cache:
            return False
        return _tabling_valid.setdefault(key, False)

    hypothesis = Clause(target, [*body, literal])
    value = hypothesis not in hypotheses and not hypothesis in excluded

    if not cache:
        return value
    return _tabling_valid.setdefault(key, value)


_tabling_simplify = {}


def simplify(
        target: 'Literal',
        body: List['Literal'],
        literal: 'Literal' = None,
        cache: bool = True,
) -> Union['Literal', List['Literal']]:
    global _tabling_simplify

    if literal is None:
        key = (target, tuple(body))
    else:
        key = (target, tuple(body), literal)
    if cache and key in _tabling_simplify:
        return _tabling_simplify[key]

    if literal is None:
        subst = {k: '_' for k, v in get_frequencies([target, *body], cache).items() if v == 1}
        result = [target.substitute(subst), *[l.substitute(subst) for l in body]]
    else:
        subst = {k: '_' for k, v in get_frequencies([target, *body, literal], cache).items() if v == 1}
        result = literal.substitute(subst)

    if not cache:
        return result
    return _tabling_simplify.setdefault(key, result)


_tabling_clauses = {}


def get_clauses(
        background: List['Clause'],
        hypotheses: List['Clause'],
        target: 'Literal',
        body: List['Literal'],
        cache: bool = True,
) -> List['Clause']:
    from foil.models import Clause
    from foil.models import Program

    global _tabling_clauses

    candidate = Clause(target, body)
    key = Program([*hypotheses, candidate, *background])
    if cache and key in _tabling_clauses:
        return _tabling_clauses[key]

    clauses = []
    for clause in key.clauses:
        if clause not in clauses:
            clauses.append(clause)

    if not cache:
        return clauses
    return _tabling_clauses.setdefault(key, clauses)


_tabling_constants = {}


def get_constants(
        background: List['Clause'],
        target: 'Literal',
        cache: bool = True,
) -> List['Value']:
    from foil.unification import is_ground

    global _tabling_constants

    key = (tuple(background), target)
    if cache and key in _tabling_constants:
        return _tabling_constants[key]

    constants = []
    for literal in [target, *[l for c in background for l in c.literals]]:
        for term in literal.terms:
            if is_ground(term) and term not in constants:
                constants.append(term)

    if not cache:
        return constants
    return _tabling_constants.setdefault(key, constants)


_tabling_examples = {}


def get_examples(
        background: List['Clause'],
        target: 'Literal',
        examples: List['Example'],
        cache: bool = True,
) -> Tuple[List['Literal'], List['Literal']]:
    from foil.models import Example
    from foil.models import Label

    global _tabling_examples

    key = (tuple(background), target, tuple(examples))
    if cache and key in _tabling_examples:
        return _tabling_examples[key]

    variables = get_variables(target, [])
    constants = get_constants(background, target, cache)
    for values in permutations(constants * len(variables), len(variables)):
        assignment = dict(zip(variables, values))
        if Example(assignment) in examples:
            continue

        example = Example(assignment, Label.NEGATIVE)
        if example not in examples:
            examples.append(example)

    positives, negatives = [], []
    for example in examples:
        literal = target.substitute(example.assignment)
        if example.label is Label.POSITIVE and literal not in positives:
            positives.append(literal)
        if example.label is Label.NEGATIVE and literal not in negatives:
            negatives.append(literal)

    if not cache:
        return positives, negatives
    return _tabling_examples.setdefault(key, (positives, negatives))


_tabling_frequencies = {}


def get_frequencies(
        literals: List['Literal'],
        cache: bool = True,
) -> Dict['Variable', int]:
    from foil.unification import is_variable

    global _tabling_frequencies

    key = tuple(literals)
    if cache and key in _tabling_frequencies:
        return _tabling_frequencies[key]

    frequencies = {}
    for literal in literals:
        for term in literal.terms:
            if is_variable(term):
                frequencies[term] = frequencies.get(term, 0) + 1

    if not cache:
        return frequencies
    return _tabling_frequencies.setdefault(key, frequencies)


_tabling_masks = {}


def get_masks(
        background: List['Clause'],
        target: 'Literal',
        cache: bool = True,
) -> List['Mask']:
    from foil.models import Clause
    from foil.models import Program

    global _tabling_masks

    candidate = Clause(target)
    key = Program([candidate, *background])
    if cache and key in _tabling_masks:
        return _tabling_masks[key]

    masks = []
    # for literal in [target, *[l for c in background for l in c.literals]]:
    for literal in [*[l for c in background for l in c.literals], target]:
        mask = literal.get_mask()
        if mask not in masks:
            masks.append(mask)

    if not cache:
        return masks
    return _tabling_masks.setdefault(key, masks)


_tabling_terms = {}


def get_terms(
        variables: List['Variable'],
        combination: Tuple[int, ...],
        cache: bool = True,
) -> List['Variable']:
    global _tabling_terms

    key = (tuple(variables), combination)
    if cache and key in _tabling_terms:
        return _tabling_terms[key]

    terms = []
    i, table = 0, {i: v for i, v in enumerate(variables)}
    for index in combination:
        if index not in table:
            while ('V%d' % i) in variables:
                i += 1
            table[index] = 'V%d' % i
        terms.append(table[index])

    if not cache:
        return terms
    return _tabling_terms.setdefault(key, terms)


_tabling_variables = {}


def get_variables(
        target: 'Literal',
        body: List['Literal'],
        cache: bool = True,
) -> List['Variable']:
    from foil.models import Clause
    from foil.unification import is_variable

    global _tabling_variables

    key = Clause(target, body)
    if cache and key in _tabling_variables:
        return _tabling_variables[key]

    variables = []
    for literal in [target, *body]:
        for term in literal.terms:
            if is_variable(term) and term not in variables:
                variables.append(term)

    if not cache:
        return variables
    return _tabling_variables.setdefault(key, variables)


_tabling_itemize = {}


def itemize(
        variables: List['Variable'],
        arity: int,
        cache: bool = True,
) -> Iterable[List['Term']]:
    global _tabling_itemize

    key = tuple([*variables, arity])
    if cache and key in _tabling_itemize:
        return _tabling_itemize[key]

    size = len(variables)
    values = [v for v in range(arity + size)] * arity
    signatures = {tuple(get_terms(variables, c)) for c in combinations(values, arity) if any(p < size for p in c)}
    indexes = sorted([(
        len(set(signature)),
        sum(1 for v in set(signature) if v not in variables),
        [size - variables.index(v) for v in signature if v in variables],
        signature
    ) for signature in signatures], reverse=True)
    items = [i[-1] for i in indexes]

    if not cache:
        return items
    return _tabling_itemize.setdefault(key, items)


_tabling_gain = {}


def gain(
        positives: List['Literal'],
        negatives: List['Literal'],
        positives_i: List['Literal'],
        negatives_i: List['Literal'],
        cache: bool = True,
) -> float:
    global _tabling_gain

    key = (tuple(positives), tuple(negatives), tuple(positives_i), tuple(negatives_i))
    if cache and key in _tabling_gain:
        return _tabling_gain[key]

    common = sum(1 for p in positives_i if p in positives)
    if common == 0:
        if not cache:
            return 0
        return _tabling_gain.setdefault(key, 0)

    information = entropy(positives, negatives)
    information_i = entropy(positives_i, negatives_i)
    difference = information - information_i
    value = common * difference

    if not cache:
        return value
    return _tabling_gain.setdefault(key, value)


_tabling_entropy = {}


def entropy(
        positives: List['Literal'],
        negatives: List['Literal'],
        cache: bool = True,
) -> float:
    global _tabling_entropy

    key = (tuple(positives), tuple(negatives))
    if cache and key in _tabling_entropy:
        return _tabling_entropy[key]

    num = sum(1 for e in positives)
    den = num + sum(1 for e in negatives)
    if den == 0 or num == den:
        if not cache:
            return 0
        return _tabling_entropy.setdefault(key, 0)

    if num == 0:
        if not cache:
            return math.inf
        return _tabling_entropy.setdefault(key, math.inf)

    value = -math.log2(num / den)
    if not cache:
        return value
    return _tabling_entropy.setdefault(key, value)
