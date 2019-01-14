import math
from itertools import permutations
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from foil.learning import Candidate
from foil.learning import Hypothesis
from foil.models import Assignment
from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Program
from foil.unification import is_variable
from foil.unification import Value


def foil(target: Literal, background: List[Clause], examples: List[Example]) -> List[Clause]:
    constants = get_constants(background, target)
    positives, negatives = get_assignments(background, constants, examples)

    hypotheses = []
    while positives:
        hypothesis = find_clause(hypotheses, target, background, constants, positives, negatives)
        if hypothesis is None:
            break

        positives = update_examples(positives, hypothesis.positives)
        hypotheses.append(hypothesis.clause)

    return hypotheses


def get_constants(background: List[Clause], target: Literal) -> List[Value]:
    # TODO to be implemented
    return [0, 1, 2, 3, 4, 5, 6, 7, 8]


def get_assignments(
        background: List[Clause], constants: List[Value], examples: List[Example],
) -> Tuple[List[Assignment], List[Assignment]]:
    # TODO to be implemented
    return [
               {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
               {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
               {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
               {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
           ], [
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


def update_examples(examples, examples_i):
    """Add to the kb those examples what are represented in extended_examples
    List of omitted examples is returned."""
    return [e for e in examples if not is_covered(e, examples_i)]


def find_clause(
        hypotheses: List[Clause], target: Literal, background: List[Clause],
        constants: List[Value], positives: List[Assignment], negatives: List[Assignment],
) -> Optional[Hypothesis]:
    body = []
    positives, negatives = [*positives], [*negatives]
    while negatives:
        literals = get_literals(target, body)
        candidate = find_literal(hypotheses, target, body, background, constants, positives, negatives)
        if candidate is None:
            break

        positives = update_examples(positives, candidate.pos)
        negatives = update_examples(negatives, candidate.neg)
        body.append(candidate.literal)

    if not body:
        return None

    return Hypothesis(Clause(target, body), positives)


def get_literals(target: Literal, body: List[Literal]) -> List[Literal]:
    # TODO to be implemented
    return [
        Literal.parse('edge(X,V0)'),
        Literal.parse('edge(V0,Y)'),
        Literal.parse('edge(V0,X)'),
        Literal.parse('edge(Y,V0)'),
        Literal.parse('edge(Y,X)'),
        Literal.parse('edge(X,Y)'),
        Literal.parse('edge(X,X)'),
        Literal.parse('edge(Y,Y)'),
        Literal.parse('path(X,V0)'),
        Literal.parse('path(V0,Y)'),
        Literal.parse('path(V0,X)'),
        Literal.parse('path(Y,V0)'),
        Literal.parse('path(Y,X)'),
        Literal.parse('path(X,Y)'),
        Literal.parse('path(X,X)'),
        Literal.parse('path(Y,Y)'),
    ]


def find_literal(
        hypotheses: List[Clause], target: Literal, body: List[Literal], background: List[Clause],
        constants: List[Value], positives: List[Assignment], negatives: List[Assignment],
) -> Optional[Candidate]:
    candidate = None
    for literal in get_literals(target, body):
        program = Program([*hypotheses, Clause(target, [*body, literal]), *background])

        positives_i = [e for p in positives for e in extend_example(p, literal, program, constants)]
        negatives_i = [e for n in negatives for e in extend_example(n, literal, program, constants)]

        score = gain(positives, negatives, positives_i, negatives_i)

        if candidate is None or score > candidate.score:
            candidate = Candidate(score, literal, positives_i, negatives_i)

    return candidate


def gain(
        pos: List[Assignment], neg: List[Assignment], pos_i: List[Assignment], neg_i: List[Assignment],
) -> float:
    """
    Find the utility of each literal when added to the body of the clause.
    Utility function is:
        gain(R, l) = T * (log_2 (pos_ii / (pos_ii + neg_ii)) - log_2 (pos_i / (pos_i + neg_i)))

    where:

        pos_i = number of positive bindings of rule R (=current set of rules)
        neg_i = number of negative bindings of rule R
        pos_ii = number of positive bindings of rule R' (= R U {l} )
        neg_ii = number of negative bindings of rule R'
        T = number of positive bindings of rule R that are still covered
            after adding literal l

    """
    if not pos and not neg or not pos_i and not neg_i:
        return -1

    t = sum(1 for p in pos if is_covered(p, pos_i))
    e = math.log2(len(pos) / (len(pos) + len(neg)))
    e_i = math.log2(len(pos_i) / (len(pos_i) + len(neg_i)) + 1e-12)

    return t * (e_i - e)


def is_covered(example: Assignment, examples_i: Iterable[Assignment]) -> bool:
    return any(is_included(example, example_i) for example_i in examples_i)


def is_included(example: Assignment, example_i: Assignment) -> bool:
    return all(item in example_i.items() for item in example.items())


def extend_example(
        example: Assignment, literal: Literal,

        program: Program, constants: List[Value],
) -> List[Assignment]:
    """Generate extended examples which satisfy the literal."""
    extension = []
    variables = {v for v in literal.terms if is_variable(v) and v not in example}
    completions = {p for p in permutations(constants * len(variables), len(variables))}
    for completion in completions:
        assignment = {**example, **dict(zip(variables, completion))}
        candidate = literal.substitute(assignment)
        if program.resolve(candidate) and assignment not in extension:
            extension.append(assignment)

    return extension


if __name__ == '__main__':
    for hypothesis in foil(
            Literal.parse('path(X,Y)'),
            [
                Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                Clause.parse('edge(7,8).'),
            ],
            [Example(a) for a in [
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
            ]]
    ):
        print(hypothesis)
