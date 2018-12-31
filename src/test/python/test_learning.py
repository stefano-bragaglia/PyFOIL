from unittest import TestCase

from assertpy import assert_that

from foil.learning import build
from foil.learning import choose
from foil.learning import common
from foil.learning import covers
from foil.learning import entropy
from foil.learning import Expand
from foil.learning import gain
from foil.learning import learn
from foil.learning import max_gain


class ExpandTest(TestCase):

    def test___as_terms(self):
        for i, entry in enumerate([
            # TODO
        ]):
            variables, combination, expected = entry
            with self.subTest(i=i, value=entry):
                result = Expand._as_terms(variables, combination)

                assert_that(
                    result,
                    'Expand._as_terms(variables: Tuple[Variable], combination: Tuple[int, ...]) -> Tuple[Variable]:'
                ).is_equal_to(expected)


class FoilTest(TestCase):

    def test__learn(self):
        for i, entry in enumerate([
            # TODO
        ]):
            background, target, masks, positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = learn(background, target, masks, positives, negatives)

                assert_that(
                    result,
                    'learn(background: List[Clause], '
                    '      target: Literal, masks: List[Mask], '
                    '      positives: List[Example], negatives: List[Example]'
                    ') -> List[Clause]:'
                ).is_equal_to(expected)

    def test__build(self):
        for i, entry in enumerate([
            # TODO
        ]):
            background, hypothesis, target, masks, positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = build(background, hypothesis, target, masks, positives, negatives)

                assert_that(
                    result,
                    'build(background: Iterable[Clause], hypothesis: Iterable[Clause], '
                    '      target: Literal, masks: Iterable[Mask], '
                    '      positives: Iterable[Example], negatives: Iterable[Example]'
                    ') -> Tuple[Clause, Iterable[Example], Iterable[Example]]:'
                ).is_equal_to(expected)

    def test__choose(self):
        for i, entry in enumerate([
            # TODO
        ]):
            background, hypothesis, target, body, masks, positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = choose(background, hypothesis, target, body,  masks, positives, negatives)

                assert_that(
                    result,
                    'choose(background: Iterable[Clause], hypothesis: Iterable[Clause], '
                    '       target: Literal, body: Iterable[Literal], masks: Iterable[Mask], '
                    '       positives: Iterable[Example], negatives: Iterable[Example]'
                    ') -> Optional[Tuple[Literal, Iterable[Example], Iterable[Example]]]:'
                ).is_equal_to(expected)

    def test__covers(self):
        for i, entry in enumerate([
            # TODO
        ]):
            background, hypothesis, target, body, examples, expected = entry
            with self.subTest(i=i, value=entry):
                result = covers(background, hypothesis, target, body, examples)

                assert_that(
                    result,
                    'covers(background: Iterable[Clause], hypothesis: Iterable[Clause],'
                    '       target: Literal, body: Iterable[Literal],'
                    '       examples: Iterable[Example]'
                    ') -> Iterable[Example]:'
                ).is_equal_to(expected)

    def test__gain(self):
        for i, entry in enumerate([
            # TODO
        ]):
            positives, negatives, positives_i, negatives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = gain(positives, negatives, positives_i, negatives_i)

                assert_that(
                    result,
                    'gain(positives: Iterable[Example], negatives: Iterable[Example],'
                    '     positives_i: Iterable[Example], negatives_i: Iterable[Example]'
                    ') -> float:'
                ).is_equal_to(expected)

    def test__max_gain(self):
        for i, entry in enumerate([
            # TODO
        ]):
            positives, negatives, positives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = max_gain(positives, negatives, positives_i)

                assert_that(
                    result,
                    'max_gain(positives: Iterable[Example], negatives: Iterable[Example], '
                    '         positives_i: Iterable[Example]'
                    ') -> float:'
                ).is_equal_to(expected)

    def test__common(self):
        for i, entry in enumerate([
            # TODO
        ]):
            positives, positives_i, expected = entry
            with self.subTest(i=i, value=entry):
                result = common(positives, positives_i)

                assert_that(
                    result,
                    'common(positives: Iterable[Example], positives_i: Iterable[Example]) -> int:'
                ).is_equal_to(expected)

    def test__entropy(self):
        for i, entry in enumerate([
            # TODO
        ]):
            positives, negatives, expected = entry
            with self.subTest(i=i, value=entry):
                result = entropy(positives, negatives)

                assert_that(
                    result,
                    'entropy(positives: Iterable[Example], negatives: Iterable[Example]) -> float:'
                ).is_equal_to(expected)
