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

In the inner loop, FOIL seeks a Prolog clause of the form

P(X1, X2, ..., Xk) :- L1, L2, ..., Ln.


that characterizes some subset of the relation P.
The clause is 'grown' by starting with just the left-hand side and adding literals one by one to the right-hand side.
At any stage in its development, the partial clause will contain m distinct bound variables that appear in the left-hand side and unnegated literals of the right-hand side. This inner loop makes use of a local training set consisting of labelled m-tuples of constants; each tuple in this set represents a value assignment to all bound variables in the clause. The inner loop can be sketched as follows:
• Initialize the local training set T~to the training set and let i = 1. • While T,- contains @ tuples:
- Find a literal Li to add to the right-hand side of the clause.
- Produce a new training set T/+1based on those tuples in Ti that satisfy Li. If Li intro-
duces new variables, each such tuple from T/ may give rise to several (expanded) tuples in Ti+1. The label of each tuple in T/+1 is the same as that of the parent tuple in Ti.
- Increment i and continue.



"""

from typing import Any
from typing import List
from typing import Tuple

from temp.model import Value

Clause = Any
TrainingSet = Any


class Assignment:
    def __init__(self, values: Tuple[Value, ...] = (), label: bool = True):
        self._values = values
        self._label = label


def get_training_set(some_input) -> TrainingSet:
    pass


def learn(input: TrainingSet) -> List[Clause]:
    clauses = []

    pass
