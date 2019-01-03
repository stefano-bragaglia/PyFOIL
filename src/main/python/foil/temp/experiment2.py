from collections import namedtuple
from typing import List
from typing import Optional

from foil.heuristic import entropy
from foil.heuristic import gain
from foil.heuristic import max_gain
from foil.models import Clause
from foil.models import Literal
from foil.models import Mask
from foil.models import Program
from foil.unification import is_variable
from foil.unification import Substitution
from foil.unification import Value
from foil.unification import Variable

_tabling_expand = {}


def expand(
        substitutions: List[Substitution],
        variables: List[Variable],
        constants: List[Value],
        candidate: Literal,
        world: List[Literal],
        cache: bool = True,
) -> List[Substitution]:
    global _tabling_expand

    key = (
        tuple((k, v) for s in substitutions for k, v in s.items()),
        tuple(variables),
        tuple(constants),
        candidate,
        tuple(world),
    )
    if cache and key in _tabling_expand:
        return _tabling_expand[key]

    expansion = []
    for substitution in substitutions:
        if not variables:
            expansion.append(substitution)
        else:
            for variable in variables:
                for constant in constants:
                    expand = {**substitution, variable: constant}
                    if candidate.substitute(expand) in world:
                        expansion.append(expand)

    if not cache:
        return expansion
    return _tabling_expand.setdefault(key, expansion)


_tabling_loose = {}


def loose(
        target: Literal,
        body: List[Literal],
        candidate: Literal,
        example: List[Variable],
        cache: bool = True,
) -> List[Variable]:
    global _tabling_loose

    key = (target, tuple(body), candidate, tuple((k, v) for k, v in example.items()))
    if cache and key in _tabling_loose:
        return _tabling_loose[key]

    variables = sorted({t for l in [target, *body, candidate] for t in l.terms if is_variable(t) and t not in example})

    if not cache:
        return variables
    return _tabling_loose.setdefault(key, variables)


Candidate = namedtuple('LiteralEntry', ['score', 'candidate', 'positives', 'negatives'])


def find_literal(
        background: List[Clause],
        hypotheses: List[Clause],
        target: Literal,
        body: List[Literal],
        masks: List[Mask],
        positives: List[Substitution],
        negatives: List[Substitution],
        cache: bool = True,
) -> Optional[Candidate]:
    from foil.models import Atom
    from foil.learning import Candidate
    from foil.learning import get_constants
    from foil.learning import get_variables
    from foil.learning import itemize

    candidate = None
    variables = get_variables(target, body)
    constants = get_constants(background, target)
    best = max_gain(len(positives), len(negatives))
    for mask in masks:
        for items in itemize(variables, mask.arity):
            literal = Literal(Atom(mask.functor, items), mask.negated)

            bound = list((positives[0] if positives else negatives[0]).keys())
            loose = sorted({t for l in [target, *body, literal] for t in l.terms if is_variable(t) and t not in bound})

            world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()

            negatives_t = [s for s in negatives if target.substitute(s) not in world]

            positives_i = expand(positives, loose, constants, literal, world)
            negatives_i = expand(negatives_t, loose, constants, literal, world)

            score = gain(len(positives), len(negatives), len(positives_i), len(negatives_i))
            if best < score:
                continue

            if candidate is None or score > candidate.score:
                candidate = Candidate(score, literal, positives_i, negatives_i)

    return candidate


if __name__ == '__main__':
    background = [
        Clause.parse('edge(0,1).'),
        Clause.parse('edge(0,3).'),
        Clause.parse('edge(1,2).'),
        Clause.parse('edge(3,2).'),
        Clause.parse('edge(3,4).'),
        Clause.parse('edge(4,5).'),
        Clause.parse('edge(4,6).'),
        Clause.parse('edge(6,8).'),
        Clause.parse('edge(7,6).'),
        Clause.parse('edge(7,8).'),
    ]
    hypotheses = [Clause.parse('path(X,Y) :- edge(X,Y).')]
    target = Literal.parse('path(X,Y)')
    body = []
    masks = [Mask(False, 'edge', 2), Mask(False, 'path', 2)]

    positives = [
        {'X': 0, 'Y': 1},
        {'X': 0, 'Y': 2},
        {'X': 0, 'Y': 3},
        {'X': 0, 'Y': 4},
        {'X': 0, 'Y': 5},
        {'X': 0, 'Y': 6},
        {'X': 0, 'Y': 8},
        {'X': 1, 'Y': 2},
        {'X': 3, 'Y': 2},
        {'X': 3, 'Y': 4},
        {'X': 3, 'Y': 5},
        {'X': 3, 'Y': 6},
        {'X': 3, 'Y': 8},
        {'X': 4, 'Y': 5},
        {'X': 4, 'Y': 6},
        {'X': 4, 'Y': 8},
        {'X': 6, 'Y': 8},
        {'X': 7, 'Y': 6},
        {'X': 7, 'Y': 8},
    ]
    negatives = [{'X': x, 'Y': y} for x in range(9) for y in range(9) if {'X': x, 'Y': y} not in positives]

    covered = Program([*hypotheses, *background]).ground()
    positives_i = [s for s in positives if target.substitute(s) not in covered]
    negatives_i = [s for s in negatives if target.substitute(s) not in covered]

    print(
        '%.3f' % entropy(len(positives_i), len(negatives_i)),
        len(positives_i),
        len(negatives_i),
    )

    candidate = find_literal(background, hypotheses, target, body, masks, positives_i, negatives_i)
    if candidate is None:
        print('Boooh!')
    else:
        score, literal, positives_ii, negatives_ii = candidate
        print(
            target,
            ':-',
            body,
            literal,
            '\t',
            '%.3f' % entropy(len(positives_ii), len(negatives_ii)),
            '%.3f' % gain(len(positives_i), len(negatives_i), len(positives_ii), len(negatives_ii)),
            len(positives_ii),
            len(negatives_ii),
        )
