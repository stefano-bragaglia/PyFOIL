from foil.models import Program

source = """
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
"""

if __name__ == '__main__':
    program = Program.parse(source)
    print(program)
    print()

    print('Done.')
