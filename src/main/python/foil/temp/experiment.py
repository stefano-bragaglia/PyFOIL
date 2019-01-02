from foil.clean import get_masks
from foil.clean import learn_hypotheses
from foil.models import Clause
from foil.models import Literal

background = [
    Clause.parse('edge(0,1).'),
    Clause.parse('edge(0,3).'),
    Clause.parse('edge(1,2).'),
    Clause.parse('edge(3,2).'),
    Clause.parse('edge(3,4).'),
    Clause.parse('edge(4,5).'),
    Clause.parse('edge(4,6).'),
    Clause.parse('edge(6,8).'),
    Clause.parse('edge(7,6).'),
    Clause.parse('edge(7,8).'),
]

target = Literal.parse('path(X,Y)')
positives = [
    Literal.parse('path(0,1)'), Literal.parse('path(0,2)'), Literal.parse('path(0,3)'),
    Literal.parse('path(0,4)'), Literal.parse('path(0,5)'), Literal.parse('path(0,6)'),
    Literal.parse('path(0,8)'), Literal.parse('path(1,2)'), Literal.parse('path(3,2)'),
    Literal.parse('path(3,4)'), Literal.parse('path(3,5)'), Literal.parse('path(3,6)'),
    Literal.parse('path(3,8)'), Literal.parse('path(4,5)'), Literal.parse('path(4,6)'),
    Literal.parse('path(4,8)'), Literal.parse('path(6,8)'), Literal.parse('path(7,6)'),
    Literal.parse('path(7,8)'),
]
negatives = [Literal.parse('path(%s,%s)' % (x, y)) for x in range(9) for y in range(9)
             if Literal.parse('path(%s,%s)' % (x, y)) not in positives]

if __name__ == '__main__':
    print(len(positives), len(negatives))

    masks = get_masks(background, target)

    hypothesis = learn_hypotheses(background, target, masks, positives, negatives)

    for clause in hypothesis:
        print(clause)

    print(len(positives), len(negatives))

    print('Done.')
