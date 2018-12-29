from unittest import TestCase

from assertpy import assert_that

from foil.unification import assign
from foil.unification import equate
from foil.unification import is_ground
from foil.unification import is_variable
from foil.unification import normalize
from foil.unification import simplify
from foil.unification import unify


class UnificationTest(TestCase):

    def test__is_ground(self):
        for i, entry in enumerate([
            (None, False),
            (True, True),
            (False, True),
            (0, True),
            (5, True),
            (-5, True),
            (0.0, True),
            (3.14, True),
            (-3.14, True),
            (0.1E-10, True),
            (-0.1E10, True),
            ('"lower"', True),
            ('"Title"', True),
            ('"UPPER"', True),
            ('"_anon"', True),
            ('lower', True),
            ('Title', False),
            ('UPPER', False),
            ('_anon', False),
        ]):
            term, expected = entry
            with self.subTest(i=i, value=entry):
                result = is_ground(term)

                assert_that(result, 'is_ground').is_equal_to(expected)

    def test__is_variable(self):
        for i, entry in enumerate([
            (None, False),
            (True, False),
            (False, False),
            (0, False),
            (5, False),
            (-5, False),
            (0.0, False),
            (3.14, False),
            (-3.14, False),
            (0.1E-10, False),
            (-0.1E10, False),
            ('"lower"', False),
            ('"Title"', False),
            ('"UPPER"', False),
            ('"_anon"', False),
            ('lower', False),
            ('Title', True),
            ('UPPER', True),
            ('_anon', True),
        ]):
            term, expected = entry
            with self.subTest(i=i, value=entry):
                result = is_variable(term)

                assert_that(result, 'is_variable').is_equal_to(expected)

    def test__normalize(self):
        for i, entry in enumerate([
            (True, 'True'),
            (False, 'False'),
            (0, '0'),
            (5, '5'),
            (-5, '-5'),
            (0.0, '0.0'),
            (3.14, '3.14'),
            (-3.14, '-3.14'),
            (0.1E-10, '1e-11'),
            (-0.1E10, '-1000000000.0'),
            ('"lower"', '"lower"'),
            ('"Title"', '"Title"'),
            ('"UPPER"', '"UPPER"'),
            ('"_anon"', '"_anon"'),
            ('lower', 'lower'),
            ('Title', 'Title'),
            ('UPPER', 'UPPER'),
            ('_anon', '_anon'),
        ]):
            term, expected = entry
            with self.subTest(i=i, value=entry):
                result = normalize(term)

                assert_that(result, description='normalize').is_equal_to(expected)

    def test_unify(self):
        for i, entry in enumerate([
            ('X', 'a', {},
             {'X': 'a'}),
            ('X', 'a', {'X': 'b'},
             None),
            ('X', 'a', {'X': 'a'},
             {'X': 'a'}),
            ('X', 'a', {'X': 'XY', 'Y': 'XY'},
             {'X': 'a', 'Y': 'a'}),
            ('X', 'a', {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'},
             {'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ('X', 'Y', {},
             {'X': 'XY', 'Y': 'XY'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XY', 'Y': 'XY'}),
            ('X', 'Y', {'X': 'a'},
             {'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'Y': 'b'},
             {'X': 'b', 'Y': 'b'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'b'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b'}),
            ('X', 'Y', {'X': 'a', 'Y': 'a'},
             {'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'X': 'a', 'Y': 'b'},
             None),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'b'},
             None),
            ('X', 'Y', {'X': 'XZ', 'Z': 'XZ'},
             {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Z': 'XZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ('X', 'Y', {'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ('X', 'Y', {'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'}),
        ]):
            var, term, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = unify(var, term, subst)

                assert_that(result, description='unify').is_equal_to(expected)

    def test__assign(self):
        for i, entry in enumerate([
            ('X', 'a', {}, {'X': 'a'}),
            ('X', 'a', {'X': 'b'}, None),
            ('X', 'a', {'X': 'a'}, {'X': 'a'}),
            ('X', 'a', {'X': 'XY', 'Y': 'XY'}, {'X': 'a', 'Y': 'a'}),
            ('X', 'a', {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}, {'X': 'a', 'Y': 'a', 'Z': 'a'}),
        ]):
            var, term, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = assign(var, term, subst)

                assert_that(result, 'assign').is_equal_to(expected)

    def test__equate(self):
        for i, entry in enumerate([
            ('X', 'Y', {},
             {'X': 'XY', 'Y': 'XY'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XY', 'Y': 'XY'}),
            ('X', 'Y', {'X': 'a'},
             {'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'Y': 'b'},
             {'X': 'b', 'Y': 'b'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'b'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b'}),
            ('X', 'Y', {'X': 'a', 'Y': 'a'},
             {'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'}),
            ('X', 'Y', {'X': 'a', 'Y': 'b'},
             None),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'b'},
             None),
            ('X', 'Y', {'X': 'XZ', 'Z': 'XZ'},
             {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Z': 'XZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'}),
            ('X', 'Y', {'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ('X', 'Y', {'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ('X', 'Y', {'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'}),
            ('X', 'Y', {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'}),
        ]):
            var1, var2, subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = equate(var1, var2, subst)

                assert_that(result, 'equate').is_equal_to(expected)

    def test__simplify(self):
        for i, entry in enumerate([
            ({},
             {}),
            ({'X': 'a'},
             {'X': 'a'}),
            ({'Y': 'b'},
             {'Y': 'b'}),
            ({'X': 'XY', 'Y': 'XY'},
             {'Y': 'X'}),
            ({'X': 'XZ', 'Z': 'XZ'},
             {'Z': 'X'}),
            ({'Y': 'YZ', 'Z': 'YZ'},
             {'Z': 'Y'}),
            ({'X': 'a', 'Y': 'a'},
             {'X': 'a', 'Y': 'a'}),
            ({'X': 'a', 'Y': 'b'},
             {'X': 'a', 'Y': 'b'}),
            ({'X': 'b', 'Y': 'b'},
             {'X': 'b', 'Y': 'b'}),
            ({'X': 'a', 'Y': 'a', 'Z': 'a'},
             {'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ({'X': 'b', 'Y': 'b', 'Z': 'b'},
             {'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c'},
             {'J': 'I', 'K': 'c'}),
            ({'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'a', 'Z': 'Y'}),
            ({'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'Y': 'b', 'Z': 'X'}),
            ({'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'},
             {'Y': 'X', 'Z': 'X'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a'},
             {'J': 'I', 'K': 'c', 'X': 'a'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'b'},
             {'J': 'I', 'K': 'c', 'Y': 'b'}),
            ({'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'X': 'W', 'Z': 'Y'}),
            ({'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'},
             {'X': 'W', 'Y': 'W', 'Z': 'W'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a'},
             {'J': 'I', 'K': 'c', 'X': 'a', 'Y': 'a'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b'},
             {'J': 'I', 'K': 'c', 'X': 'b', 'Y': 'b'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'b'},
             {'J': 'I', 'K': 'c', 'X': 'a', 'Y': 'b'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XY', 'Y': 'XY'},
             {'J': 'I', 'K': 'c', 'Y': 'X'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Z': 'XZ'},
             {'J': 'I', 'K': 'c', 'Z': 'X'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'Y': 'YZ', 'Z': 'YZ'},
             {'J': 'I', 'K': 'c', 'Z': 'Y'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'a', 'Z': 'a'},
             {'J': 'I', 'K': 'c', 'X': 'a', 'Y': 'a', 'Z': 'a'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'b', 'Y': 'b', 'Z': 'b'},
             {'J': 'I', 'K': 'c', 'X': 'b', 'Y': 'b', 'Z': 'b'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'a', 'Y': 'YZ', 'Z': 'YZ'},
             {'J': 'I', 'K': 'c', 'X': 'a', 'Z': 'Y'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XZ', 'Y': 'b', 'Z': 'XZ'},
             {'J': 'I', 'K': 'c', 'Y': 'b', 'Z': 'X'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'X': 'XYZ', 'Y': 'XYZ', 'Z': 'XYZ'},
             {'J': 'I', 'K': 'c', 'Y': 'X', 'Z': 'X'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WX', 'X': 'WX', 'Y': 'YZ', 'Z': 'YZ'},
             {'J': 'I', 'K': 'c', 'X': 'W', 'Z': 'Y'}),
            ({'I': 'IJ', 'J': 'IJ', 'K': 'c', 'W': 'WXYZ', 'X': 'WXYZ', 'Y': 'WXYZ', 'Z': 'WXYZ'},
             {'J': 'I', 'K': 'c', 'X': 'W', 'Y': 'W', 'Z': 'W'}),
        ]):
            subst, expected = entry
            with self.subTest(i=i, value=entry):
                result = simplify(subst)

                assert_that(result, 'equate').is_equal_to(expected)
