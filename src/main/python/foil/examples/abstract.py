from foil.models import Literal
from foil.models import Program

source = """
q(X,Y) :- p(Y,X).
p(1,2).
"""

if __name__ == '__main__':
    program = Program.parse(source)
    print(program)
    print()

    query = Literal.parse('q(2,1)')
    print('?-', query)

    derivation = program.resolve(query)
    if derivation:
        print('YES')
        for step in derivation:
            clause = program.get_clause(step.index)
            subst = '{%s}' % ', '.join('%s: %s' % (k, repr(v)) for k, v in step.substitution.items())
            print('    ', clause, '  /  ', subst, '  /  ', step.literal)
    else:
        print('NO')
    print()

    print('Done.')
