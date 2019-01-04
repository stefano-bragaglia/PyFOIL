from collections import namedtuple
from typing import List

Hypothesis = namedtuple('Hypothesis', ['clause', 'positives'])

_tabling_learn_hypotheses = {}


def learn_hypotheses(
        target: 'Literal',
        background: List['Clause'],
        examples: List['Example'],
        cache: bool = True,
) -> List['Clause']:
    from foil.exploration import get_constants
    from foil.exploration import get_examples
    from foil.exploration import get_masks

    global _tabling_learn_hypotheses

    key = (target, tuple(background), tuple(examples))
    if cache and key in _tabling_learn_hypotheses:
        return _tabling_learn_hypotheses[key]

    hypotheses = []
    masks = get_masks(background, target, cache)
    constants = get_constants(background, target, cache)
    positives, negatives = get_examples(target, background, constants, examples, cache)
    while positives:
        result = learn_clause(hypotheses, target, background, masks, constants, positives, negatives, cache)
        if result is None:
            break

        print(result.clause)
        hypotheses.append(result.clause)
        positives = result.positives

    if not cache:
        return hypotheses

    return _tabling_learn_hypotheses.setdefault(key, hypotheses)


_tabling_learn_clause = {}


def learn_clause(
        hypotheses: List['Clause'],
        target: 'Literal',
        background: List['Clause'],
        masks: List['Mask'],
        constants: List['Value'],
        positives: List['Substitution'],
        negatives: List['Substitution'],
        cache: bool = True,
):
    from foil.exploration import find_candidate
    from foil.models import Clause

    global _tabling_learn_clause

    key = (tuple(hypotheses), target, tuple(background),
           tuple(masks), tuple(constants),
           tuple((k, v) for s in positives for k, v in s.items()),
           tuple((k, v) for s in negatives for k, v in s.items()))
    if cache and key in _tabling_learn_clause:
        return _tabling_learn_clause[key]

    body = []
    while negatives:
        candidate = find_candidate(hypotheses, target, body, background, masks, constants, positives, negatives, cache)
        if candidate is None:
            break

        print('\t', body, candidate.literal, '%.3f' % candidate.score)
        body.append(candidate.literal)
        positives = candidate.positives
        negatives = candidate.negatives

    print(len(positives), len(negatives))
    hypothesis = Hypothesis(Clause(target, body), positives)

    if not cache:
        return hypothesis

    return _tabling_learn_clause.setdefault(key, hypothesis)
