from foil.models import Example
from foil.models import Label
from foil.models import Literal
from foil.models import Problem
from foil.models import Program

if __name__ == '__main__':
    problem = Problem(
        Program.parse('edge(0,1). edge(0,3). edge(1,2). edge(3,2). edge(3,4). '
                      'edge(4,5). edge(4,6). edge(6,8). edge(7,6). edge(7,8).'),
        Literal.parse('path(X,Y)'),
        [
            Example({'X': 0, 'Y': 1}, Label.POSITIVE),
            Example({'X': 0, 'Y': 2}, Label.POSITIVE),
            Example({'X': 0, 'Y': 3}, Label.POSITIVE),
            Example({'X': 0, 'Y': 4}, Label.POSITIVE),
            Example({'X': 0, 'Y': 5}, Label.POSITIVE),
            Example({'X': 0, 'Y': 6}, Label.POSITIVE),
            Example({'X': 0, 'Y': 8}, Label.POSITIVE),
            Example({'X': 1, 'Y': 2}, Label.POSITIVE),
            Example({'X': 3, 'Y': 2}, Label.POSITIVE),
            Example({'X': 3, 'Y': 4}, Label.POSITIVE),
            Example({'X': 3, 'Y': 5}, Label.POSITIVE),
            Example({'X': 3, 'Y': 6}, Label.POSITIVE),
            Example({'X': 3, 'Y': 8}, Label.POSITIVE),
            Example({'X': 4, 'Y': 5}, Label.POSITIVE),
            Example({'X': 4, 'Y': 6}, Label.POSITIVE),
            Example({'X': 4, 'Y': 8}, Label.POSITIVE),
            Example({'X': 6, 'Y': 8}, Label.POSITIVE),
            Example({'X': 7, 'Y': 6}, Label.POSITIVE),
            Example({'X': 7, 'Y': 8}, Label.POSITIVE),
        ],
    )
    print(problem)
    print()

    hypotheses = problem.learn()
    for hypothesis in hypotheses:
        print(hypothesis)
    print()

    print('Done.')
