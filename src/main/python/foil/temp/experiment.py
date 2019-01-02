from foil.models import Clause
from foil.models import Example
from foil.models import Literal
from foil.models import Problem
from foil.models import Program

if __name__ == '__main__':
    problem = Problem(
        Program([
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
        ]),
        Literal.parse('path(X,Y)'),
        [
            Example({'X': 0, 'Y': 1}),
            Example({'X': 0, 'Y': 2}),
            Example({'X': 0, 'Y': 3}),
            Example({'X': 0, 'Y': 4}),
            Example({'X': 0, 'Y': 5}),
            Example({'X': 0, 'Y': 6}),
            Example({'X': 0, 'Y': 8}),
            Example({'X': 1, 'Y': 2}),
            Example({'X': 3, 'Y': 2}),
            Example({'X': 3, 'Y': 4}),
            Example({'X': 3, 'Y': 5}),
            Example({'X': 3, 'Y': 6}),
            Example({'X': 3, 'Y': 8}),
            Example({'X': 4, 'Y': 5}),
            Example({'X': 4, 'Y': 6}),
            Example({'X': 4, 'Y': 8}),
            Example({'X': 6, 'Y': 8}),
            Example({'X': 7, 'Y': 6}),
            Example({'X': 7, 'Y': 8}),
        ]
    )
    print(problem)
    print()

    hypothesis = problem.learn()
    for clause in hypothesis:
        print(clause)

    print('Done.')
