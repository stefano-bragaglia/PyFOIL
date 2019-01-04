from collections import namedtuple
from itertools import combinations
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

Candidate = namedtuple('Candidate', ['score', 'literal', 'positives', 'negatives'])

_tabling_candidates = {}


def find_candidate(
        hypotheses: List['Clause'],
        target: 'Literal',
        body: List['Literal'],
        background: List['Clause'],
        masks: List['Mask'],
        constants: List['Value'],
        positives: List['Substitution'],
        negatives: List['Substitution'],
        cache: bool = True,
) -> Optional[Candidate]:
    from foil.heuristic import gain
    from foil.heuristic import max_gain
    from foil.models import Atom
    from foil.models import Clause
    from foil.models import Literal
    from foil.models import Program

    global _tabling_candidates

    key = (
        tuple(hypotheses),
        target,
        tuple(body),
        tuple(background),
        tuple(masks),
        tuple(constants),
        tuple((k, v) for p in positives for k, v in p.items()),
        tuple((k, v) for n in negatives for k, v in n.items())
    )
    if cache and key in _tabling_candidates:
        return _tabling_candidates[key]

    candidate = None
    bound = max_gain(len(positives), len(negatives))
    variables = get_variables(target, body, cache)
    for mask in masks:
        for items in itemize(variables, mask.arity, cache):
            if all(v not in variables for v in items):
                continue

            literal = Literal(Atom(mask.functor, items), mask.negated)
            world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
            positives_i = expand(positives, target, body, literal, constants, world, False)
            negatives_i = expand(negatives, target, body, literal, constants, world, True)
            score = gain(len(positives), len(negatives), len(positives_i), len(negatives_i))
            if score > bound:
                continue

            if candidate is None or score > candidate.score:
                candidate = Candidate(score, literal, positives_i, negatives_i)

    if not cache:
        return candidate

    return _tabling_candidates.setdefault(key, candidate)


_tabling_items = {}


def itemize(
        variables: List['Variable'],
        arity: int,
        cache: bool = True,
) -> Iterable[List['Variable']]:
    global _tabling_items

    key = (tuple(variables), arity)
    if cache and key in _tabling_items:
        return _tabling_items[key]

    size = len(variables)
    values = [v for v in range(arity + size)] * arity

    items = []
    for combination in combinations(values, arity):
        if any(position < size for position in combination):
            items.append(get_items(variables, combination))

    if not cache:
        return items

    return _tabling_items.setdefault(key, items)


_tabling_expand = {}


def expand(
        substitutions: List['Substitution'],
        target: 'Literal',
        body: List['Literal'],
        candidate: 'Literal',
        constants: List['Value'],
        world: List['Literal'],
        update: bool,
        cache: bool = True,
) -> List['Substitution']:
    global _tabling_expand

    key = (tuple((k, v) for s in substitutions for k, v in s.items()),
           target, tuple(body), candidate, tuple(constants), tuple(world), update)
    if cache and key in _tabling_expand:
        return _tabling_expand[key]

    if not substitutions:
        if not cache:
            return []

        return _tabling_expand.setdefault(key, [])

    variables = get_free_variables([target, *body, candidate], substitutions[0], cache)
    if not variables:
        if not cache:
            return substitutions

        return _tabling_expand.setdefault(key, substitutions)

    if update:
        substitutions = [s for s in substitutions if target.substitute(s) not in world]
    expansion = get_expansion(substitutions, variables, constants, candidate, world, cache)

    if not cache:
        return expansion

    return _tabling_expand.setdefault(key, expansion)


_tabling_constants = {}


def get_constants(
        background: List['Clause'],
        target: 'Literal',
        cache: bool = True,
) -> List['Value']:
    from foil.unification import is_ground

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


_tabling_free_variables = {}


def get_free_variables(
        literals: List['Literal'],
        subst: 'Substitution',
        cache: bool = True,
) -> Set['Variable']:
    from foil.unification import is_variable

    global _tabling_free_variables

    key = (tuple(literals), tuple((k, v) for k, v in subst.items()))
    if cache and key in _tabling_free_variables:
        return _tabling_free_variables[key]

    free_variables = set()
    for literal in literals:
        literal = literal.substitute(subst)
        for term in literal.terms:
            if is_variable(term):
                free_variables.add(term)

    if not cache:
        return free_variables

    return _tabling_free_variables.setdefault(key, free_variables)


_tabling_expansion = {}


def get_expansion(
        substitutions: List['Substitution'],
        variables: Set['Variable'],
        constants: List['Value'],
        candidate: 'Literal',
        world: List['Literal'],
        cache: bool = True,
) -> List['Substitution']:
    global _tabling_expansion

    key = (tuple((k, v) for s in substitutions for k, v in s.items()),
           tuple(sorted(variables)), tuple(constants), candidate, tuple(world))
    if cache in key in _tabling_expansion:
        return _tabling_expansion[key]

    expansion = []
    for substitution in substitutions:
        for variable in variables:
            for constant in constants:
                expand = {**substitution, variable: constant}
                if candidate.substitute(expand) in world:
                    expansion.append(expand)

    if not cache:
        return expansion

    return _tabling_expansion.setdefault(key, expansion)


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
    for literal in [*[l for c in background for l in c.literals], target]:
        mask = literal.get_mask()
        if mask not in masks:
            masks.append(mask)

    if not cache:
        return masks

    return _tabling_masks.setdefault(key, masks)


_tabling_items = {}


def get_items(
        variables: List['Variable'],
        combination: Tuple[int, ...],
        cache: bool = True,
) -> List['Variable']:
    global _tabling_items

    key = (tuple(variables), combination)
    if cache and key in _tabling_items:
        return _tabling_items[key]

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

    return _tabling_items.setdefault(key, terms)


_tabling_variables = {}


def get_variables(
        target: 'Literal',
        body: List['Literal'],
        cache: bool = True,
) -> List['Variable']:
    from foil.unification import is_variable

    global _tabling_variables

    key = (target, tuple(body))
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


_tabling_examples = {}


def get_examples(
        target: 'Literal',
        background: List['Clause'],
        constants: List['Value'],
        examples: List['Example'],
        cache: bool = True,
) -> Tuple[List['Literal'], List['Literal']]:
    from foil.models import Label
    from foil.models import Program
    from foil.unification import is_variable

    global _tabling_examples

    key = (target, tuple(background), tuple(constants), tuple(examples))
    if cache and key in _tabling_examples:
        return _tabling_examples[key]

    positives, negatives = [], []
    for example in examples:
        literal = target.substitute(example.assignment)
        if example.label == Label.POSITIVE and example.assignment not in positives:
            positives.append(example.assignment)
        if example.label == Label.NEGATIVE and example.assignment not in negatives:
            positives.append(example.assignment)

    world = Program(background).ground()
    constants = get_constants(background, target, cache)
    variables = sorted({t for t in target.terms if is_variable(t)})
    size = len(variables)
    for combination in {c for c in combinations(constants * size, size)}:
        assignment = dict(zip(variables, combination))
        literal = target.substitute(assignment)
        if literal in world:
            if assignment not in positives:
                positives.append(assignment)
        else:
            if assignment not in negatives:
                negatives.append(assignment)

    if not cache:
        return positives, negatives

    return _tabling_examples.setdefault(key, (positives, negatives))
