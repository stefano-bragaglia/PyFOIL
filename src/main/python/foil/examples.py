from foil.model import Clause
from foil.model import Example
from foil.model import Literal
from foil.model import Program
from foil.model import term_repr


def abstract():
    program = Program.parse("""
        q(X,Y) :- p(Y,X).
        p(1,2).
    """)
    print(program)
    print()
    query = Literal.parse('q(2,1)')
    print('?-', query)
    derivation = program.resolve(query)
    if derivation:
        print('YES')
        for step in derivation:
            clause = program.get_clause(step[0])
            subs = '{%s}' % ', '.join('%s: %s' % (k, term_repr(v)) for k, v in step[2].items())
            print('    ', clause, '  /  ', subs, '  /  ', step[1])
    else:
        print('NO')


def connectedness():
    program = Program.parse("""
        edge(0,1).
        edge(0,3).
        edge(1,2).
        edge(3,2).
        edge(3,4).
        edge(4,5).
        edge(4,6).
        edge(6,8).
        edge(7,6).
        edge(7,8).
    """)
    print(program)
    print()

    examples = []
    for x in range(9):
        for y in range(9):
            fact = Literal.parse('path(%s,%s)' % (x, y))
            positive = Clause.parse('edge(%s,%s).' % (x, y)) in program.clauses
            examples.append(Example(fact, positive))
    target = Literal.parse('path(X,Y)')
    # result = program.foil(target, examples)
    # for clause in result:
    #     print(clause)


def parenthood():
    program = Program.parse("""
        father(frank,abe).
        father(frank,alan).
        father(alan,sean).
        father(sean,jane).
        father(george,bob).
        father(george,tim).
        father(bob,jan).
        father(tim,tom).
        father(tom,thomas).
        father(ian,ann).
        father(thomas,billy).
        mother(rebecca,alan).        
        mother(rebecca,abe).        
        mother(joan,sean).        
        mother(jane,ann).
        mother(jannet,tim).        
        mother(jannet,bob).        
        mother(tammy,tom).        
        mother(tipsy,thomas).        
        mother(debrah,billy).        
        mother(jill,jan).        
        mother(jan,jane).        
    """)
    print(program)
    print()


if __name__ == '__main__':
    parenthood()
    connectedness()
    abstract()
