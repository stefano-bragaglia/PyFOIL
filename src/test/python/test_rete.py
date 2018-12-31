from unittest import TestCase

from assertpy import assert_that

from foil.models import Clause
from foil.models import Literal
from foil.rete import Alpha
from foil.rete import Beta
from foil.rete import Engine
from foil.rete import Leaf
from foil.rete import Root


class RootTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([
            (Root(), Literal.parse('fact(0).'), None),
        ]):
            root, fact, expected = entry
            with self.subTest(i=i, value=entry):
                result = root.notify(fact)

                assert_that(result, 'Root.notify').is_equal_to(expected)


class AlphaTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([
            (Alpha(Literal.parse('fact(X)'), Root()), Literal.parse('fact(0).'), {}, Root(), None),
        ]):
            alpha, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = alpha.notify(fact, subst, parent)

                assert_that(result, 'Alpha.notify').is_equal_to(expected)


class BetaTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([
            (Beta(Alpha(Literal.parse('fact(X)'), Root()), Alpha(Literal.parse('fact(X)'), Root())),
             [Literal.parse('fact(0).')], {}, Alpha(Literal.parse('fact(X)'), Root()), None),
        ]):
            beta, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = beta.notify(fact, subst, parent)

                assert_that(result, 'Beta.notify').is_equal_to(expected)


class LeafTest(TestCase):

    def test__notify(self):
        for i, entry in enumerate([
            (Leaf(Clause.parse('fact(X).'), Alpha(Literal.parse('fact(X)'), Root()), Root(), []),
             [Literal.parse('fact(0).')], {}, Alpha(Literal.parse('fact(X)'), Root()), None),
        ]):
            leaf, fact, subst, parent, expected = entry
            with self.subTest(i=i, value=entry):
                result = leaf.notify(fact, subst, parent)

                assert_that(result, 'Leaf.notify').is_equal_to(expected)


class EngineTest(TestCase):

    def test__load(self):
        for i, entry in enumerate([
            (Engine(), Clause.parse('fact(X) :- fact(0).'), None),
        ]):
            engine, clause, expected = entry
            with self.subTest(i=i, value=entry):
                result = engine.load(clause)

                assert_that(result, 'Engine.load').is_equal_to(expected)

    def test__insert(self):
        for i, entry in enumerate([
            (Engine(), Clause.parse('fact(0).'), None),
        ]):
            engine, fact, expected = entry
            with self.subTest(i=i, value=entry):
                result = engine.insert(fact)

                assert_that(result, 'Engine.insert').is_equal_to(expected)
