from collections import namedtuple
from itertools import combinations
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

Candidate = namedtuple('Candidate', ['score', 'literal', 'pos', 'neg'])


# ----------------------------------------------------------------------------------------------------------------------

def find_literal(
        hypotheses: List['Clause'],
        target: 'Literal',
        body: List['Literal'],
        background: List['Clause'],
        masks: List['Mask'],
        constants: List['Value'],
        positives: List['Substitution'],
        negatives: List['Substitution'],
) -> Optional[Candidate]:
    from foil.heuristic import gain
    from foil.heuristic import max_gain
    from foil.models import Atom
    from foil.models import Clause
    from foil.models import Literal
    from foil.models import Program

    candidate, bound = None, max_gain(len(positives), len(negatives))

    print('-' * 120)
    print(target, ':-', body, ':', len(positives), len(negatives), '/', '%.3f' % bound)
    print('-' * 120)

    variables = get_variables([target, *body])

    for mask in masks:
        for items in itemize(variables, mask.arity):
            literal = Literal(Atom(mask.functor, items), mask.negated)

            # TODO
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

    return candidate


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


def get_constants(literals: List['Literal']) -> List['Value']:
    from foil.unification import is_ground

    constants = []
    for literal in literals:
        for term in literal.terms:
            if is_ground(term) and term not in constants:
                constants.append(term)

    return sorted(constants, key=lambda x: repr(x))


def get_expansion(
        literal: 'Literal',
        world: List['Literal'],
        free_variables: Set['Variable'],
        constants: List['Value'],
        substitutions: List['Substitution'],
) -> List['Substitution']:
    if not free_variables:
        return substitutions

    expansion = []
    for subst in substitutions:
        for variable in free_variables:
            for constant in constants:
                expand = {**subst, variable: constant}
                if literal.substitute(expand) in world:
                    expansion.append(expand)

    return expansion


def get_free_variables(literals: List['Literal'], subst: 'Substitution') -> Set['Variable']:
    from foil.unification import is_variable

    free_variables = set()
    for literal in literals:
        literal = literal.substitute(subst)
        for term in literal.terms:
            if is_variable(term):
                free_variables.add(term)

    return free_variables


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
            while ('V%d' % i) in table.values():
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


def expand(
        target: 'Literal',
        body: List['Literal'],
        literal: 'Literal',
        world: List['Literal'],
        constants: List['Value'],
        substitutions: List['Substitution'],
) -> List['Substitution']:
    substitutions = [s for s in substitutions if target.substitute(s) not in world]
    if not substitutions:
        return []

    free_variables = get_free_variables([target, *body, literal], substitutions[0])
    if not free_variables:
        return substitutions

    return get_expansion(literal, world, free_variables, constants, substitutions)


def itemize(variables: List['Variable'], arity: int) -> List[List['Variable']]:
    size = len(variables)
    values = [v for v in range(arity + size)] * arity
    signatures = []
    for combination in combinations(values, arity):
        if any(position < size for position in combination):
            signature = get_signature(variables, combination)
            if signature not in signatures:
                signatures.append(signature)

    # TODO I don't think ordering is needed. Delete?
    # ranking = []
    # for signature in signatures:
    #     novel = len({t for t in signature if t not in variables})
    #     free = sum(1 for t in signature if t not in variables)
    #     count = len({t for t in signature})
    #     index = tuple(size - variables.index(t) for t in signature if t in variables)
    #     ranking.append((novel, free, count, index, signature))
    # signatures = [i[-1] for i in sorted(ranking, reverse=True)]

    return sorted(signatures)


def sort(assignments: List['Assignment']) -> List['Assignment']:
    return [e[-1] for e in sorted((*[(k, v) for k, v in sorted(a.items())], a) for a in assignments)]
