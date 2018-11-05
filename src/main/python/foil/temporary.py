# target relation is a predicate
# predicate include (in theory) different variables only
# no reason why it shouldn't contain constant (to be ignored) or repeated variables (to be unified)

# training sets (or examples) it's a set of tuples
# each tuple is an assignment of values to the variables in the given predicate (a substitution?)
# each example is labelled as (+) or (-) (depending if they are in the predicate above or not)
# (+) are those with the relation. Possible sources for (-) are:
#    * they are part of the problem (<0,2> must not be in any world?)
#    * closed-world (everything not (+), deduced as (-) -- all the tuple among the possible not given as (+)
#    * the values of tuple can be typed (to reduce the search space when generating the (-) list above)

"""
At the outermost level, the operation of FOIL can be summarized as:
• Establish the training set consisting of constant tuples, some labelled (+) and some (-).

• Until there are no (+) tuples left in the training set:
- Find a clause that characterizes part of the the target relation.
- Remove all tuples that satisfy the right-hand side of this clause from the training set.
"""

from typing import Any
from typing import List

Clause = Any
TrainingSet = Any


def get_training_set(some_input) -> TrainingSet:
    pass


def learn(input: TrainingSet) -> List[Clause]:
    clauses = []


    pass
