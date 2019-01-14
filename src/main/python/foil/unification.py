import re
from collections import namedtuple
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

Value = Union[bool, float, int, str]
Variable = str
Term = Union[Value, Variable]

Substitution = Dict[Variable, Term]
Step = namedtuple('Step', ['index', 'literal', 'substitution'])
Derivation = List[Step]


def is_ground(term: Term) -> bool:
    return term is not None and not is_variable(term)


def is_variable(term: Term) -> bool:
    return isinstance(term, str) and bool(re.match(r'[_A-Z][_a-zA-Z0-9]*', term))


def normalize(term: Term) -> str:
    if isinstance(term, bool) or isinstance(term, float) or isinstance(term, int):
        return str(term)

    if isinstance(term, str) and re.match(r'[_a-zA-Z][_a-zA-Z0-9]*', term):
        return str(term)

    if isinstance(term, str) and any(term.startswith(ch) and term.endswith(ch) for ch in ['"', "'"]):
        return str(term)

    return repr(term)


def unify(var: Variable, term: Term, subst: Substitution) -> Optional[Substitution]:
    if var == term:
        return subst

    if is_variable(term):
        var, term = term, var

    if not is_variable(var):
        return None

    if is_variable(term):
        return equate(var, term, subst)

    return assign(var, term, subst)


def assign(var: Variable, value: Value, subst: Substitution) -> Optional[Substitution]:
    if var not in subst:
        return {var: value, **subst}

    term = subst[var]
    if is_variable(term):
        return {k: value if v == term else term for k, v in subst.items()}

    return subst if term == value else None


def equate(var1: Variable, var2: Variable, subst: Substitution) -> Optional[Substitution]:
    term1, term2 = subst.get(var1), subst.get(var2)
    if is_ground(term1) and is_ground(term2):
        return subst if term1 == term2 else None

    mentions = set([var1, var2] + [k for k, v in subst.items() for t in (term1, term2)
                                   if t and is_variable(t) and v == t])
    if is_ground(term1) and not is_ground(term2):
        label = term1
    elif is_ground(term2) and not is_ground(term1):
        label = term2
    else:
        label = ''.join(sorted(mentions))

    return {var1: label, var2: label, **{k: label if k in mentions else v for k, v in subst.items()}}


def simplify(subst: Substitution) -> Optional[Substitution]:
    result = {}
    for var, term in subst.items():
        if var not in result:
            if is_variable(term):
                vv = sorted({k for k, v in subst.items() if v == term})
                for v in vv:
                    if v != vv[0]:
                        result[v] = vv[0]
            else:
                result[var] = term

    return result


# @Tabling
def resolve(program: 'Program', query: 'Literal') -> Optional[Derivation]:
    for i, clause in enumerate(program.clauses):
        substitution = clause.head.unify(query)
        if substitution is None:
            continue

        derivation = [Step(i, query, substitution)]
        if not clause.body:
            return derivation

        for query in clause.body:
            substituted = query.substitute(substitution)
            sub_goal = resolve(program, substituted)
            if not sub_goal:
                return None

            derivation = [*derivation, *sub_goal]

        return derivation

    return None
