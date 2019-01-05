from unittest import TestCase

from assertpy import assert_that

from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Mask
from foil.tabling import get_constants
from foil.tabling import get_examples
from foil.tabling import get_masks
from foil.tabling import get_variables
from foil.tabling import itemize


class TablingTest(TestCase):

    def test__get_constants(self):
        for i, entry in enumerate([
            (
                    Literal.parse('path(X,Y)'),
                    [
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
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ),
            (
                    Literal.parse('path(X,Y)'),
                    [
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
                    ],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ),
        ]):
            target, background, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_constants(target, background)

                assert_that(
                    result,
                    'get_constants(literals: List[Literal]) -> List[Value]',
                ).is_equal_to(expected)

    def test__get_examples(self):
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
                    ]],
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
                    ]],
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
            world, constants, target, examples, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_examples(world, constants, target, examples)

                assert_that(
                    result,
                    'get_examples(world: List[Literal], constants: List[Value], target: Literal, '
                    'examples: List[Example]) -> Tuple[List[Assignment], List[Assignment]]'
                ).is_equal_to(expected)

    def test__get_masks(self):
        for i, entry in enumerate([
            (
                    Literal.parse('path(X,Y)'),
                    [
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
                    ],
                    [Mask(False, 'edge', 2), Mask(False, 'path', 2)],
            ),
        ]):
            target, background, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_masks(target, background)

                assert_that(
                    result,
                    'get_masks(background: List[Clause], target: Literal) -> List[Mask]',
                ).is_equal_to(expected)

    def test__get_variables(self):
        for i, entry in enumerate([
            (Literal.parse('path(X,Y)'), [], ['X', 'Y']),
            (Literal.parse('path(Y,Z)'), [], ['Y', 'Z']),
            (Literal.parse('path(X,Y,Z,X,Y,Y)'), [], ['X', 'Y', 'Z']),
            (Literal.parse('path(X,Y)'), [Literal.parse('edge(X,V0)'), Literal.parse('path(V0,Y)')], ['X', 'Y', 'V0']),
            (Literal.parse('path(X,Y)'), [], ['X', 'Y']),
            (Literal.parse('path(Y,Z)'), [], ['Y', 'Z']),
            (Literal.parse('path(X,Y,Z,X,Y,Y)'), [], ['X', 'Y', 'Z']),
            (Literal.parse('path(X,Y)'), [Literal.parse('edge(X,V0)'), Literal.parse('path(V0,Y)')], ['X', 'Y', 'V0']),
        ]):
            target, body, expected = entry
            with self.subTest(i=i, value=entry):
                result = get_variables(target, body)

                assert_that(
                    result,
                    'get_variables(literals: List[Literal]) -> List[Variable]',
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