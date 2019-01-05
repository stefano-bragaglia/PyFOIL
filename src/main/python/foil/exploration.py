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
    print('-' * 120)
    print(target, ':-', body, ':', len(positives), len(negatives), '/', '%.3f' % bound)
    print('-' * 120)
    variables = get_variables(target, body, cache)
    for mask in masks:
        for items in itemize(variables, mask.arity, cache):
            literal = Literal(Atom(mask.functor, items), mask.negated)
            world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
            positives_i = expand(positives, target, body, literal, constants, world, False)
            negatives_i = expand(negatives, target, body, literal, constants, world, True)
            score = gain(len(positives), len(negatives), len(positives_i), len(negatives_i))
            if score > bound:
                print(' ', 'Skip:', target, ':-', body, literal, ':', len(positives_i), len(negatives_i), '/',
                      '%.3f' % score)
                continue

            if candidate is None or score > candidate.score:
                print('*', target, ':-', body, literal, ':', len(positives_i), len(negatives_i), '/', '%.3f' % score,
                      '+')
                candidate = Candidate(score, literal, positives_i, negatives_i)
            else:
                print('*', target, ':-', body, literal, ':', len(positives_i), len(negatives_i), '/', '%.3f' % score)

    print('-' * 120)
    print('>>>>>', target, ':-', body, candidate.literal, ':', len(candidate.positives), len(candidate.negatives), '/',
          candidate.score)
    print('-' * 120)

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
    groups = []
    for combination in combinations(values, arity):
        if any(position < size for position in combination):
            terms = get_items(variables, combination)
            if terms not in groups:
                groups.append(terms)
    ranking = []
    for terms in groups:
        unique = len(set(terms)) + arity + size - 1
        novels = len({t for t in terms if t not in variables})
        ranking.append((unique, novels, terms))
    items = [pos[-1] for pos in sorted(ranking, reverse=True)]

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


# ----------------------------------------------------------------------------------------------------------------------

def get_assignments(examples: List['Example']) -> Tuple[List['Assignment'], List['Assignment']]:
    from foil.models import Label

    pos, neg = [], []
    for example in examples:
        if example.label == Label.POSITIVE and example.assignment not in pos:
            pos.append(example.assignment)
        if example.label == Label.NEGATIVE and example.assignment not in neg:
            neg.append(example.assignment)

    return sort(pos), sort(neg)


def get_closure(
        world: List['Literal'],
        constants: List['Value'],
        target: 'Literal',
        pos: List['Assignment'],
        neg: List['Assignment'],
) -> Tuple[List['Assignment'], List['Assignment']]:
    from foil.unification import is_variable

    variables = sorted({t for t in target.terms if is_variable(t)})
    n_variables = len(variables)
    for combination in {c for c in combinations(constants * n_variables, n_variables)}:
        assignment = dict(zip(variables, combination))
        literal = target.substitute(assignment)
        if literal in world and assignment not in pos:
            pos.append(assignment)
        if literal not in world and assignment not in pos and assignment not in neg:
            neg.append(assignment)

    return sort(pos), sort(neg)


def get_masks(literals: List['Literal']) -> List['Mask']:
    masks = []
    for literal in literals:
        mask = literal.get_mask()
        if mask not in masks:
            masks.append(mask)

    return masks


def get_signature(variables: List['Variable'], combination: Tuple[int, ...]) -> List['Variable']:
    signature, i, table = [], 0, {i: v for i, v in enumerate(variables)}
    for index in combination:
        if index not in table:
            while ('V%d' % i) in variables:
                i += 1
            table[index] = 'V%d' % i
        signature.append(table[index])

    return signature


def get_variables(literals: List['Literal']) -> List['Variable']:
    from foil.unification import is_variable

    variables = []
    for literal in literals:
        for term in literal.terms:
            if is_variable(term) and term not in variables:
                variables.append(term)

    return variables


def sort(assignments: List['Assignment']) -> List['Assignment']:
    return [e[-1] for e in sorted((*[(k, v) for k, v in sorted(a.items())], a) for a in assignments)]
