from foil.models import Literal
from foil.models import Program

if __name__ == '__main__':
    relation = Literal.parse('res(X,Y,c)')
    print(relation)
    print()

    program = Program.parse('pred(X) :- func(X). pred(X,Y) :- pred(X), func(Y).')
    print(program)
    print()



