from collections import Callable
from typing import List, Dict

from .lsystem_settings import LSystemSettings, VARIABLES, ALPHABET, PUSH_STATE, POP_STATE, ROTATE_POS, ROTATE_NEG


class Node:
    __slots__ = ('depth', 'children', 'child_offsets', 'rotations', 'next_rotation')

    children: List['Node']
    child_offsets: List[int]
    depth: int
    rotations: List[float]
    next_rotation: float

    def __init__(self, depth: int):
        self.depth = depth
        self.children = []
        self.child_offsets = []
        self.rotations = []
        self.next_rotation = 0


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

    def handle_rotate(self, char: str,  formula: str, idx: int) -> int:
        if char == '+':
            self.current.next_rotation += 1
        elif char == '-':
            self.current.next_rotation -= 1
        else:
            print('Error: Invalid character encountered in handle_rotate: {}.'.format(char))
            return -1

        return idx + 1

    def handle_variable(self, char: str,  formula: str, idx: int) -> int:
        self.current.rotations.append(self.current.next_rotation)
        self.current.next_rotation = 0
        return idx + 1


LSystem.symbol_handlers = {
    PUSH_STATE: LSystem.handle_push_state,
    POP_STATE: LSystem.handle_pop_state,
    ROTATE_POS: LSystem.handle_rotate,
    ROTATE_NEG: LSystem.handle_rotate,
}
LSystem.symbol_handlers.update({var: LSystem.handle_variable for var in VARIABLES})

assert all(x in LSystem.symbol_handlers.keys() for x in ALPHABET)


def register():
    pass


def unregister():
    pass