from itertools import permutations
from typing import List
from unittest import TestCase

from assertpy import assert_that

from foil.models import Assignment
from foil.models import Clause
from foil.models import Literal
from foil.models import Program
from foil.unification import is_variable
from foil.unification import Value


def covers(examples: List[Assignment], examples_i: List[Assignment]) -> List[Assignment]:
    reference = [pi.items() for pi in examples_i]

    return [e for e in examples if any(all(item in items for item in e.items()) for items in reference)]


def extend(
        examples: List[Assignment], literal: Literal, constants: List[Value], world: List[Literal],
) -> List[Assignment]:
    if not examples:
        return []

    variables = {v for v in literal.terms if is_variable(v) and v not in examples[0]}
    if not variables:
        return [e for e in examples if literal.substitute(e) in world]

    size = len(variables)
    additions = [dict(zip(variables, v)) for v in set(permutations(constants * size, size))]

    return [{**e, **a} for e in examples for a in additions if literal.substitute({**e, **a}) in world]


class ExtendTest(TestCase):
    target = Literal.parse('path(X,Y)')
    background = [
        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
        Clause.parse('edge(7,8).'),
    ]
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

    hypotheses0 = []
    hypotheses1 = [Clause.parse('path(X,Y) :- edge(X,Y).')]

    edge_x_y = Literal.parse('edge(X,Y)')
    edge_x_v0 = Literal.parse('edge(X,V0)')
    path_v0_y = Literal.parse('path(V0,Y)')
    edge_v0_y = Literal.parse('edge(V0,Y)')

    def test__extend(self):
        for i, entry in enumerate([
            (self.pos_0_0, self.hypotheses0, [], self.edge_x_y, self.pos_0_1),
            (self.neg_0_0, self.hypotheses0, [], self.edge_x_y, self.neg_0_1),
            (self.pos_1_0, self.hypotheses1, [], self.edge_x_v0, self.pos_1_1),
            (self.neg_1_0, self.hypotheses1, [], self.edge_x_v0, self.neg_1_1),
            (self.pos_1_1, self.hypotheses1, [self.edge_x_v0], self.path_v0_y, self.pos_1_2),
            (self.neg_1_1, self.hypotheses1, [self.edge_x_v0], self.path_v0_y, self.neg_1_2),
            (self.pos_1_1, self.hypotheses1, [self.edge_x_v0], self.edge_v0_y, self.pos_1_3),
            (self.neg_1_1, self.hypotheses1, [self.edge_x_v0], self.edge_v0_y, self.neg_1_3),
        ]):
            examples, hypotheses, body, literal, expected = entry
            world = Program([*hypotheses, Clause(self.target, [*body, literal]), *self.background]).ground()
            with self.subTest(i=i, value=entry):
                result = extend(examples, literal, self.constants, world)

                if not expected:
                    assert_that(result, 'extend').is_empty()
                else:
                    assert_that(result, 'extend').contains_only(*expected)

    def test__covers(self):
        for i, entry in enumerate([
            (self.pos_0_0, self.pos_0_1, self.pos_0_1),
            (self.neg_0_0, self.neg_0_1, self.neg_0_1),

        ]):
            examples, examples_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = covers(examples, examples_i)

                if not expected:
                    assert_that(result, 'covers').is_empty()
                else:
                    assert_that(result, 'covers').contains_only(*expected)
