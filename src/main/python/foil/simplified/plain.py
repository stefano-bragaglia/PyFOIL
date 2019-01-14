from itertools import zip_longest

from foil.models import Clause
from foil.models import Example
from foil.models import Label
from foil.models import Literal
from foil.models import Program
from foil.simplified.problem import expand2
from foil.simplified.problem import filter2

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


def grouper(iterable, n, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


if __name__ == '__main__':
    hypotheses = []
    body = []
    literal = Literal.parse('edge(X,Y)')

    for clause in [*hypotheses, Clause(target, [*body, literal])]:
        print(clause)
    for group in grouper(sorted(repr(c) for c in background), 5, ''):
        print('\t'.join(group))
    print()

    world = Program([*hypotheses, Clause(target, [*body, literal]), *background]).ground()
    sources = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.POSITIVE)) for a in pos_0), 3, '            ')]
    expands = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.POSITIVE)) for a in expand2(pos_0, literal)), 3, '            ')]
    filters = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.POSITIVE)) for a in filter2(expand2(pos_0, literal), literal, world, Label.POSITIVE)), 3, '            ')]
    targets = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.POSITIVE)) for a in pos_1), 3, '            ')]
    while len(expands) < len(sources):
        expands.append('')
    while len(filters) < len(sources):
        filters.append('')
    while len(targets) < len(sources):
        targets.append('')
    for i in range(len(sources)):
        print('\t|\t'.join([sources[i], expands[i], filters[i], targets[i]]))
    print()

    sources = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.NEGATIVE)) for a in neg_0), 3, '            ')]
    expands = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.NEGATIVE)) for a in expand2(neg_0, literal)), 3, '            ')]
    filters = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.NEGATIVE)) for a in filter2(expand2(neg_0, literal), literal, world, Label.POSITIVE)), 3, '            ')]
    targets = ['\t'.join(g) for g in grouper(sorted(repr(Example(a, Label.NEGATIVE)) for a in neg_1), 3, '            ')]
    while len(expands) < len(sources):
        expands.append('')
    while len(filters) < len(sources):
        filters.append('')
    while len(targets) < len(sources):
        targets.append('')
    for i in range(len(sources)):
        print('\t|\t'.join([sources[i], expands[i], filters[i], targets[i]]))
    print()

    pass
