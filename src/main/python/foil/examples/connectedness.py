from foil.models import Program

source = """
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
"""

if __name__ == '__main__':
    program = Program.parse(source)
    print(program)
    print()

    # examples = []
    # for x in range(9):
    #     for y in range(9):
    #         fact = Literal.parse('path(%s,%s)' % (x, y))
    #         positive = Clause.parse('edge(%s,%s).' % (x, y)) in program.clauses
    #         examples.append(Example(fact, positive))
    # target = Literal.parse('path(X,Y)')
    # # result = program.foil(target, examples)
    # # for clause in result:
    # #     print(clause)

    print('Done.')
