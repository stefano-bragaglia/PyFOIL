import copy
from typing import List
from typing import Tuple


class Tabling:
    def __init__(self, f):
        self.f = f
        self.cache = {}

    def __call__(self, *args):
        key = ()
        for arg in args:
            if type(arg) is list:
                values = ()
                for item in arg:
                    val = ()
                    if type(item) is dict:
                        val = (*val, tuple((k, v) for k, v in item.items()))
                    else:
                        val = (*val, item)
                    values = (*values, val)
                key = (*key, values)
                # key = (*key, tuple(arg))
            elif type(arg) is dict:
                key = (*key, tuple((k, v) for k, v in arg.items()))
            else:
                key = (*key, arg)

        return copy.deepcopy(self.cache.setdefault(key, self.f(*args)))
        # return self.cache.setdefault(key, self.f(*args))


@Tabling
def get_constants(target: 'Literal', background: List['Clause']) -> List['Value']:
    from foil.learning import get_constants

    return get_constants([target, *[l for c in background for l in c.literals]])


@Tabling
def get_examples(
        world: List['Literal'],
        constants: List['Value'],
        target: 'Literal',
        examples: List['Example'],
) -> Tuple[List['Assignment'], List['Assignment']]:
    from foil.learning import get_assignments
    from foil.learning import get_closure

    pos, neg = get_assignments(examples)
    pos, neg = get_closure(world, constants, target, pos, neg)

    return pos, neg


@Tabling
def get_masks(target: 'Literal', background: List['Clause']) -> List['Mask']:
    from foil.learning import get_masks

    return get_masks([*[l for c in background for l in c.literals], target])


@Tabling
def get_variables(target: 'Literal', body: List['Literal']) -> List['Variable']:
    from foil.learning import get_variables

    return get_variables([target, *body])


@Tabling
def itemize(variables: List['Variable'], arity: int) -> List[List['Variable']]:
    from foil.learning import itemize

    return itemize(variables, arity)
