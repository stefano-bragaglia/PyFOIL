from unittest import TestCase

from assertpy import assert_that


class RootTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([]):
            root, fact, expected = entry
            with self.subTest(i=i, value=entry):
                result = root.notify(fact)

                assert_that(result, 'Root.notify').is_equal_to(expected)


class AlphaTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([]):
            alpha, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = alpha.notify(fact, subst, parent)

                assert_that(result, 'Alpha.notify').is_equal_to(expected)


class BetaTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([]):
            beta, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = beta.notify(fact, subst, parent)

                assert_that(result, 'Beta.notify').is_equal_to(expected)


class LeafTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([]):
            leaf, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = leaf.notify(fact, subst, parent)

                assert_that(result, 'Leaf.notify').is_equal_to(expected)


class EngineTest(TestCase):

    def test__load(self):
        for i, entry in enumerate([]):
            engine, clause, expected = entry
            with self.subTest(i=i, value=entry):
                result = engine.load(clause)

                assert_that(result, 'Engine.load').is_equal_to(expected)

    def test__insert(self):
        for i, entry in enumerate([]):
            engine, fact, expected = entry
            with self.subTest(i=i, value=entry):
                result = engine.insert(fact)

                assert_that(result, 'Engine.insert').is_equal_to(expected)
