from unittest import TestCase

from assertpy import assert_that

from foil.models import Clause
from foil.models import Label
from foil.models import Literal
from foil.models import Program
from foil.simplified.problem import common
from foil.simplified.problem import entropy
from foil.simplified.problem import expand2
from foil.simplified.problem import filter2
from foil.simplified.problem import gain
from foil.simplified.problem import is_complement
from foil.simplified.problem import max_gain


class ProblemTest(TestCase):
    target = Literal.parse('path(X,Y)')
    background = [
        Clause.parse('edge(0,1).'), Clause.parse('edge(0,3).'), Clause.parse('edge(1,2).'),
        Clause.parse('edge(3,2).'), Clause.parse('edge(3,4).'), Clause.parse('edge(4,5).'),
        Clause.parse('edge(4,6).'), Clause.parse('edge(6,8).'), Clause.parse('edge(7,6).'),
        Clause.parse('edge(7,8).'),
    ]

    pos_0 = [
        {'X': 0, 'Y': 1}, {'X': 0, 'Y': 2}, {'X': 0, 'Y': 3}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5},
        {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8}, {'X': 1, 'Y': 2}, {'X': 3, 'Y': 2}, {'X': 3, 'Y': 4},
        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 5}, {'X': 4, 'Y': 6},
        {'X': 4, 'Y': 8}, {'X': 6, 'Y': 8}, {'X': 7, 'Y': 6}, {'X': 7, 'Y': 8},
    ]
    neg_0 = [
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

    pos_1 = [
        {'X': 0, 'Y': 2}, {'X': 0, 'Y': 4}, {'X': 0, 'Y': 5}, {'X': 0, 'Y': 6}, {'X': 0, 'Y': 8},
        {'X': 3, 'Y': 5}, {'X': 3, 'Y': 6}, {'X': 3, 'Y': 8}, {'X': 4, 'Y': 8},
    ]
    neg_1 = []

    pos_2 = [
        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 1},
        {'X': 0, 'Y': 4, 'V0': 3}, {'X': 0, 'Y': 5, 'V0': 1}, {'X': 0, 'Y': 5, 'V0': 3},
        {'X': 0, 'Y': 6, 'V0': 1}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 1},
        {'X': 0, 'Y': 8, 'V0': 3}, {'X': 3, 'Y': 5, 'V0': 2}, {'X': 3, 'Y': 5, 'V0': 4},
        {'X': 3, 'Y': 6, 'V0': 2}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 2},
        {'X': 3, 'Y': 8, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 5}, {'X': 4, 'Y': 8, 'V0': 6},
    ]
    neg_2 = [
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

    pos_3 = [
        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 3},
        {'X': 0, 'Y': 5, 'V0': 3}, {'X': 0, 'Y': 6, 'V0': 3}, {'X': 0, 'Y': 8, 'V0': 3},
        {'X': 3, 'Y': 5, 'V0': 4}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 3, 'Y': 8, 'V0': 4},
        {'X': 4, 'Y': 8, 'V0': 6},
    ]
    neg_3 = []

    pos_4 = [
        {'X': 0, 'Y': 2, 'V0': 1}, {'X': 0, 'Y': 2, 'V0': 3}, {'X': 0, 'Y': 4, 'V0': 3},
        {'X': 3, 'Y': 5, 'V0': 4}, {'X': 3, 'Y': 6, 'V0': 4}, {'X': 4, 'Y': 8, 'V0': 6},
    ]
    neg_4 = []

    def test__max_gain(self):
        for i, entry in enumerate([
            (self.pos_0, self.pos_1, 10.629120763666352),
            (self.pos_1, self.pos_2, 14.264662506490406),
            (self.pos_2, self.pos_3, 11.47373857107525),
            (self.pos_2, self.pos_4, 7.470674987019189),
        ]):
            positives, positives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = max_gain(positives, positives_i)

                assert_that(result, 'max_gain').is_equal_to(expected)

    def test__gain(self):
        for i, entry in enumerate([
            (self.pos_0, self.neg_0, self.pos_1, self.neg_1, 18.827302404982337),
            (self.pos_1, self.neg_0, self.pos_2, self.neg_2, 8.818399062613263),
            (self.pos_2, self.neg_2, self.pos_3, self.neg_3, 20.000000000014428),
            (self.pos_2, self.neg_2, self.pos_4, self.neg_4, 12.000000000008658),
        ]):
            positives, negatives, positives_i, negatives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = gain(positives, negatives, positives_i, negatives_i)

                assert_that(result, 'gain').is_equal_to(expected)

    def test__common(self):
        for i, entry in enumerate([
            (self.pos_0, self.pos_1, 9),
            (self.pos_1, self.pos_2, 9),
            (self.pos_2, self.pos_3, 10),
            (self.pos_2, self.pos_4, 6),
        ]):
            positives, positives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = common(positives, positives_i)

                assert_that(result, 'common').is_equal_to(expected)

    def test__entropy(self):
        for i, entry in enumerate([
            (self.pos_0, self.neg_0, 2.091922489441039),
            (self.pos_1, self.neg_0, 2.9798221180623696),
            (self.pos_1, self.neg_1, 0.0),
            (self.pos_2, self.neg_2, 2.0),
            (self.pos_3, self.neg_3, 0.0),
            (self.pos_4, self.neg_4, 0.0),
        ]):
            positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = entropy(positives, negatives)

                assert_that(result, 'entropy').is_equal_to(expected)

    def test__expand(self):
        for i, entry in enumerate([
            (self.pos_0, [], self.target, [], Literal.parse('edge(X,Y)'), Label.POSITIVE, self.pos_1),
            (self.neg_0, [], self.target, [], Literal.parse('edge(X,Y)'), Label.NEGATIVE, self.neg_1),

            (self.pos_1, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [], Literal.parse('edge(X,V0)'),
             Label.POSITIVE, self.pos_2),
            (self.neg_0, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [], Literal.parse('edge(X,V0)'),
             Label.NEGATIVE, self.neg_2),

            (self.pos_2, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [Literal.parse('edge(X,V0)'), ],
             Literal.parse('path(V0,Y)'), Label.POSITIVE, self.pos_3),
            (self.neg_2, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [Literal.parse('edge(X,V0)'), ],
             Literal.parse('path(V0,Y)'), Label.NEGATIVE, self.neg_3),

            (self.pos_2, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [Literal.parse('edge(X,V0)'), ],
             Literal.parse('path(V0,Y)'), Label.POSITIVE, self.pos_4),
            (self.neg_2, [Clause.parse('path(X,Y) :- edge(X,Y).')], self.target, [Literal.parse('edge(X,V0)'), ],
             Literal.parse('edge(V0,Y)'), Label.NEGATIVE, self.neg_4),
        ]):
            positives, hypotheses, target, body, literal, label, expected = entry
            world = Program([*hypotheses, Clause(target, [*body, literal]), *self.background]).ground()
            with self.subTest(i=i, value=entry):
                result = expand2(positives, literal)
                result = filter2(result, literal, world, label)

                if not expected:
                    assert_that(result, 'expand %d %s' % (len(result), is_complement(result, expected, positives))).is_empty()
                else:
                    assert_that(result, 'expand %d %s' % (len(result), is_complement(result, expected, positives))).contains_only(*expected)
