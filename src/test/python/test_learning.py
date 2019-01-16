import math
from unittest import TestCase

from assertpy import assert_that

from foil.learning import Candidate
from foil.learning import covers
from foil.learning import entropy
from foil.learning import exclude
from foil.learning import extend
from foil.learning import find_clause
from foil.learning import find_literal
from foil.learning import foil
from foil.learning import gain
from foil.learning import get_closure
from foil.learning import get_constants
from foil.learning import get_masks
from foil.learning import get_signature
from foil.learning import get_table
from foil.learning import Hypothesis
from foil.learning import itemize
from foil.learning import max_gain
from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Mask
from foil.models import Program

hypotheses_0 = []
hypotheses_1 = [Clause.parse('path(X,Y) :- edge(X,Y).')]

target = Literal.parse('path(X,Y)')

body_0 = []
body_1 = [Literal.parse('edge(X,V0)')]

edge_x_y = Literal.parse('edge(X,Y)')
edge_x_v0 = Literal.parse('edge(X,V0)')
path_v0_y = Literal.parse('path(V0,Y)')
edge_v0_y = Literal.parse('edge(V0,Y)')

background = [
    Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
    Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
    Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
    Clause.parse('edge(7,8).'),
]

# literals = [
#     Literal.parse('edge(X,V0)'), Literal.parse('edge(V0,Y)'),
#     Literal.parse('edge(V0,X)'), Literal.parse('edge(Y,V0)'),
#     Literal.parse('edge(Y,X)'), Literal.parse('edge(X,Y)'),
#     Literal.parse('edge(X,X)'), Literal.parse('edge(Y,Y)'),
#     Literal.parse('path(X,V0)'), Literal.parse('path(V0,Y)'),
#     Literal.parse('path(V0,X)'), Literal.parse('path(Y,V0)'),
#     Literal.parse('path(Y,X)'), Literal.parse('path(X,Y)'),
#     Literal.parse('path(X,X)'), Literal.parse('path(Y,Y)'),
# ]
masks = [Mask(False, 'edge', 2), Mask(False, 'path', 2)]
constants = [0, 1, 2, 3, 4, 5, 6, 7, 8]

pos_0_0 = [
    {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
    {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
    {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
    {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
]
pos_0_1 = [
    {'X': 0, 'Y': 1}, {'X': 0, 'Y': 3}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
    {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
]
pos_1_0 = [
    {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
    {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8},
]
pos_1_1 = [
    {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
    {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
    {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
    {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
    {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
    {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6},
]
pos_1_2 = [
    {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 3},
    {'X': 0, 'Y': 5, 'V0': 3}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 3},
    {'X': 3, 'Y': 5, 'V0': 4}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 4},
    {'X': 4, 'Y': 8, 'V0': 6},
]
pos_1_3 = [
    {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 3},
    {'X': 3, 'Y': 5, 'V0': 4}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 6},
]

neg_0_0 = [
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
neg_0_1 = []
neg_1_0 = [*neg_0_0]
neg_1_1 = [
    {'X': 0, 'Y': 0, 'V0': 1}, {'X': 0, 'Y': 0, 'V0': 3}, {'X': 0, 'Y': 7, 'V0': 1},
    {'X': 0, 'Y': 7, 'V0': 3}, {'X': 1, 'Y': 0, 'V0': 2}, {'X': 1, 'Y': 1, 'V0': 2},
    {'X': 1, 'Y': 3, 'V0': 2}, {'X': 1, 'Y': 4, 'V0': 2}, {'X': 1, 'Y': 5, 'V0': 2},
    {'X': 1, 'Y': 6, 'V0': 2}, {'X': 1, 'Y': 7, 'V0': 2}, {'X': 1, 'Y': 8, 'V0': 2},
    {'X': 3, 'Y': 0, 'V0': 2}, {'X': 3, 'Y': 0, 'V0': 4}, {'X': 3, 'Y': 1, 'V0': 2},
    {'X': 3, 'Y': 1, 'V0': 4}, {'X': 3, 'Y': 3, 'V0': 2}, {'X': 3, 'Y': 3, 'V0': 4},
    {'X': 3, 'Y': 7, 'V0': 2}, {'X': 3, 'Y': 7, 'V0': 4}, {'X': 4, 'Y': 0, 'V0': 5},
    {'X': 4, 'Y': 0, 'V0': 6}, {'X': 4, 'Y': 1, 'V0': 5}, {'X': 4, 'Y': 1, 'V0': 6},
    {'X': 4, 'Y': 2, 'V0': 5}, {'X': 4, 'Y': 2, 'V0': 6}, {'X': 4, 'Y': 3, 'V0': 5},
    {'X': 4, 'Y': 3, 'V0': 6}, {'X': 4, 'Y': 4, 'V0': 5}, {'X': 4, 'Y': 4, 'V0': 6},
    {'X': 4, 'Y': 7, 'V0': 5}, {'X': 4, 'Y': 7, 'V0': 6}, {'X': 6, 'Y': 0, 'V0': 8},
    {'X': 6, 'Y': 1, 'V0': 8}, {'X': 6, 'Y': 2, 'V0': 8}, {'X': 6, 'Y': 3, 'V0': 8},
    {'X': 6, 'Y': 4, 'V0': 8}, {'X': 6, 'Y': 5, 'V0': 8}, {'X': 6, 'Y': 6, 'V0': 8},
    {'X': 6, 'Y': 7, 'V0': 8}, {'X': 7, 'Y': 0, 'V0': 8}, {'X': 7, 'Y': 0, 'V0': 6},
    {'X': 7, 'Y': 1, 'V0': 8}, {'X': 7, 'Y': 1, 'V0': 6}, {'X': 7, 'Y': 2, 'V0': 8},
    {'X': 7, 'Y': 2, 'V0': 6}, {'X': 7, 'Y': 3, 'V0': 8}, {'X': 7, 'Y': 3, 'V0': 6},
    {'X': 7, 'Y': 4, 'V0': 8}, {'X': 7, 'Y': 4, 'V0': 6}, {'X': 7, 'Y': 5, 'V0': 8},
    {'X': 7, 'Y': 5, 'V0': 6}, {'X': 7, 'Y': 7, 'V0': 8}, {'X': 7, 'Y': 7, 'V0': 6},
]
neg_1_2 = []
neg_1_3 = []


class LearningTest(TestCase):

    def test__get_closure(self):
        for i, entry in enumerate([
            (background, [
                Example({'X': 0, 'Y': 1}), Example({'X': 0, 'Y': 2}), Example({'X': 0, 'Y': 3}),
                Example({'X': 0, 'Y': 4}), Example({'X': 0, 'Y': 5}), Example({'X': 0, 'Y': 6}),
                Example({'X': 0, 'Y': 8}), Example({'X': 1, 'Y': 2}), Example({'X': 3, 'Y': 2}),
                Example({'X': 3, 'Y': 4}), Example({'X': 3, 'Y': 5}), Example({'X': 3, 'Y': 6}),
                Example({'X': 3, 'Y': 8}), Example({'X': 4, 'Y': 5}), Example({'X': 4, 'Y': 6}),
                Example({'X': 4, 'Y': 8}), Example({'X': 6, 'Y': 8}), Example({'X': 7, 'Y': 6}),
                Example({'X': 7, 'Y': 8}),
            ], (pos_0_0, neg_0_0)),
        ]):
            world, examples, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_closure(target, constants, world, examples)

                assert_that(
                    result,
                    'get_closure(target: Literal, constants: List[Value], world: List[Literal],'
                    ' examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]:',
                ).is_length(2)
                if not expected[0]:
                    assert_that(
                        result[0],
                        'get_closure(target: Literal, constants: List[Value], world: List[Literal],'
                        ' examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]:',
                    ).is_empty()
                else:
                    assert_that(
                        result[0],
                        'get_closure(target: Literal, constants: List[Value], world: List[Literal],'
                        ' examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]:',
                    ).contains_only(*expected[0])
                if not expected[1]:
                    assert_that(
                        result[1],
                        'get_closure(target: Literal, constants: List[Value], world: List[Literal],'
                        ' examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]:',
                    ).is_empty()
                else:
                    assert_that(
                        result[1],
                        'get_closure(target: Literal, constants: List[Value], world: List[Literal],'
                        ' examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]:',
                    ).contains_only(*expected[1])

    def test__get_masks(self):
        for i, entry in enumerate([
            ([target, *[l for c in background for l in c.literals]], [Mask(False, 'path', 2), Mask(False, 'edge', 2)]),
        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_masks(literals)

                assert_that(
                    result,
                    'get_masks(literals: List[Literal]) -> List[Mask]:',
                ).contains_only(*expected)

    def test__get_constants(self):
        for i, entry in enumerate([
            ([target, *[l for c in background for l in c.literals]], [0, 1, 2, 3, 4, 5, 6, 7, 8]),
        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_constants(literals)

                assert_that(
                    result,
                    'get_constants(literals: List[Literal]) -> List[Value]:',
                ).contains_only(*expected)

    def test__foil(self):
        for i, entry in enumerate([
            (pos_0_0, neg_0_0, [
                Clause.parse('path(X,Y) :- edge(X,Y).'),
                Clause.parse('path(X,Y) :- edge(X,V0), path(V0,Y).'),
            ]),
        ]):
            positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = foil(target, background, masks, constants, positives, negatives)

                assert_that(
                    result,
                    'foil(target: Literal, background: List[Clause], positives: List[Assignment],'
                    ' negatives: List[Assignment]) -> List[Clause]:',
                ).is_equal_to(expected)

    def test__exclude(self):
        for i, entry in enumerate([
            (pos_0_0, pos_0_1, pos_1_0),
            (pos_1_0, pos_1_2, []),
        ]):
            examples, examples_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = exclude(examples, examples_i)

                assert_that(
                    result,
                    'exclude(examples: List[Assignment], examples_i: List[Assignment]) -> List[Assignment]:',
                ).is_equal_to(expected)

    def test__find_clause(self):
        for i, entry in enumerate([
            (hypotheses_0, pos_0_0, neg_0_0, Hypothesis(Clause(target, [edge_x_y]), pos_0_1)),
            (hypotheses_1, pos_1_0, neg_1_0, Hypothesis(Clause(target, [edge_x_v0, path_v0_y]), pos_1_2)),
        ]):
            hypotheses, positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = find_clause(hypotheses, target, background, masks, constants, positives, negatives)

                assert_that(
                    result,
                    'find_clause(hypotheses: List[Clause], target: Literal, background: List[Clause], '
                    'literals: List[Literal], constants: List[Value], positives: List[Assignment], '
                    'negatives: List[Assignment]) -> Optional[Hypothesis]:',
                ).is_equal_to(expected)

    def test__find_literal(self):
        for i, entry in enumerate([
            (hypotheses_0, body_0, pos_0_0, neg_0_0, Candidate(20.91922489442482, edge_x_y, pos_0_1, neg_0_1)),
            (hypotheses_1, body_0, pos_1_0, neg_1_0, Candidate(8.818399062613263, edge_x_v0, pos_1_1, neg_1_1)),
            (hypotheses_1, body_1, pos_1_1, neg_1_1, Candidate(20.000000000014428, path_v0_y, pos_1_2, neg_1_2)),
        ]):
            hypotheses, body, positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = find_literal(hypotheses, target, body, background, masks, constants, positives, negatives)

                assert_that(
                    result,
                    'find_literal(hypotheses: List[Clause], target: Literal, body: List[Literal],'
                    ' background: List[Clause], literals: List[Literal], constants: List[Value],'
                    ' positives: List[Assignment], negatives: List[Assignment]) -> Optional[Candidate]:',
                ).is_equal_to(expected)

    def test__max_gain(self):
        for i, entry in enumerate([
            (pos_0_0, neg_0_0, 39.74652729937974),
            (pos_1_0, neg_1_0, 26.818399062561326),
            (pos_1_1, neg_1_1, 36.0),
        ]):
            pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = max_gain(pos, neg)

                assert_that(
                    result,
                    'max_gain(pos: List[Assignment], neg: List[Assignment]) -> float:',
                ).is_equal_to(expected)

    def test__get_table(self):
        for i, entry in enumerate([
            ([target], {0: 'X', 1: 'Y'}),
            ([target, edge_x_y], {0: 'X', 1: 'Y'}),
            ([target, edge_x_v0], {0: 'X', 1: 'Y', 2: 'V0'}),
            ([target, edge_x_v0, path_v0_y], {0: 'X', 1: 'Y', 2: 'V0'}),
            ([target, edge_x_v0, edge_v0_y], {0: 'X', 1: 'Y', 2: 'V0'}),
        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_table(literals)

                assert_that(
                    result,
                    'get_table(literals: List[Literal]) -> Dict[int, Variable]:',
                ).is_equal_to(expected)

    def test__itemize(self):
        for i, entry in enumerate([
            ({0: 'X'}, 1, [['X']]),
            ({0: 'X'}, 2, [['V0', 'X'], ['X', 'V0'], ['X', 'X']]),
            ({0: 'X'}, 3, [
                ['V0', 'V0', 'X'],
                ['V0', 'V1', 'X'],
                ['V0', 'X', 'V0'],
                ['V0', 'X', 'V1'],
                ['V0', 'X', 'X'],
                ['X', 'V0', 'V0'],
                ['X', 'V0', 'V1'],
                ['X', 'V0', 'X'],
                ['X', 'X', 'V0'],
                ['X', 'X', 'X'],
            ]),
            ({0: 'X', 1: 'Y'}, 2, [
                ['V0', 'X'],
                ['V0', 'Y'],
                ['X', 'V0'],
                ['X', 'X'],
                ['X', 'Y'],
                ['Y', 'V0'],
                ['Y', 'X'],
                ['Y', 'Y'],
            ]),
        ]):
            table, arity, expected = entry
            with self.subTest(i=i, value=entry):
                result = itemize(table, arity)

                assert_that(
                    result,
                    'itemize(table: Dict[int, Variable], arity: int) -> List[List[Variable]]:',
                ).contains_only(*expected)

    def test__get_signature(self):
        for i, entry in enumerate([
            ({0: 'X'}, (0, 1, 2), ['X', 'V0', 'V1']),
            ({0: 'X', 1: 'Y'}, (0, 0), ['X', 'X']),
            ({0: 'X', 1: 'Y'}, (0, 1), ['X', 'Y']),
            ({0: 'X', 1: 'Y'}, (0, 2), ['X', 'V0']),
            ({0: 'X', 1: 'Y'}, (1, 0), ['Y', 'X']),
            ({0: 'X', 1: 'Y'}, (1, 1), ['Y', 'Y']),
            ({0: 'X', 1: 'Y'}, (1, 2), ['Y', 'V0']),
            ({0: 'X', 1: 'Y'}, (2, 0), ['V0', 'X']),
            ({0: 'X', 1: 'Y'}, (2, 1), ['V0', 'Y']),
            ({0: 'X', 1: 'Y'}, (2, 2), ['V0', 'V0']),
            ({0: 'X', 1: 'Y'}, (0, 3), ['X', 'V0']),
            ({0: 'X', 1: 'Y'}, (1, 3), ['Y', 'V0']),
            ({0: 'X', 1: 'Y'}, (3, 0), ['V0', 'X']),
            ({0: 'X', 1: 'Y'}, (3, 1), ['V0', 'Y']),
            ({0: 'X', 1: 'Y'}, (3, 3), ['V0', 'V0']),
            ({0: 'X', 1: 'Y'}, (0, 0, 0), ['X', 'X', 'X']),
            ({0: 'X', 1: 'Y'}, (0, 0, 1), ['X', 'X', 'Y']),
            ({0: 'X', 1: 'Y'}, (0, 1, 0), ['X', 'Y', 'X']),
            ({0: 'X', 1: 'Y'}, (0, 1, 1), ['X', 'Y', 'Y']),
            ({0: 'X', 1: 'Y'}, (1, 0, 0), ['Y', 'X', 'X']),
            ({0: 'X', 1: 'Y'}, (1, 0, 1), ['Y', 'X', 'Y']),
            ({0: 'X', 1: 'Y'}, (1, 1, 0), ['Y', 'Y', 'X']),
            ({0: 'X', 1: 'Y'}, (1, 1, 1), ['Y', 'Y', 'Y']),
        ]):
            table, combination, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_signature(table, combination)

                assert_that(
                    result,
                    'get_signature(table: Dict[int, Variable], combination: Tuple[int, ...]) -> List[Variable]:',
                ).is_equal_to(expected)

    def test__extend(self):
        for i, entry in enumerate([
            (pos_0_0, hypotheses_0, [], edge_x_y, pos_0_1),
            (neg_0_0, hypotheses_0, [], edge_x_y, neg_0_1),
            (pos_1_0, hypotheses_1, [], edge_x_v0, pos_1_1),
            (neg_1_0, hypotheses_1, [], edge_x_v0, neg_1_1),
            (pos_1_1, hypotheses_1, [edge_x_v0], path_v0_y, pos_1_2),
            (neg_1_1, hypotheses_1, [edge_x_v0], path_v0_y, neg_1_2),
            (pos_1_1, hypotheses_1, [edge_x_v0], edge_v0_y, pos_1_3),
            (neg_1_1, hypotheses_1, [edge_x_v0], edge_v0_y, neg_1_3),
        ]):
            examples, hypotheses, body, literal, expected = entry
            world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
            with self.subTest(i=i, value=entry):
                result = extend(examples, literal, constants, world)

                if not expected:
                    assert_that(result, 'extend').is_empty()
                else:
                    assert_that(result, 'extend').contains_only(*expected)

    def test__gain(self):
        for i, entry in enumerate([
            (pos_0_0, neg_0_0, pos_0_1, neg_0_1, 20.91922489442482),
            (pos_1_0, neg_1_0, pos_1_1, neg_1_1, 8.818399062613263),
            (pos_1_1, neg_1_1, pos_1_2, neg_1_2, 20.000000000014428),
            (pos_1_1, neg_1_1, pos_1_3, neg_1_3, 12.000000000008658),
        ]):
            pos, neg, pos_i, neg_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = gain(pos, neg, pos_i, neg_i)

                assert_that(
                    result,
                    'gain(pos: List[Assignment], neg: List[Assignment],'
                    ' pos_i: List[Assignment], neg_i: List[Assignment]) -> float:',
                ).is_equal_to(expected)

    def test__entropy(self):
        for i, entry in enumerate([
            (19, 62, 2.091922489441039),
            (18, 54, 2.0),
            (6, 0, 0.0),
            (6, 6, 1.0),
            (0, 6, math.inf),
            (0, 0, math.inf),
        ]):
            pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = entropy(pos, neg)

                assert_that(
                    result,
                    'entropy(pos: int, neg: int) -> float:',
                ).is_equal_to(expected)

    def test__covers(self):
        for i, entry in enumerate([
            (pos_0_0, pos_0_1, pos_0_1),
            (neg_0_0, neg_0_1, neg_0_0),
            (pos_1_0, pos_1_1, pos_1_0),
            (neg_1_0, neg_1_1, [
                {'X': 0, 'Y': 0}, {'X': 0, 'Y': 7}, {'X': 1, 'Y': 0}, {'X': 1, 'Y': 1}, {'X': 1, 'Y': 3},
                {'X': 1, 'Y': 4}, {'X': 1, 'Y': 5}, {'X': 1, 'Y': 6}, {'X': 1, 'Y': 7}, {'X': 1, 'Y': 8},
                {'X': 3, 'Y': 0}, {'X': 3, 'Y': 1}, {'X': 3, 'Y': 3}, {'X': 3, 'Y': 7}, {'X': 4, 'Y': 0},
                {'X': 4, 'Y': 1}, {'X': 4, 'Y': 2}, {'X': 4, 'Y': 3}, {'X': 4, 'Y': 4}, {'X': 4, 'Y': 7},
                {'X': 6, 'Y': 0}, {'X': 6, 'Y': 1}, {'X': 6, 'Y': 2}, {'X': 6, 'Y': 3}, {'X': 6, 'Y': 4},
                {'X': 6, 'Y': 5}, {'X': 6, 'Y': 6}, {'X': 6, 'Y': 7}, {'X': 7, 'Y': 0}, {'X': 7, 'Y': 1},
                {'X': 7, 'Y': 2}, {'X': 7, 'Y': 3}, {'X': 7, 'Y': 4}, {'X': 7, 'Y': 5}, {'X': 7, 'Y': 7}
            ]),
            (pos_1_1, pos_1_2, pos_1_2),
            (neg_1_1, neg_1_2, neg_1_1),
            (pos_1_1, pos_1_3, pos_1_3),
            (neg_1_1, neg_1_3, neg_1_1),

        ]):
            examples, examples_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = covers(examples, examples_i)

                assert_that(
                    result,
                    'covers(examples: List[Assignment], examples_i: List[Assignment]) -> List[Assignment]:',
                ).is_equal_to(expected)
