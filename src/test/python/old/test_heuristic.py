import math
from unittest import TestCase

from assertpy import assert_that

from foil.old.heuristic import entropy
from foil.old.heuristic import gain
from foil.old.heuristic import max_gain


class HeuristicTest(TestCase):

    def test_max_gain(self):
        for i, entry in enumerate([
            (19, 62, 39.74652729937974),
            (18, 54, 36.0),
            (6, 0, 0.0),
            (6, 6, 6.0),
            (0, 6, 0),
            # (0, 0, math.nan),
        ]):
            pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = max_gain(pos, neg)

                assert_that(result, 'max_gain(pos: int, neg: int) -> float:').is_equal_to(expected)

    def test_gain(self):
        for i, entry in enumerate([
            (18, 54, 10, 0, 20.0),
            (18, 54, 0, 54, 0),
        ]):
            pos, neg, pos_i, neg_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = gain(pos, neg, pos_i, neg_i)

                assert_that(result, 'gain(pos: int, neg: int, pos_i: int, neg_i: int) -> float:').is_equal_to(expected)

    def test__entropy(self):
        for i, entry in enumerate([
            (19, 62, 2.091922489441039),
            (18, 54, 2.0),
            (6, 0, 0.0),
            (6, 6, 1.0),
            (0, 6, math.inf),
            # (0, 0, math.nan),
        ]):
            pos, neg, expected = entry
            with self.subTest(i=i, value=entry):
                result = entropy(pos, neg)

                assert_that(result, 'entropy(pos: int, neg: int) -> float:').is_equal_to(expected)
