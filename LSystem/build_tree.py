from collections import Callable
from typing import List, Dict, Tuple

from .lsystem_settings import LSystemSettings, VARIABLES, ALPHABET, PUSH_STATE, POP_STATE, ROTATE_X_POS, ROTATE_X_NEG, \
    ROTATE_Z_POS, ROTATE_Z_NEG, IMPLICIT_SYMBOLS


class Node:
    __slots__ = ('depth', 'children', 'child_offsets', 'rotations', 'next_rotation_x', 'next_rotation_z')

    children: List['Node']
    child_offsets: List[int]
    depth: int
    rotations: List[Tuple[float, float]]
    next_rotation_x: float
    next_rotation_z: float

    def __init__(self, depth: int):
        self.depth = depth
        self.children = []
        self.child_offsets = []
        self.rotations = []
        self.next_rotation_x = 0
        self.next_rotation_z = 0


def parse_number(formula, idx):
    end = idx
    while end < len(formula) and formula[end] in '.0123456789':
        end += 1

    try:
        return end, float(formula[idx:end])
    except ValueError:
        return -1, None


class LSystem:
    symbol_handlers = None  # type: Dict[str, Callable[[object, str, str, int], int]]

    def __init__(self):
        self.root = Node(0)
        self.current = self.root
        self.stack = []

    def build_tree(self, formula: str, setting: LSystemSettings):
        cursor = 0
        formula_length = len(formula)
        while cursor < formula_length:
            char = formula[cursor]
            cursor = LSystem.symbol_handlers[char](self, char, formula, cursor)
            if cursor < 0:
                print('An error occurred. Aborting tree building.')
                return

    def handle_push_state(self, char: str, formula: str, idx: int) -> int:
        new = Node(self.current.depth + 1)
        self.current.children.append(new)
        self.current.child_offsets.append(len(self.current.rotations))
        self.stack.append(self.current)
        self.current = new
        return idx + 1

    def handle_pop_state(self, char: str,  formula: str, idx: int) -> int:
        if not self.stack:
            print('Error: expanded formula popped more states than available.')
            return -1

        self.current = self.stack.pop()
        return idx + 1

    def handle_rotate_x(self, char: str, formula: str, idx: int) -> int:
        number = 1
        if len(formula) > idx + 2 and formula[idx + 1] == '(':
            idx, number = parse_number(formula, idx + 2)
            if idx < 0 or formula[idx] != ')':
                print('Error: invalid parameter specified.')
                return -1

        if char == '+':
            self.current.next_rotation_x += number
        elif char == '-':
            self.current.next_rotation_x -= number
        else:
            print('Error: Invalid character encountered in handle_rotate_x: {}.'.format(char))
            return -1

        return idx + 1

    def handle_rotate_z(self, char: str, formula: str, idx: int) -> int:
        number = 1
        if len(formula) > idx + 2 and formula[idx + 1] == '(':
            idx, number = parse_number(formula, idx + 2)
            if idx < 0 or formula[idx] != ')':
                print('Error: invalid parameter specified.')
                return -1

        if char == '*':
            self.current.next_rotation_z += number
        elif char == '/':
            self.current.next_rotation_z -= number
        else:
            print('Error: Invalid character encountered in handle_rotate_z: {}.'.format(char))
            return -1

        return idx + 1

    def handle_variable(self, char: str,  formula: str, idx: int) -> int:
        self.current.rotations.append((self.current.next_rotation_x, self.current.next_rotation_z))
        self.current.next_rotation_x = 0
        self.current.next_rotation_z = 0
        return idx + 1

    def handle_unexpected_symbol(self, char: str,  formula: str, idx: int) -> int:
        print('Unexpected Symbol encountered at position {}: {}'.format(idx, char))
        return -1


LSystem.symbol_handlers = {
    PUSH_STATE: LSystem.handle_push_state,
    POP_STATE: LSystem.handle_pop_state,
    ROTATE_X_POS: LSystem.handle_rotate_x,
    ROTATE_X_NEG: LSystem.handle_rotate_x,
    ROTATE_Z_POS: LSystem.handle_rotate_z,
    ROTATE_Z_NEG: LSystem.handle_rotate_z,
}
LSystem.symbol_handlers.update({var: LSystem.handle_variable for var in VARIABLES})
LSystem.symbol_handlers.update({s: LSystem.handle_unexpected_symbol for s in IMPLICIT_SYMBOLS})

assert all(x in LSystem.symbol_handlers.keys() for x in ALPHABET)


def register():
    pass


def unregister():
    pass