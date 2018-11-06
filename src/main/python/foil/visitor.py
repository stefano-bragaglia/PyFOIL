import json
import re
from typing import Dict
from typing import List
from typing import Union

from arpeggio import NonTerminal
from arpeggio import PTNodeVisitor
from arpeggio import Terminal

Node = Union[Terminal, NonTerminal]


# noinspection PyMethodMayBeStatic
class FoilVisitor(PTNodeVisitor):
    def visit_comment(self, node: Node, children: List) -> str:
        return node.value

    def visit_program(self, node: Node, children: List) -> 'Program':
        from foil.model import Program

        return Program(tuple(children))

    """
        
    def scope():
        return '#', literal, Optional(':', Optional(examples)), '.'
    
    
    def examples():
        return example, ZeroOrMore(',', example)
    
    
    def example():
        return Optional(label), substitution
        
    """
    def visit_substitution(self, node: Node, children: List) -> 'Atom':
        try:
            return children[0]
        except IndexError:
            return {}

    def visit_labels(self, node: Node, children: List) -> bool:
        return node.value == '(+)'

    def visit_substitution(self, node: Node, children: List) -> 'Atom':
        try:
            return children[0]
        except IndexError:
            return {}

    def visit_assignments(self, node: Node, children: List) -> Dict[str, Union[bool, int, float, str]]:
        result = {}
        for child in children:
            result.update(child)

        return result

    def visit_assignment(self, node: Node, children: List) -> Dict[str, Union[bool, int, float, str]]:
        return {children[0]: children[1]}

    def visit_value(self, node: Node, children: List) -> Union[bool, int, float, str]:
        return children[0]

    def visit_clause(self, node: Node, children: List) -> 'Clause':
        from foil.model import Clause

        try:
            return Clause(children[0], tuple(children[1]))
        except IndexError:
            return Clause(children[0], tuple())

    def visit_literals(self, node: Node, children: List) -> List['Literal']:
        return [child for child in children]

    def visit_literal(self, node: Node, children: List) -> 'Literal':
        from foil.model import Literal

        try:
            return Literal(children[0], children[1])
        except IndexError:
            return Literal(children[0], False)

    def visit_negation(self, node: Node, children: List) -> bool:
        return len(children) % 2 == 1

    def visit_atom(self, node: Node, children: List) -> 'Atom':
        from foil.model import Atom

        try:
            return Atom(children[0], tuple(children[1]))
        except IndexError:
            return Atom(children[0], tuple())

    # noinspection RegExpSingleCharAlternation
    def visit_functor(self, node: Node, children: List) -> bool:
        if re.match(r'("|\')[a-z][a-z_0-9]*\1', children[0]):
            return children[0][1:-1]

        return children[0]

    def visit_terms(self, node: Node, children: List) -> List[Union[bool, int, float, str]]:
        return [child for child in children]

    def visit_term(self, node: Node, children: List) -> Union[bool, int, float, str]:
        return children[0]

    def visit_boolean(self, node: Node, children: List) -> bool:
        return children[0]

    def visit_false(self, node: Node, children: List) -> bool:
        return False

    def visit_true(self, node: Node, children: List) -> bool:
        return True

    def visit_number(self, node: Node, children: List) -> Union[int, float]:
        return children[0]

    def visit_real(self, node: Node, children: List) -> float:
        return float(node.value)

    def visit_integer(self, node: Node, children: List) -> int:
        return int(node.value)

    def visit_string(self, node: Node, children: List) -> str:
        return children[0]

    def visit_double_quote(self, node: Node, children: List) -> str:
        return json.dumps(children[0])

    def visit_single_quote(self, node: Node, children: List) -> str:
        return json.dumps(children[0])

    def visit_identifier(self, node: Node, children: List) -> str:
        return str(node.value)

    def visit_variable(self, node: Node, children: List) -> str:
        return str(node.value)
