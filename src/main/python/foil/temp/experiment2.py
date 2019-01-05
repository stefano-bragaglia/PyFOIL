from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Program

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
    examples = [Example(a) for a in [
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
    ]]

    # for hypothesis in learn_hypotheses(target, background, examples):
    #     print(hypothesis)

    for literal in Program([
        Clause.parse('path(X,Y) :- edge(X,V0).'),
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
    ]).ground():
        print(literal)
