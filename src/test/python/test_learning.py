import math
from unittest import TestCase

from assertpy import assert_that

from foil.learning import expand
from foil.learning import find_literal
from foil.learning import get_assignments
from foil.learning import get_closure
from foil.learning import get_constants
from foil.learning import get_expansion
from foil.learning import get_free_variables
from foil.learning import get_masks
from foil.learning import get_signature
from foil.learning import get_variables
from foil.learning import itemize
from foil.learning import sort
from foil.heuristic import entropy
from foil.heuristic import gain
from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Mask
from foil.models import Program


class ExplorationTest(TestCase):

    def test__find_literal(self):
        for i, entry in enumerate([
            (
                    [],
                    Literal.parse('path(X,Y)'),
                    [],
                    [
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [Mask(False, 'edge', 2), Mask(False, 'path', 2)],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
                    [
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
                    ],
                    None,
            ),
        ]):
            hypotheses, target, body, background, masks, constants, pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = find_literal(hypotheses, target, body, background, masks, constants, pos, neg)

                assert_that(
                    result,
                    'find_literal(hypotheses: List[Clause], target: Literal, body: List[Literal], '
                    'background: List[Clause], masks: List[Mask], constants: List[Value], '
                    'pos: List[Substitution], neg: List[Substitution]) -> Optional[Candidate]'
                ).is_equal_to(expected)

    def test__get_assignments(self):
        for i, entry in enumerate([
            ([Example(a) for a in [
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
            ]], ([
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
                 ],
                 [],
             )),
        ]):
            examples, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_assignments(examples)

                assert_that(
                    result,
                    'get_assignments(examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]',
                ).is_equal_to(expected)

    def test__get_closure(self):
        for i, entry in enumerate([
            (
                    [
                        Literal.parse('edge(0,1)'),
                        Literal.parse('edge(0,3)'),
                        Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'),
                        Literal.parse('edge(3,4)'),
                        Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'),
                        Literal.parse('edge(6,8)'),
                        Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'),
                    ],
                    [c for c in range(9)],
                    Literal.parse('path(X,Y)'),
                    [
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
                    ],
                    [],
                    (
                            [
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
                            ],
                            [
                                {'X': 0, 'Y': 0},
                                {'X': 0, 'Y': 7},
                                {'X': 1, 'Y': 0},
                                {'X': 1, 'Y': 1},
                                {'X': 1, 'Y': 3},
                                {'X': 1, 'Y': 4},
                                {'X': 1, 'Y': 5},
                                {'X': 1, 'Y': 6},
                                {'X': 1, 'Y': 7},
                                {'X': 1, 'Y': 8},
                                {'X': 2, 'Y': 0},
                                {'X': 2, 'Y': 1},
                                {'X': 2, 'Y': 2},
                                {'X': 2, 'Y': 3},
                                {'X': 2, 'Y': 4},
                                {'X': 2, 'Y': 5},
                                {'X': 2, 'Y': 6},
                                {'X': 2, 'Y': 7},
                                {'X': 2, 'Y': 8},
                                {'X': 3, 'Y': 0},
                                {'X': 3, 'Y': 1},
                                {'X': 3, 'Y': 3},
                                {'X': 3, 'Y': 7},
                                {'X': 4, 'Y': 0},
                                {'X': 4, 'Y': 1},
                                {'X': 4, 'Y': 2},
                                {'X': 4, 'Y': 3},
                                {'X': 4, 'Y': 4},
                                {'X': 4, 'Y': 7},
                                {'X': 5, 'Y': 0},
                                {'X': 5, 'Y': 1},
                                {'X': 5, 'Y': 2},
                                {'X': 5, 'Y': 3},
                                {'X': 5, 'Y': 4},
                                {'X': 5, 'Y': 5},
                                {'X': 5, 'Y': 6},
                                {'X': 5, 'Y': 7},
                                {'X': 5, 'Y': 8},
                                {'X': 6, 'Y': 0},
                                {'X': 6, 'Y': 1},
                                {'X': 6, 'Y': 2},
                                {'X': 6, 'Y': 3},
                                {'X': 6, 'Y': 4},
                                {'X': 6, 'Y': 5},
                                {'X': 6, 'Y': 6},
                                {'X': 6, 'Y': 7},
                                {'X': 7, 'Y': 0},
                                {'X': 7, 'Y': 1},
                                {'X': 7, 'Y': 2},
                                {'X': 7, 'Y': 3},
                                {'X': 7, 'Y': 4},
                                {'X': 7, 'Y': 5},
                                {'X': 7, 'Y': 7},
                                {'X': 8, 'Y': 0},
                                {'X': 8, 'Y': 1},
                                {'X': 8, 'Y': 2},
                                {'X': 8, 'Y': 3},
                                {'X': 8, 'Y': 4},
                                {'X': 8, 'Y': 5},
                                {'X': 8, 'Y': 6},
                                {'X': 8, 'Y': 7},
                                {'X': 8, 'Y': 8},
                            ],
                    )
            ),
        ]):
            world, constants, target, pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_closure(world, constants, target, pos, neg)

                assert_that(
                    result,
                    'get_closure(world: List[Literal], constants: List[Value], target: Literal, '
                    'pos: List[Assignment], neg: List[Assignment]) -> Tuple[List[Assignment], List[Assignment]]',
                ).is_equal_to(expected)

    def test__get_constants(self):
        for i, entry in enumerate([
            (
                    [
                        Literal.parse('path(X,Y)'),
                        Literal.parse('edge(0,1)'),
                        Literal.parse('edge(0,3)'),
                        Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'),
                        Literal.parse('edge(3,4)'),
                        Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'),
                        Literal.parse('edge(6,8)'),
                        Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ),

        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_constants(literals)

                assert_that(
                    result,
                    'get_constants(literals: List[Literal]) -> List[Value]',
                ).is_equal_to(expected)

    def test__get_expansion(self):
        for i, entry in enumerate([
            (
                    Literal.parse('edge(X,Y)'),
                    [
                        Literal.parse('path(0,3)'), Literal.parse('edge(4,6)'), Literal.parse('edge(3,4)'),
                        Literal.parse('path(3,2)'), Literal.parse('path(6,8)'), Literal.parse('edge(6,8)'),
                        Literal.parse('edge(0,1)'), Literal.parse('edge(4,5)'), Literal.parse('path(4,6)'),
                        Literal.parse('path(7,6)'), Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'),
                        Literal.parse('edge(0,3)'), Literal.parse('edge(3,2)'), Literal.parse('edge(7,6)'),
                        Literal.parse('path(1,2)'), Literal.parse('path(3,4)'), Literal.parse('path(4,5)'),
                        Literal.parse('path(7,8)'), Literal.parse('edge(1,2)'),
                    ],
                    set(),
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
            ),
            (
                    Literal.parse('edge(X,V0)'),
                    [
                        Literal.parse('edge(6,8)'), Literal.parse('path(4,Y)'), Literal.parse('edge(4,5)'),
                        Literal.parse('path(1,Y)'), Literal.parse('path(7,Y)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(4,6)'), Literal.parse('path(3,Y)'), Literal.parse('edge(0,1)'),
                        Literal.parse('edge(3,4)'), Literal.parse('path(6,Y)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(7,8)'), Literal.parse('edge(0,3)'),
                        Literal.parse('path(0,Y)'),
                    ],
                    {'V0'},
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8}
                    ],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
                        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
                        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6}
                    ],
            ),
            (
                    Literal.parse('edge(X,V0)'),
                    [
                        Literal.parse('edge(6,8)'), Literal.parse('path(4,Y)'), Literal.parse('edge(4,5)'),
                        Literal.parse('path(1,Y)'), Literal.parse('path(7,Y)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(4,6)'), Literal.parse('path(3,Y)'), Literal.parse('edge(0,1)'),
                        Literal.parse('edge(3,4)'), Literal.parse('path(6,Y)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(7,8)'), Literal.parse('edge(0,3)'),
                        Literal.parse('path(0,Y)'),
                    ],
                    {'V0'},
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
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
                    ],
                    [
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
                    ],
            ),
        ]):
            literal, world, free_variables, constants, substitutions, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_expansion(literal, world, free_variables, constants, substitutions)

                assert_that(
                    result,
                    'get_expansion(literal: Literal, world: List[Literal], constants: List[Value], '
                    'free_variables: Set[Variable], substitutions: List[Substitution]) -> List[Substitution]',
                ).is_equal_to(expected)

    def test__get_free_variables(self):
        for i, entry in enumerate([
            ([Literal.parse('path(X,Y)'), Literal.parse('edge(X,Y)')], {'X': 0, 'Y': 0}, set()),
            ([Literal.parse('path(X,Y)'), Literal.parse('edge(X,V0)')], {'X': 0, 'Y': 0}, {'V0'}),
        ]):
            literals, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_free_variables(literals, subst)

                assert_that(
                    result,
                    'get_free_variables(literals: List[Literal], subst: Substitution) -> Set[Variable]',
                ).is_equal_to(expected)

    def test__get_masks(self):
        for i, entry in enumerate([
            (
                    [
                        Literal.parse('edge(0,1)'),
                        Literal.parse('edge(0,3)'),
                        Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'),
                        Literal.parse('edge(3,4)'),
                        Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'),
                        Literal.parse('edge(6,8)'),
                        Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'),
                        Literal.parse('path(X,Y)'),
                    ],
                    [Mask(False, 'edge', 2), Mask(False, 'path', 2)],
            ),
        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_masks(literals)

                assert_that(
                    result,
                    'get_masks(background: List[Clause], target: Literal) -> List[Mask]',
                ).is_equal_to(expected)

    def test__get_signature(self):
        for i, entry in enumerate([
            (['X'], (0, 1, 2), ['X', 'V0', 'V1']),
            (['X', 'Y'], (0, 0), ['X', 'X']),
            (['X', 'Y'], (0, 1), ['X', 'Y']),
            (['X', 'Y'], (0, 2), ['X', 'V0']),
            (['X', 'Y'], (1, 0), ['Y', 'X']),
            (['X', 'Y'], (1, 1), ['Y', 'Y']),
            (['X', 'Y'], (1, 2), ['Y', 'V0']),
            (['X', 'Y'], (2, 0), ['V0', 'X']),
            (['X', 'Y'], (2, 1), ['V0', 'Y']),
            (['X', 'Y'], (2, 2), ['V0', 'V0']),
            (['X', 'Y'], (0, 3), ['X', 'V0']),
            (['X', 'Y'], (1, 3), ['Y', 'V0']),
            (['X', 'Y'], (3, 0), ['V0', 'X']),
            (['X', 'Y'], (3, 1), ['V0', 'Y']),
            (['X', 'Y'], (3, 3), ['V0', 'V0']),
            (['X', 'Y'], (0, 0, 0), ['X', 'X', 'X']),
            (['X', 'Y'], (0, 0, 1), ['X', 'X', 'Y']),
            (['X', 'Y'], (0, 1, 0), ['X', 'Y', 'X']),
            (['X', 'Y'], (0, 1, 1), ['X', 'Y', 'Y']),
            (['X', 'Y'], (1, 0, 0), ['Y', 'X', 'X']),
            (['X', 'Y'], (1, 0, 1), ['Y', 'X', 'Y']),
            (['X', 'Y'], (1, 1, 0), ['Y', 'Y', 'X']),
            (['X', 'Y'], (1, 1, 1), ['Y', 'Y', 'Y']),
        ]):
            variables, combination, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_signature(variables, combination)

                assert_that(
                    result,
                    'get_signature(variables: List[Variable], combination: Tuple[int, ...]) -> List[Variable]'
                ).is_equal_to(expected)

    def test__get_variables(self):
        for i, entry in enumerate([
            ([Literal.parse('path(X,Y)')], ['X', 'Y']),
            ([Literal.parse('path(Y,Z)')], ['Y', 'Z']),
            ([Literal.parse('path(X,Y,Z,X,Y,Y)')], ['X', 'Y', 'Z']),
            ([Literal.parse('path(X,Y)'), Literal.parse('edge(X,V0)'), Literal.parse('path(V0,Y)')], ['X', 'Y', 'V0']),
        ]):
            literals, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_variables(literals)

                assert_that(
                    result,
                    'get_variables(literals: List[Literal]) -> List[Variable]',
                ).is_equal_to(expected)

    def test__expand(self):
        for i, entry in enumerate([
            (
                    Literal.parse('path(X,Y)'),
                    [],
                    Literal.parse('edge(X,Y)'),
                    [
                        Literal.parse('path(0,3)'), Literal.parse('edge(4,6)'), Literal.parse('edge(3,4)'),
                        Literal.parse('path(3,2)'), Literal.parse('path(6,8)'), Literal.parse('edge(6,8)'),
                        Literal.parse('edge(0,1)'), Literal.parse('edge(4,5)'), Literal.parse('path(4,6)'),
                        Literal.parse('path(7,6)'), Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'),
                        Literal.parse('edge(0,3)'), Literal.parse('edge(3,2)'), Literal.parse('edge(7,6)'),
                        Literal.parse('path(1,2)'), Literal.parse('path(3,4)'), Literal.parse('path(4,5)'),
                        Literal.parse('path(7,8)'), Literal.parse('edge(1,2)'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
                    [
                        {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8}
                    ],
            ),
            (
                    Literal.parse('path(X,Y)'),
                    [],
                    Literal.parse('edge(X,V0)'),
                    [
                        Literal.parse('edge(6,8)'), Literal.parse('path(4,Y)'), Literal.parse('edge(4,5)'),
                        Literal.parse('path(1,Y)'), Literal.parse('path(7,Y)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(4,6)'), Literal.parse('path(3,Y)'), Literal.parse('edge(0,1)'),
                        Literal.parse('edge(3,4)'), Literal.parse('path(6,Y)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(7,8)'), Literal.parse('edge(0,3)'),
                        Literal.parse('path(0,Y)'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8}
                    ],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
                        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
                        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6}
                    ],
            ),
            (
                    Literal.parse('path(X,Y)'),
                    [],
                    Literal.parse('edge(X,V0)'),
                    [
                        Literal.parse('edge(6,8)'), Literal.parse('path(4,Y)'), Literal.parse('edge(4,5)'),
                        Literal.parse('path(1,Y)'), Literal.parse('path(7,Y)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(4,6)'), Literal.parse('path(3,Y)'), Literal.parse('edge(0,1)'),
                        Literal.parse('edge(3,4)'), Literal.parse('path(6,Y)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(7,8)'), Literal.parse('edge(0,3)'),
                        Literal.parse('path(0,Y)'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
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
                    ],
                    [
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
                    ],
            ),
        ]):
            target, body, literal, world, constants, substitutions, expected = entry
            with self.subTest(i=i, value=entry):
                result = expand(target, body, literal, world, constants, substitutions)

                for i, r in enumerate(result):
                    e = expected[i]
                    assert_that(r, '%d) %s == %s' % (i, r, e)).is_equal_to(e)

                assert_that(
                    result,
                    'expand(target: Literal, body: List[Literal], literal: Literal, world: List[Literal], '
                    'constants: List[Value], substitutions: List[Substitution]) -> List[Substitution]',
                ).is_equal_to(expected)

    def test__itemize(self):
        for i, entry in enumerate([
            (['X'], 1, [['X']]),
            (['X'], 2, [['V0', 'X'], ['X', 'V0'], ['X', 'X']]),
            (['X'], 3, [
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
            (['X', 'Y'], 2, [
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
            variables, arity, expected = entry
            with self.subTest(i=i, value=entry):
                result = itemize(variables, arity)

                assert_that(
                    result,
                    'itemize(variables: List[Variable], arity: int) -> List[List[Variable]]',
                ).is_equal_to(expected)

    def test__sort(self):
        for i, entry in enumerate([
            (
                    [{'X': 10, 'Y': 0}, {'X': 5, 'Y': 5}, {'X': 0, 'Y': 10}],
                    [{'X': 0, 'Y': 10}, {'X': 5, 'Y': 5}, {'X': 10, 'Y': 0}],
            ),
        ]):
            assignments, expected = entry
            with self.subTest(i=i, value=entry):
                result = sort(assignments)

                assert_that(
                    result,
                    'sort(assignments: List[Assignment]) -> List[Assignment]',
                ).is_equal_to(expected)

    def test_test(self):
        for i, entry in enumerate([
            (
                    [],
                    Literal.parse('path(X,Y)'),
                    [],
                    Literal.parse('edge(X,Y)'),
                    [
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
                    [
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
                    ],

                    # EXPECTED:
                    [
                        Clause.parse('path(X,Y) :- edge(X,Y).'),
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [
                        Literal.parse('edge(0,1)'), Literal.parse('edge(0,3)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(3,4)'), Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'), Literal.parse('edge(6,8)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'), Literal.parse('path(0,3)'),
                        Literal.parse('path(1,2)'), Literal.parse('path(3,2)'), Literal.parse('path(3,4)'),
                        Literal.parse('path(4,5)'), Literal.parse('path(4,6)'), Literal.parse('path(6,8)'),
                        Literal.parse('path(7,6)'), Literal.parse('path(7,8)'),
                    ],
                    [
                        {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8},
                    ],
                    [
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
                    ],
                    2.9798221180623696,
                    -7.991096657591974,
            ),
            (
                    [Clause.parse('path(X,Y) :- edge(X,Y).')],
                    Literal.parse('path(X,Y)'),
                    [],
                    Literal.parse('edge(X,V0)'),
                    [
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
                        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
                        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
                        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
                    ],
                    [
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
                    ],

                    # EXPECTED:
                    [
                        Clause.parse('path(X,Y) :- edge(X,Y).'),
                        Clause.parse('path(X,Y) :- edge(X,V0).'),
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [
                        Literal.parse('edge(0,1)'), Literal.parse('edge(0,3)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(3,4)'), Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'), Literal.parse('edge(6,8)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'), Literal.parse('path(0,3)'),
                        Literal.parse('path(0,Y)'), Literal.parse('path(1,2)'), Literal.parse('path(1,Y)'),
                        Literal.parse('path(3,2)'), Literal.parse('path(3,4)'), Literal.parse('path(3,Y)'),
                        Literal.parse('path(4,5)'), Literal.parse('path(4,6)'), Literal.parse('path(4,Y)'),
                        Literal.parse('path(6,8)'), Literal.parse('path(6,Y)'), Literal.parse('path(7,6)'),
                        Literal.parse('path(7,8)'), Literal.parse('path(7,Y)'),
                    ],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
                        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
                        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6}
                    ],
                    [
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
                    ],
                    2.0,
                    1.6546048099387036,
            ),
            (
                    [Clause.parse('path(X,Y) :- edge(X,Y).')],
                    Literal.parse('path(X,Y)'),
                    [Literal.parse('edge(X,V0)')],
                    Literal.parse('path(V0,Y)'),
                    [
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
                        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
                        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6}
                    ],
                    [
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
                    ],

                    # EXPECTED:
                    [
                        Clause.parse('path(X,Y) :- edge(X,Y).'),
                        Clause.parse('path(X,Y) :- edge(X,V0), path(V0,Y).'),
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [
                        Literal.parse('edge(0,1)'), Literal.parse('edge(0,3)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(3,4)'), Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'), Literal.parse('edge(6,8)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'), Literal.parse('path(0,2)'),
                        Literal.parse('path(0,3)'), Literal.parse('path(0,4)'), Literal.parse('path(0,5)'),
                        Literal.parse('path(0,6)'), Literal.parse('path(0,8)'), Literal.parse('path(1,2)'),
                        Literal.parse('path(3,2)'), Literal.parse('path(3,4)'), Literal.parse('path(3,5)'),
                        Literal.parse('path(3,6)'), Literal.parse('path(3,8)'), Literal.parse('path(4,5)'),
                        Literal.parse('path(4,6)'), Literal.parse('path(4,8)'), Literal.parse('path(6,8)'),
                        Literal.parse('path(7,6)'), Literal.parse('path(7,8)'),
                    ],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 3},
                        {'X': 0, 'Y': 5, 'V0': 3}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 3},
                        {'X': 3, 'Y': 5, 'V0': 4}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 4},
                        {'X': 4, 'Y': 8, 'V0': 6},
                    ],
                    [
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
                    ],
                    math.inf,
                    0,
            ),
            (
                    [Clause.parse('path(X,Y) :- edge(X,Y).')],
                    Literal.parse('path(X,Y)'),
                    [Literal.parse('edge(X,V0)')],
                    Literal.parse('edge(V0,Y)'),
                    [
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    [
                        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
                        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
                        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6}
                    ],
                    [
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
                    ],

                    # EXPECTED:
                    [
                        Clause.parse('path(X,Y) :- edge(X,Y).'),
                        Clause.parse('path(X,Y) :- edge(X,V0), edge(V0,Y).'),
                        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
                        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
                        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
                        Clause.parse('edge(7,8).'),
                    ],
                    [
                        Literal.parse('edge(0,1)'), Literal.parse('edge(0,3)'), Literal.parse('edge(1,2)'),
                        Literal.parse('edge(3,2)'), Literal.parse('edge(3,4)'), Literal.parse('edge(4,5)'),
                        Literal.parse('edge(4,6)'), Literal.parse('edge(6,8)'), Literal.parse('edge(7,6)'),
                        Literal.parse('edge(7,8)'), Literal.parse('path(0,1)'), Literal.parse('path(0,2)'),
                        Literal.parse('path(0,3)'), Literal.parse('path(0,4)'), Literal.parse('path(1,2)'),
                        Literal.parse('path(3,2)'), Literal.parse('path(3,4)'), Literal.parse('path(3,5)'),
                        Literal.parse('path(3,6)'), Literal.parse('path(4,5)'), Literal.parse('path(4,6)'),
                        Literal.parse('path(4,8)'), Literal.parse('path(6,8)'), Literal.parse('path(7,6)'),
                        Literal.parse('path(7,8)'),
                    ],
                    [
                        {'X': 0, 'Y': 5, 'V0': 1},
                        {'X': 0, 'Y': 5, 'V0': 3},
                        {'X': 0, 'Y': 6, 'V0': 1},
                        {'X': 0, 'Y': 6, 'V0': 3},
                        {'X': 0, 'Y': 8, 'V0': 1},
                        {'X': 0, 'Y': 8, 'V0': 3},
                        {'X': 3, 'Y': 8, 'V0': 2},
                        {'X': 3, 'Y': 8, 'V0': 4},
                    ],
                    [
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
                    ],
                    2.9541963103868754,
                    -7.633570483095003,
            ),
        ]):
            hypotheses, target, body, literal, background, constants, pos, neg, exp_clauses, exp_world, exp_pos_i, exp_neg_i, exp_entropy, emp_score = entry
            with self.subTest(i=i, value=entry):
                clauses = [*hypotheses, Clause(target, [*body, literal]), *background]
                assert_that(clauses, 'clauses').is_equal_to(exp_clauses)

                world = sorted(Program(clauses).ground(), key=lambda x: repr(x))
                assert_that(world, 'world').is_equal_to(exp_world)

                pos_i = expand(target, body, literal, world, constants, pos)
                if not exp_pos_i:
                    assert_that(pos_i, 'pos_i').is_empty()
                else:
                    for i, res in enumerate(pos_i):
                        exp = exp_pos_i[i]
                        assert_that(res, 'pos_i: %d/%d) %s == %s' % (i, len(pos_i), res, exp)).is_equal_to(exp)

                neg_i = expand(target, body, literal, world, constants, neg)
                if not exp_neg_i:
                    assert_that(neg_i, 'neg_i').is_empty()
                else:
                    for i, res in enumerate(neg_i):
                        exp = exp_neg_i[i]
                        assert_that(res, 'neg_i: %d/%d) %s == %s' % (i, len(neg_i), res, exp)).is_equal_to(exp)

                ent = entropy(len(pos_i), len(neg_i))
                assert_that(ent, 'entropy(%d,%d)' % (len(pos_i), len(neg_i))).is_equal_to(exp_entropy)

                score = gain(len(pos), len(neg), len(pos_i), len(neg_i))
                assert_that(score, 'score(%d,%d,%d,%d)' % (len(pos), len(neg), len(pos_i), len(neg_i))) \
                    .is_equal_to(emp_score)
