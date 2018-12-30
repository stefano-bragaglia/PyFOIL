from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from foil.models import Clause
from foil.models import Literal
from foil.unification import is_variable
from foil.unification import Substitution


class Assignment:
    def __init__(self, substitution: Substitution, positive: bool):
        self._substitution = substitution
        self._positive = positive

    def __repr__(self) -> str:
        return '(%s) {%s}' % (
            ['-', '+'][self._positive],
            ', '.join('%s: %s' % (k, repr(v)) for k, v in sorted(self._substitution.items())),
        )

    @property
    def substitution(self) -> Substitution:
        return self._substitution

    @property
    def positive(self) -> bool:
        return self._positive

    def extend(self, literal: Literal, ground: List[Literal]) -> List['Assignment']:
        literal = literal.substitute(self._substitution)
        if not literal:
            return []

        table = {}
        for fact in ground:
            substitution = literal.unify(fact)
            if substitution:
                for variable, constant in substitution.items():
                    table.setdefault(variable, set()).add(constant)

        result = [self]
        for variable, constants in table.items():
            result = [Assignment({**s._substitution, variable: c}, self._positive) for c in constants for s in result]

        return result

    def satisfy(self, literal: Literal, ground: List[Literal]) -> bool:
        literal = literal.substitute(self._substitution)
        if not literal:
            return False

        return any(bool(literal.unify(fact)) for fact in ground)


class Example:
    def __init__(self, fact: Literal, positive: bool):
        if not fact.is_ground():
            raise ValueError('Examples should be ground: %s' % repr(fact))

        self._fact = fact
        self._positive = positive

    def __hash__(self) -> int:
        return hash(self._fact) * hash(self._positive)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._positive != other._positive:
            return False

        return self._fact == other._fact

    def __repr__(self) -> str:
        return '(%s) %s' % (['-', '+'][self._positive], repr(self._fact))

    @property
    def fact(self) -> Literal:
        return self._fact

    @property
    def positive(self) -> bool:
        return self._positive

    def get_assignment(self, target: Literal) -> Optional[Assignment]:
        substitution = target.unify(self._fact)
        if not substitution:
            return None

        return Assignment(substitution, self._positive)


class TrainingSet:
    def __init__(self, assignments: List[Assignment]):
        self._assignments = assignments

    def __repr__(self) -> str:
        return '\n'.join(repr(a) for a in self._assignments)

    @property
    def assignments(self) -> Iterable[Assignment]:
        return self._assignments

    def extend(self, literal: Literal, ground: List[Literal]) -> Tuple[int, List[Assignment]]:
        count, result = 0, []
        for assignment in self._assignments:
            if assignment.satisfy(literal, ground):
                count += 1
                for extension in assignment.extend(literal, ground):
                    if extension not in result:
                        result.append(extension)

        return count, result

    # def foil(self, target: Literal, examples: List[Example]) -> List[Clause]:
    #     training_set = TrainingSet([e.get_assignment(target) for e in examples])
    #
    #     ground = self.get_world()
    #
    #     clauses = []
    #     while any(e.positive for e in training_set.assignments):
    #         clause = self.new_clause(target, training_set)
    #         if not clause:
    #             raise ValueError("Shouldn't have happened")
    #
    #         clauses.append(clause)
    #         training_set = TrainingSet([a for a in training_set.assignments if not a.satisfy(target, ground)])
    #
    #     return clauses
    #
    # def new_clause(self, target: Literal, training_set: TrainingSet) -> Clause:
    #     body, current_set = [], training_set
    #     while any(not e.positive for e in current_set.assignments):
    #         candidates = self.new_literals(target, body)
    #         literal, extended_examples = self.choose_literal(candidates, current_set)
    #         if literal:
    #             body = (*body, literal)
    #             current_set = extended_examples
    #
    #     return Clause(target, body)
    #
    # def choose_literal(self, literals: List[Literal], training_set: TrainingSet) -> Tuple[Literal, List[Example]]:
    #     best, literal, extended_examples = None, None, training_set
    #     for literal in literals:
    #         max_gain = cover(extended_examples, literal) * information(extended_examples)
    #         if best is not None and max_gain < best:
    #             continue
    #
    #         # future_examples = []
    #         # for example in extended_examples:
    #         #     for e in example.extend(literal, self.get_constants()):
    #         #         if e not in future_examples:
    #         #             future_examples.append(e)
    #
    #         future_examples = [ee for e in extended_examples for ee in e.extend(literal, self.get_constants())]
    #         gain = cover(examples, literal) * (information(examples) - information(future_examples))
    #         if best is None or gain > best:
    #             best, literal, extended_examples = gain, literal, future_examples
    #
    #     return literal, extended_examples
    #
    # def new_literals(self, head: Literal, body: List[Literal]) -> List[Literal]:
    #     literals = []
    #     count = self._count(head, body)
    #     for negated, functor, arity in self._get_signatures():
    #         for indexes in self._get_indexes(count, arity):
    #             literal = Literal(Atom(functor, tuple('V%d' % i for i in indexes)), negated)
    #             if literal not in literals:
    #                 literals.append(literal)
    #
    #     return literals
    #
    # def extend(self, example: Example, literal: Literal) -> List[Example]:
    #     raise NotImplementedError

    # def extend(self, literal: Literal, ground: List[Literal]) -> Tuple[int, List[Assignment]]:
    #     count, result = 0, []
    #     for assignment in self._assignments:
    #         if assignment.satisfy(literal, ground):
    #             count += 1
    #             for extension in assignment.extend(literal, ground):
    #                 if extension not in result:
    #                     result.append(extension)
    #
    #     return count, result


# def _get_signatures(self) -> List[Tuple[bool, str, int]]:
#     signatures = []
#     for clause in self._clauses:
#         signature = (clause.head.negated, clause.head.functor, clause.head.get_arity())
#         if signature not in signatures:
#             signatures.append(signature)
#
#     return signatures


def _count(head: Literal, body: List[Literal]) -> int:
    indexes = {}
    for literal in [*body, head]:
        for term in literal.terms:
            if is_variable(term):
                indexes.setdefault(term, len(indexes))

    return len(indexes)


def _get_indexes(count: int, arity: int) -> List[List[int]]:
    items = [[]]
    for _ in range(arity):
        updates = []
        for combination in items:
            for current in range(count + arity - 1):
                update = [*combination, current]
                updates.append(update)
        items = updates
    valid_items = [p for p in items if any(i < count for i in p)]

    return sorted(valid_items, key=lambda x: sum(1 for i in x if i < count))


if __name__ == '__main__':
    print(_get_indexes(2, 2))