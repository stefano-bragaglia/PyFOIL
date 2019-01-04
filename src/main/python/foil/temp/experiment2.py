from foil.models import Clause
from foil.models import Literal

from foil.temp.learning import learn_hypotheses

if __name__ == '__main__':
    target = Literal.parse('path(X,Y)')
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
    positives = [
        {'X': 0, 'Y': 1},
        {'X': 0, 'Y': 2},
        {'X': 0, 'Y': 3},
        {'X': 0, 'Y': 4},
        {'X': 0, 'Y': 5},
        {'X': 0, 'Y': 6},
        {'X': 0, 'Y': 8},
        {'X': 1, 'Y': 2},
        {'X': 3, 'Y': 2},
        {'X': 3, 'Y': 4},
        {'X': 3, 'Y': 5},
        {'X': 3, 'Y': 6},
        {'X': 3, 'Y': 8},
        {'X': 4, 'Y': 5},
        {'X': 4, 'Y': 6},
        {'X': 4, 'Y': 8},
        {'X': 6, 'Y': 8},
        {'X': 7, 'Y': 6},
        {'X': 7, 'Y': 8},
    ]
    negatives = [{'X': x, 'Y': y} for x in range(9) for y in range(9) if {'X': x, 'Y': y} not in positives]

    for hypothesis in learn_hypotheses(target, background, positives, negatives):
        print(hypothesis)
