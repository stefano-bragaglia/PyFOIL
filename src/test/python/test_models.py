from unittest import TestCase

from assertpy import assert_that

from foil.models import Atom
from foil.models import Clause
from foil.models import Literal
from foil.models import Mask


class MaskTest(TestCase):  # TODO
    pass


class AtomTest(TestCase):

    def test__parse(self):
        for i, entry in enumerate([
            ('func', Atom('func')),
            ('func()', Atom('func', [])),
            ('func(term)', Atom('func', ['term'])),
            ('func(term, 5.0)', Atom('func', ['term', 5.0])),
            ('func(term, 5.0, True)', Atom('func', ['term', 5.0, True])),
        ]):
            content, expected = entry
            with self.subTest(i=i, value=entry):
                result = Atom.parse(content)

                assert_that(result, 'Atom.parse(content: str) -> Atom:') \
                    .is_equal_to(expected)

    def test__get_arity(self):
        for i, entry in enumerate([
            (Atom('func'), 0),
            (Atom('func', []), 0),
            (Atom('func', ['term']), 1),
            (Atom('func', ['term', 5.0]), 2),
            (Atom('func', ['term', 5.0, True]), 3),
        ]):
            atom, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.get_arity()

                assert_that(result, 'Atom.get_arity(self) -> int:') \
                    .is_equal_to(expected)

    def test__is_ground(self):
        for i, entry in enumerate([
            (Atom('func'), True),
            (Atom('func', []), True),
            (Atom('func', ['term']), True),
            (Atom('func', ['term', 5.0]), True),
            (Atom('func', ['term', 5.0, True]), True),
            (Atom('func', ['term', 5.0, True, 'Var']), False),
            (Atom('func', ['term', 5.0, True, '_anon']), False),
        ]):
            atom, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.is_ground()

                assert_that(result, 'Atom.is_ground(self) -> bool:') \
                    .is_equal_to(expected)

    def test__unify(self):
        for i, entry in enumerate([
            (Atom('func'), Atom('pred'), None),
            (Atom('func'), Atom('func'), {}),
            (Atom('func', []), Atom('pred', []), None),
            (Atom('func', []), Atom('func', []), {}),
            (Atom('func', ['term', 5.0]), Atom('pred', ['term', 5.0]), None),
            (Atom('func', ['term', 5.0]), Atom('func', ['term', 5.0]), {}),
            (Atom('func', ['term', 5.0]), Atom('pred', ['term', 5.0]), None),
            (Atom('func', ['term', 5.0]), Atom('func', ['term', 5.0]), {}),
            (Atom('func', ['term', 5.0]), Atom('pred', [5.0, 'term']), None),
            (Atom('func', ['term', 5.0]), Atom('func', [5.0, 'term']), None),
            (Atom('func', ['term', 5.0]), Atom('pred', ['term']), None),
            (Atom('func', ['term', 5.0]), Atom('func', ['term']), None),
            (Atom('func', ['term', 5.0]), Atom('pred', [5.0]), None),
            (Atom('func', ['term', 5.0]), Atom('func', [5.0]), None),
            (Atom('func', ['term', 5.0]), Atom('pred', [True]), None),
            (Atom('func', ['term', 5.0]), Atom('func', [True]), None),
            (Atom('func', ['term', 'V1', 'V2']), Atom('pred', ['term', 5.0, True]), None),
            (Atom('func', ['term', 'V1', 'V2']), Atom('func', ['term', 5.0, True]), {'V1': 5.0, 'V2': True}),
            (Atom('func', ['term', 'V1', 'V2']), Atom('func', ['V0', 5.0, True]),
             {'V0': 'term', 'V1': 5.0, 'V2': True}),
            (Atom('func', ['term', 5.0, True]), Atom('func', ['term', 'V1', 'V2']), {'V1': 5.0, 'V2': True}),
            (Atom('func', ['term', 'V1', 'V2']), Atom('func', ['X', 'Y', 'Z']),
             {'X': 'term', 'Y': 'V1', 'Z': 'V2'}),
        ]):
            atom1, atom2, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom1.unify(atom2)

                assert_that(result, 'Atom.unify(self, other: Atom) -> Optional[Substitution]:') \
                    .is_equal_to(expected)

    def test__substitute(self):
        for i, entry in enumerate([
            (Atom.parse('pred'), {}, Atom.parse('pred')),
            (Atom.parse('pred'), {'X': 'a'}, Atom.parse('pred')),
            (Atom.parse('pred'), {'Y': 'X'}, Atom.parse('pred')),
            (Atom.parse('pred(a)'), {}, Atom.parse('pred(a)')),
            (Atom.parse('pred(a)'), {'X': 'a'}, Atom.parse('pred(a)')),
            (Atom.parse('pred(a)'), {'Y': 'X'}, Atom.parse('pred(a)')),
            (Atom.parse('pred(X)'), {}, Atom.parse('pred(X)')),
            (Atom.parse('pred(X)'), {'X': 'a'}, Atom.parse('pred(a)')),
            (Atom.parse('pred(X)'), {'Y': 'X'}, Atom.parse('pred(X)')),
            (Atom.parse('pred(Y)'), {}, Atom.parse('pred(Y)')),
            (Atom.parse('pred(Y)'), {'X': 'a'}, Atom.parse('pred(Y)')),
            (Atom.parse('pred(Y)'), {'Y': 'X'}, Atom.parse('pred(X)')),
            (Atom.parse('pred(X, Y)'), {}, Atom.parse('pred(X, Y)')),
            (Atom.parse('pred(X, Y)'), {'X': 'a'}, Atom.parse('pred(a, Y)')),
            (Atom.parse('pred(X, Y)'), {'Y': 'X'}, Atom.parse('pred(X, X)')),
        ]):
            atom, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.substitute(subst)

                assert_that(result, 'Atom.substitute(self, subst: Substitution) -> Atom:') \
                    .is_equal_to(expected)


class LiteralTest(TestCase):

    def test__parse(self):
        for i, entry in enumerate([
            ('func', Literal(Atom('func'))),
            ('func()', Literal(Atom('func', []))),
            ('func(term)', Literal(Atom('func', ['term']))),
            ('func(term, 5.0)', Literal(Atom('func', ['term', 5.0]))),
            ('func(term, 5.0, True)', Literal(Atom('func', ['term', 5.0, True]))),
            ('func(term, 5.0, True, X)', Literal(Atom('func', ['term', 5.0, True, 'X']))),

            ('~func', Literal(Atom('func'), True)),
            ('~func()', Literal(Atom('func', []), True)),
            ('~func(term)', Literal(Atom('func', ['term']), True)),
            ('~func(term, 5.0)', Literal(Atom('func', ['term', 5.0]), True)),
            ('~func(term, 5.0, True)', Literal(Atom('func', ['term', 5.0, True]), True)),
            ('~func(term, 5.0, True, X)', Literal(Atom('func', ['term', 5.0, True, 'X']), True)),

            ('~~func', Literal(Atom('func'))),
            ('~~func()', Literal(Atom('func', []))),
            ('~~func(term)', Literal(Atom('func', ['term']))),
            ('~~func(term, 5.0)', Literal(Atom('func', ['term', 5.0]))),
            ('~~func(term, 5.0, True)', Literal(Atom('func', ['term', 5.0, True]))),
            ('~~func(term, 5.0, True, X)', Literal(Atom('func', ['term', 5.0, True, 'X']))),

            ('~~~func', Literal(Atom('func'), True)),
            ('~~~func()', Literal(Atom('func', []), True)),
            ('~~~func(term)', Literal(Atom('func', ['term']), True)),
            ('~~~func(term, 5.0)', Literal(Atom('func', ['term', 5.0]), True)),
            ('~~~func(term, 5.0, True)', Literal(Atom('func', ['term', 5.0, True]), True)),
            ('~~~func(term, 5.0, True, X)', Literal(Atom('func', ['term', 5.0, True, 'X']), True)),
        ]):
            content, expected = entry
            with self.subTest(i=i, value=entry):
                result = Literal.parse(content)

                assert_that(result, 'Literal.parse(content: str) -> Literal:') \
                    .is_equal_to(expected)

    def test__get_arity(self):
        for i, entry in enumerate([
            (Literal.parse('func'), 0),
            (Literal.parse('func()'), 0),
            (Literal.parse('func(term)'), 1),
            (Literal.parse('func(term, 5.0)'), 2),
            (Literal.parse('func(term, 5.0, True)'), 3),
            (Literal.parse('~func'), 0),
            (Literal.parse('~func()'), 0),
            (Literal.parse('~func(term)'), 1),
            (Literal.parse('~func(term, 5.0)'), 2),
            (Literal.parse('~func(term, 5.0, True)'), 3),
        ]):
            atom, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.get_arity()

                assert_that(result, 'Literal.get_arity(self) -> int:') \
                    .is_equal_to(expected)

    def test__get_complement(self):
        for i, entry in enumerate([
            (Literal.parse('func'), Literal.parse('~func')),
            (Literal.parse('func()'), Literal.parse('~func()')),
            (Literal.parse('func(term)'), Literal.parse('~func(term)')),
            (Literal.parse('func(term, 5.0)'), Literal.parse('~func(term, 5.0)')),
            (Literal.parse('func(term, 5.0, True)'), Literal.parse('~func(term, 5.0, True)')),
            (Literal.parse('func(term, 5.0, True, X)'), Literal.parse('~func(term, 5.0, True, X)')),

            (Literal.parse('~func'), Literal.parse('func')),
            (Literal.parse('~func()'), Literal.parse('func()')),
            (Literal.parse('~func(term)'), Literal.parse('func(term)')),
            (Literal.parse('~func(term, 5.0)'), Literal.parse('func(term, 5.0)')),
            (Literal.parse('~func(term, 5.0, True)'), Literal.parse('func(term, 5.0, True)')),
            (Literal.parse('~func(term, 5.0, True, X)'), Literal.parse('func(term, 5.0, True, X)')),
        ]):
            literal, expected = entry
            with self.subTest(i=i, value=entry):
                result = literal.get_complement()

                assert_that(result, 'Literal.get_complement(self) -> Literal:') \
                    .is_equal_to(expected)

    def test__get_mask(self):
        for i, entry in enumerate([
            (Literal.parse('func'), Mask(False, 'func', 0)),
            (Literal.parse('func()'), Mask(False, 'func', 0)),
            (Literal.parse('func(term)'), Mask(False, 'func', 1)),
            (Literal.parse('func(term, 5.0)'), Mask(False, 'func', 2)),
            (Literal.parse('func(term, 5.0, True)'), Mask(False, 'func', 3)),
            (Literal.parse('func(term, 5.0, True, X)'), Mask(False, 'func', 4)),

            (Literal.parse('~func'), Mask(True, 'func', 0)),
            (Literal.parse('~func()'), Mask(True, 'func', 0)),
            (Literal.parse('~func(term)'), Mask(True, 'func', 1)),
            (Literal.parse('~func(term, 5.0)'), Mask(True, 'func', 2)),
            (Literal.parse('~func(term, 5.0, True)'), Mask(True, 'func', 3)),
            (Literal.parse('~func(term, 5.0, True, X)'), Mask(True, 'func', 4)),
        ]):
            literal, expected = entry
            with self.subTest(i=i, value=entry):
                result = literal.get_mask()

                assert_that(result, 'Literal.get_mask(self) -> Mask:') \
                    .is_equal_to(expected)

    def test__is_ground(self):
        for i, entry in enumerate([
            (Literal.parse('func'), True),
            (Literal.parse('func()'), True),
            (Literal.parse('func(term)'), True),
            (Literal.parse('func(term, 5.0)'), True),
            (Literal.parse('func(term, 5.0, True)'), True),
            (Literal.parse('func(term, 5.0, True, Var)'), False),
            (Literal.parse('func(term, 5.0, True, _anon)'), False),
            (Literal.parse('~func'), True),
            (Literal.parse('~func()'), True),
            (Literal.parse('~func(term)'), True),
            (Literal.parse('~func(term, 5.0)'), True),
            (Literal.parse('~func(term, 5.0, True)'), True),
            (Literal.parse('~func(term, 5.0, True, Var)'), False),
            (Literal.parse('~func(term, 5.0, True, _anon)'), False),
        ]):
            atom, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.is_ground()

                assert_that(result, 'Literal.is_ground(self) -> bool:') \
                    .is_equal_to(expected)

    def test__unify(self):
        for i, entry in enumerate([
            (Literal.parse('func'),
             Literal.parse('pred'),
             None),
            (Literal.parse('func'),
             Literal.parse('func'),
             {}),
            (Literal.parse('func()'),
             Literal.parse('pred()'),
             None),
            (Literal.parse('func()'),
             Literal.parse('func()'),
             {}),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(term, 5.0)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(term, 5.0)'),
             {}),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(term, 5.0)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(term, 5.0)'),
             {}),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(5.0, term)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(5.0, term)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(term)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(term)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(5.0)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(5.0)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('pred(True)'),
             None),
            (Literal.parse('func(term, 5.0)'),
             Literal.parse('func(True)'),
             None),
            (Literal.parse('func(term, V1, V2)'),
             Literal.parse('pred(term, 5.0, True)'),
             None),
            (Literal.parse('func(term, V1, V2)'),
             Literal.parse('func(term, 5.0, True)'),
             {'V1': 5.0, 'V2': True}),
            (Literal.parse('func(term, V1, V2)'),
             Literal.parse('func(V0, 5.0, True)'),
             {'V0': 'term', 'V1': 5.0, 'V2': True}),
            (Literal.parse('func(term, 5.0, True)'),
             Literal.parse('func(term, V1, V2)'),
             {'V1': 5.0, 'V2': True}),
            (Literal.parse('func(term, V1, V2)'),
             Literal.parse('func(X, Y, Z)'),
             {'X': 'term', 'Y': 'V1', 'Z': 'V2'}),
            (Literal.parse('~func'),
             Literal.parse('~pred'),
             None),
            (Literal.parse('~func'),
             Literal.parse('~func'),
             {}),
            (Literal.parse('~func()'),
             Literal.parse('~pred()'),
             None),
            (Literal.parse('~func()'),
             Literal.parse('~func()'),
             {}),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(term, 5.0)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(term, 5.0)'),
             {}),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(term, 5.0)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(term, 5.0)'),
             {}),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(5.0, term)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(5.0, term)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(term)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(term)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(5.0)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(5.0)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~pred(True)'),
             None),
            (Literal.parse('~func(term, 5.0)'),
             Literal.parse('~func(True)'),
             None),
            (Literal.parse('~func(term, V1, V2])'),
             Literal.parse('~pred(term, 5.0, True)'),
             None),
            (Literal.parse('~func(term, V1, V2)'),
             Literal.parse('~func(term, 5.0, True)'),
             {'V1': 5.0, 'V2': True}),
            (Literal.parse('~func(term, V1, V2)'),
             Literal.parse('~func(V0, 5.0, True)'),
             {'V0': 'term', 'V1': 5.0, 'V2': True}),
            (Literal.parse('~func(term, 5.0, True)'),
             Literal.parse('~func(term, V1, V2)'),
             {'V1': 5.0, 'V2': True}),
            (Literal.parse('~func(term, V1, V2)'),
             Literal.parse('~func(X, Y, Z)'),
             {'X': 'term', 'Y': 'V1', 'Z': 'V2'}),
        ]):
            atom1, atom2, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom1.unify(atom2)

                assert_that(result, 'Literal.unify(self, other: Literal) -> Optional[Substitution]:') \
                    .is_equal_to(
                    expected)

    def test__substitute(self):
        for i, entry in enumerate([
            (Literal.parse('pred'), {}, Literal.parse('pred')),
            (Literal.parse('pred'), {'X': 'a'}, Literal.parse('pred')),
            (Literal.parse('pred'), {'Y': 'X'}, Literal.parse('pred')),
            (Literal.parse('pred(a)'), {}, Literal.parse('pred(a)')),
            (Literal.parse('pred(a)'), {'X': 'a'}, Literal.parse('pred(a)')),
            (Literal.parse('pred(a)'), {'Y': 'X'}, Literal.parse('pred(a)')),
            (Literal.parse('pred(X)'), {}, Literal.parse('pred(X)')),
            (Literal.parse('pred(X)'), {'X': 'a'}, Literal.parse('pred(a)')),
            (Literal.parse('pred(X)'), {'Y': 'X'}, Literal.parse('pred(X)')),
            (Literal.parse('pred(Y)'), {}, Literal.parse('pred(Y)')),
            (Literal.parse('pred(Y)'), {'X': 'a'}, Literal.parse('pred(Y)')),
            (Literal.parse('pred(Y)'), {'Y': 'X'}, Literal.parse('pred(X)')),
            (Literal.parse('pred(X, Y)'), {}, Literal.parse('pred(X, Y)')),
            (Literal.parse('pred(X, Y)'), {'X': 'a'}, Literal.parse('pred(a, Y)')),
            (Literal.parse('pred(X, Y)'), {'Y': 'X'}, Literal.parse('pred(X, X)')),
            (Literal.parse('~pred'), {}, Literal.parse('~pred')),
            (Literal.parse('~pred'), {'X': 'a'}, Literal.parse('~pred')),
            (Literal.parse('~pred'), {'Y': 'X'}, Literal.parse('~pred')),
            (Literal.parse('~pred(a)'), {}, Literal.parse('~pred(a)')),
            (Literal.parse('~pred(a)'), {'X': 'a'}, Literal.parse('~pred(a)')),
            (Literal.parse('~pred(a)'), {'Y': 'X'}, Literal.parse('~pred(a)')),
            (Literal.parse('~pred(X)'), {}, Literal.parse('~pred(X)')),
            (Literal.parse('~pred(X)'), {'X': 'a'}, Literal.parse('~pred(a)')),
            (Literal.parse('~pred(X)'), {'Y': 'X'}, Literal.parse('~pred(X)')),
            (Literal.parse('~pred(Y)'), {}, Literal.parse('~pred(Y)')),
            (Literal.parse('~pred(Y)'), {'X': 'a'}, Literal.parse('~pred(Y)')),
            (Literal.parse('~pred(Y)'), {'Y': 'X'}, Literal.parse('~pred(X)')),
            (Literal.parse('~pred(X, Y)'), {}, Literal.parse('~pred(X, Y)')),
            (Literal.parse('~pred(X, Y)'), {'X': 'a'}, Literal.parse('~pred(a, Y)')),
            (Literal.parse('~pred(X, Y)'), {'Y': 'X'}, Literal.parse('~pred(X, X)')),
        ]):
            atom, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = atom.substitute(subst)

                assert_that(result, 'Literal.substitute(self, substitution: Substitution) -> Literal:') \
                    .is_equal_to(expected)


class ClauseTest(TestCase):

    def test__parse(self):
        for i, entry in enumerate([
            ('func.', Clause(Literal(Atom('func')))),
            ('func().', Clause(Literal(Atom('func', [])))),
            ('func(Var).', Clause(Literal(Atom('func', ['Var'])))),
            ('func(term).', Clause(Literal(Atom('func', ['term'])))),
            ('func(term, 5.0).', Clause(Literal(Atom('func', ['term', 5.0])))),
            ('func(term, 5.0, True).', Clause(Literal(Atom('func', ['term', 5.0, True])))),

            ('~func.', Clause(Literal(Atom('func'), True))),
            ('~func().', Clause(Literal(Atom('func', []), True))),
            ('~func(Var).', Clause(Literal(Atom('func', ['Var']), True))),
            ('~func(term).', Clause(Literal(Atom('func', ['term']), True))),
            ('~func(term, 5.0).', Clause(Literal(Atom('func', ['term', 5.0]), True))),
            ('~func(term, 5.0, True).', Clause(Literal(Atom('func', ['term', 5.0, True]), True))),

            ('func :- pred.', Clause(Literal(Atom('func')), [Literal(Atom('pred'))])),
            ('func() :- pred.', Clause(Literal(Atom('func', [])), [Literal(Atom('pred'))])),
            ('func(Var) :- pred.', Clause(Literal(Atom('func', ['Var'])), [Literal(Atom('pred'))])),
            ('func(term) :- pred.', Clause(Literal(Atom('func', ['term'])), [Literal(Atom('pred'))])),
            ('func(term, 5.0) :- pred.', Clause(Literal(Atom('func', ['term', 5.0])), [Literal(Atom('pred'))])),
            ('func(term, 5.0, True) :- pred.',
             Clause(Literal(Atom('func', ['term', 5.0, True])), [Literal(Atom('pred'))])),

            ('~func :- pred.', Clause(Literal(Atom('func'), True), [Literal(Atom('pred'))])),
            ('~func() :- pred.', Clause(Literal(Atom('func', []), True), [Literal(Atom('pred'))])),
            ('~func(Var) :- pred.', Clause(Literal(Atom('func', ['Var']), True), [Literal(Atom('pred'))])),
            ('~func(term) :- pred.', Clause(Literal(Atom('func', ['term']), True), [Literal(Atom('pred'))])),
            ('~func(term, 5.0) :- pred.', Clause(Literal(Atom('func', ['term', 5.0]), True), [Literal(Atom('pred'))])),
            ('~func(term, 5.0, True) :- pred.',
             Clause(Literal(Atom('func', ['term', 5.0, True]), True), [Literal(Atom('pred'))])),
        ]):
            content, expected = entry
            with self.subTest(i=i, value=entry):
                result = Clause.parse(content)

                assert_that(result, 'Clause.parse(content: str) -> Clause:') \
                    .is_equal_to(expected)

    def test__get_arity(self):
        for i, entry in enumerate([
            (Clause.parse('func.'), 0),
            (Clause.parse('func().'), 0),
            (Clause.parse('func(Var).'), 0),
            (Clause.parse('func(term).'), 0),
            (Clause.parse('func(term, 5.0).'), 0),
            (Clause.parse('func(term, 5.0, True).'), 0),
            (Clause.parse('~func.'), 0),
            (Clause.parse('~func().'), 0),
            (Clause.parse('~func(Var).'), 0),
            (Clause.parse('~func(term).'), 0),
            (Clause.parse('~func(term, 5.0).'), 0),
            (Clause.parse('~func(term, 5.0, True).'), 0),

            (Clause.parse('func :- pred.'), 1),
            (Clause.parse('func() :- pred.'), 1),
            (Clause.parse('func(Var) :- pred.'), 1),
            (Clause.parse('func(term) :- pred.'), 1),
            (Clause.parse('func(term, 5.0) :- pred.'), 1),
            (Clause.parse('func(term, 5.0, True) :- pred.'), 1),
            (Clause.parse('~func :- pred.'), 1),
            (Clause.parse('~func() :- pred.'), 1),
            (Clause.parse('~func(Var) :- pred.'), 1),
            (Clause.parse('~func(term) :- pred.'), 1),
            (Clause.parse('~func(term, 5.0) :- pred.'), 1),
            (Clause.parse('~func(term, 5.0, True) :- pred.'), 1),

            (Clause.parse('func :- ~pred.'), 1),
            (Clause.parse('func() :- ~pred.'), 1),
            (Clause.parse('func(Var) :- ~pred.'), 1),
            (Clause.parse('func(term) :- ~pred.'), 1),
            (Clause.parse('func(term, 5.0) :- ~pred.'), 1),
            (Clause.parse('func(term, 5.0, True) :- ~pred.'), 1),
            (Clause.parse('~func :- ~pred.'), 1),
            (Clause.parse('~func() :- ~pred.'), 1),
            (Clause.parse('~func(Var) :- ~pred.'), 1),
            (Clause.parse('~func(term) :- ~pred.'), 1),
            (Clause.parse('~func(term, 5.0) :- ~pred.'), 1),
            (Clause.parse('~func(term, 5.0, True) :- ~pred.'), 1),
        ]):
            clause, expected = entry
            with self.subTest(i=i, value=entry):
                result = clause.get_arity()

                assert_that(result, 'Clause.get_arity(self) -> int:') \
                    .is_equal_to(expected)

    def test__is_fact(self):
        for i, entry in enumerate([
            (Clause.parse('func.'), True),
            (Clause.parse('func().'), True),
            (Clause.parse('func(Var).'), False),
            (Clause.parse('func(term).'), True),
            (Clause.parse('func(term, 5.0).'), True),
            (Clause.parse('func(term, 5.0, True).'), True),
            (Clause.parse('~func.'), True),
            (Clause.parse('~func().'), True),
            (Clause.parse('~func(Var).'), False),
            (Clause.parse('~func(term).'), True),
            (Clause.parse('~func(term, 5.0).'), True),
            (Clause.parse('~func(term, 5.0, True).'), True),

            (Clause.parse('func :- pred.'), False),
            (Clause.parse('func() :- pred.'), False),
            (Clause.parse('func(Var) :- pred.'), False),
            (Clause.parse('func(term) :- pred.'), False),
            (Clause.parse('func(term, 5.0) :- pred.'), False),
            (Clause.parse('func(term, 5.0, False) :- pred.'), False),
            (Clause.parse('~func :- pred.'), False),
            (Clause.parse('~func() :- pred.'), False),
            (Clause.parse('~func(Var) :- pred.'), False),
            (Clause.parse('~func(term) :- pred.'), False),
            (Clause.parse('~func(term, 5.0) :- pred.'), False),
            (Clause.parse('~func(term, 5.0, False) :- pred.'), False),

            (Clause.parse('func :- ~pred.'), False),
            (Clause.parse('func() :- ~pred.'), False),
            (Clause.parse('func(Var) :- ~pred.'), False),
            (Clause.parse('func(term) :- ~pred.'), False),
            (Clause.parse('func(term, 5.0) :- ~pred.'), False),
            (Clause.parse('func(term, 5.0, False) :- ~pred.'), False),
            (Clause.parse('~func :- ~pred.'), False),
            (Clause.parse('~func() :- ~pred.'), False),
            (Clause.parse('~func(Var) :- ~pred.'), False),
            (Clause.parse('~func(term) :- ~pred.'), False),
            (Clause.parse('~func(term, 5.0) :- ~pred.'), False),
            (Clause.parse('~func(term, 5.0, False) :- ~pred.'), False),
        ]):
            clause, expected = entry
            with self.subTest(i=i, value=entry):
                result = clause.is_fact()

                assert_that(result, 'Clause.is_fact(self) -> bool:') \
                    .is_equal_to(expected)

    def test__is_ground(self):
        for i, entry in enumerate([
            (Clause.parse('func.'), True),
            (Clause.parse('func().'), True),
            (Clause.parse('func(Var).'), False),
            (Clause.parse('func(term).'), True),
            (Clause.parse('func(term, 5.0).'), True),
            (Clause.parse('func(term, 5.0, True).'), True),
            (Clause.parse('~func.'), True),
            (Clause.parse('~func().'), True),
            (Clause.parse('~func(Var).'), False),
            (Clause.parse('~func(term).'), True),
            (Clause.parse('~func(term, 5.0).'), True),
            (Clause.parse('~func(term, 5.0, True).'), True),

            (Clause.parse('func :- pred.'), True),
            (Clause.parse('func() :- pred.'), True),
            (Clause.parse('func(Var) :- pred.'), False),
            (Clause.parse('func(term) :- pred.'), True),
            (Clause.parse('func(term, 5.0) :- pred.'), True),
            (Clause.parse('func(term, 5.0, True) :- pred.'), True),
            (Clause.parse('~func :- pred.'), True),
            (Clause.parse('~func() :- pred.'), True),
            (Clause.parse('~func(Var) :- pred.'), False),
            (Clause.parse('~func(term) :- pred.'), True),
            (Clause.parse('~func(term, 5.0) :- pred.'), True),
            (Clause.parse('~func(term, 5.0, True) :- pred.'), True),

            (Clause.parse('func :- ~pred.'), True),
            (Clause.parse('func() :- ~pred.'), True),
            (Clause.parse('func(Var) :- ~pred.'), False),
            (Clause.parse('func(term) :- ~pred.'), True),
            (Clause.parse('func(term, 5.0) :- ~pred.'), True),
            (Clause.parse('func(term, 5.0, True) :- ~pred.'), True),
            (Clause.parse('~func :- ~pred.'), True),
            (Clause.parse('~func() :- ~pred.'), True),
            (Clause.parse('~func(Var) :- ~pred.'), False),
            (Clause.parse('~func(term) :- ~pred.'), True),
            (Clause.parse('~func(term, 5.0) :- ~pred.'), True),
            (Clause.parse('~func(term, 5.0, True) :- ~pred.'), True),
        ]):
            clause, expected = entry
            with self.subTest(i=i, value=entry):
                result = clause.is_ground()

                assert_that(result, 'Clause.is_ground(self) -> bool:') \
                    .is_equal_to(expected)

    def test__substitute(self):
        for i, entry in enumerate([
            (Literal.parse('pred.'), {}, Literal.parse('pred.')),
            (Literal.parse('pred.'), {'X': 'a'}, Literal.parse('pred.')),
            (Literal.parse('pred.'), {'Y': 'X'}, Literal.parse('pred.')),

            (Literal.parse('pred(a).'), {}, Literal.parse('pred(a).')),
            (Literal.parse('pred(a).'), {'X': 'a'}, Literal.parse('pred(a).')),
            (Literal.parse('pred(a).'), {'Y': 'X'}, Literal.parse('pred(a).')),

            (Literal.parse('pred(X).'), {}, Literal.parse('pred(X).')),
            (Literal.parse('pred(X).'), {'X': 'a'}, Literal.parse('pred(a).')),
            (Literal.parse('pred(X).'), {'Y': 'X'}, Literal.parse('pred(X).')),

            (Literal.parse('pred(Y).'), {}, Literal.parse('pred(Y).')),
            (Literal.parse('pred(Y).'), {'X': 'a'}, Literal.parse('pred(Y).')),
            (Literal.parse('pred(Y).'), {'Y': 'X'}, Literal.parse('pred(X).')),

            (Literal.parse('pred(X, Y).'), {}, Literal.parse('pred(X, Y).')),
            (Literal.parse('pred(X, Y).'), {'X': 'a'}, Literal.parse('pred(a, Y).')),
            (Literal.parse('pred(X, Y).'), {'Y': 'X'}, Literal.parse('pred(X, X).')),

            (Literal.parse('~pred.'), {}, Literal.parse('~pred.')),
            (Literal.parse('~pred.'), {'X': 'a'}, Literal.parse('~pred.')),
            (Literal.parse('~pred.'), {'Y': 'X'}, Literal.parse('~pred.')),

            (Literal.parse('~pred(a).'), {}, Literal.parse('~pred(a).')),
            (Literal.parse('~pred(a).'), {'X': 'a'}, Literal.parse('~pred(a).')),
            (Literal.parse('~pred(a).'), {'Y': 'X'}, Literal.parse('~pred(a).')),

            (Literal.parse('~pred(X).'), {}, Literal.parse('~pred(X).')),
            (Literal.parse('~pred(X).'), {'X': 'a'}, Literal.parse('~pred(a).')),
            (Literal.parse('~pred(X).'), {'Y': 'X'}, Literal.parse('~pred(X).')),

            (Literal.parse('~pred(Y).'), {}, Literal.parse('~pred(Y).')),
            (Literal.parse('~pred(Y).'), {'X': 'a'}, Literal.parse('~pred(Y).')),
            (Literal.parse('~pred(Y).'), {'Y': 'X'}, Literal.parse('~pred(X).')),

            (Literal.parse('~pred(X, Y).'), {}, Literal.parse('~pred(X, Y).')),
            (Literal.parse('~pred(X, Y).'), {'X': 'a'}, Literal.parse('~pred(a, Y).')),
            (Literal.parse('~pred(X, Y).'), {'Y': 'X'}, Literal.parse('~pred(X, X).')),

        ]):
            clause, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = clause.substitute(subst)

                assert_that(result, 'Clause.substitute(self, substitution: Substitution) -> Clause:') \
                    .is_equal_to(expected)


class ProgramTest(TestCase):

    def test__parse(self):  # TODO
        pass

    def test__get_clause(self):  # TODO
        pass

    def test__get_facts(self):  # TODO
        pass

    def test__get_rules(self):  # TODO
        pass

    def test__is_empty(self):  # TODO
        pass

    def test__is_ground(self):  # TODO
        pass

    def test__resolve(self):  # TODO
        pass

    def test__ground(self):  # TODO
        pass


class LabelTest(TestCase):  # TODO
    pass


class ExampleTest(TestCase):

    def test__parse(self):  # TODO
        pass

    def test__get_clause(self):  # TODO
        pass


class ProblemTest(TestCase):

    def test__parse(self):  # TODO
        pass

    def test__get_clause(self):  # TODO
        pass

    def test__get_facts(self):  # TODO
        pass

    def test__get_rules(self):  # TODO
        pass

    def test__is_empty(self):  # TODO
        pass

    def test__is_ground(self):  # TODO
        pass

    def test__complete(self):  # TODO
        pass

    def test__resolve(self):  # TODO
        pass

    def test__ground(self):  # TODO
        pass

    def test__get_masks(self):  # TODO
        pass
