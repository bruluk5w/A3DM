from typing import Dict

import bpy
import bmesh
import bmesh.ops
from mathutils import Matrix
from math import pi
from .lsystem_settings import LSystemSettings, VARIABLES, ALPHABET, PUSH_STATE, POP_STATE
from .build_tree import LSystem, Node


def register():
    pass


def unregister():
    pass


def lsystem(obj: bpy.types.Object, settings: 'LSystemSettings'):
    print('Creating L-system with {} and {}'.format(obj.name, str(settings)))
    if not all((len(rule.src) == 1 and rule.src in VARIABLES) for rule in settings.rules):
        print('Error: Invalid first field in a rule.')
        return

    rules = {rule.src: rule.target for rule in settings.rules}
    rules.update({c: c for c in (VARIABLES - rules.keys())})
    if not 0 < settings.depth < 15:
        print('Error: Invalid recursion depth specified: {}\nShould be between 1 and 15.'.format(settings.depth))
        return

    if not all(x in ALPHABET for x in settings.formula):
        print('Error: Invalid characters in axiom formula.')
        return

    for idx, rule in enumerate(settings.rules):
        num_push = rule.target.count(PUSH_STATE)
        num_pop = rule.target.count(POP_STATE)
        if num_push > num_pop:
            print('Warning: Rule {} pushes states more often than it pops them. '
                  'Each iteration will increase nesting depth.'.format(idx))
        elif num_pop > num_push:
            print('Error: Rule {} pops states more often than it pushes them.'
                  'This is not supported.'.format(idx))
            return

    # expand formula
    formula = settings.formula
    for i in range(settings.depth):
        formula = ''.join([
            rules[c] if c in VARIABLES else c
            for c in formula
        ])

    tree = LSystem()
    tree.build_tree(formula, settings)
    draw_tree(obj, tree, settings)


FlIP_180 = Matrix.Rotation(pi, 4, 'X')


def draw_tree(obj: bpy.types.Object, tree: LSystem, settings: LSystemSettings):
    if not obj or obj.type != 'MESH':
        print('Invalid object passed. There is no mesh.')
        return
    mesh = bmesh.new(use_operators=True)
    mesh = ensure_bmesh(mesh)  # todo: remove

    # recursively draw the tree
    bmesh.ops.create_circle(mesh, cap_ends=True, radius=0.2, segments=settings.tube_segments, matrix=FlIP_180)
    mesh.faces.ensure_lookup_table()
    draw_node(mesh.faces[0], tree.root, mesh, settings)

    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()


def draw_node(last_circle, node: Node, mesh: bmesh.types.BMesh, settings: LSystemSettings):
    print('Draw node')
    when building tree track at which offset children are entered and build them here
    for idx in range(node.elements):
        last_circle = bmesh.ops.extrude_discrete_faces(mesh, faces=[last_circle])['faces'][0]
        bmesh.ops.translate(mesh, verts=last_circle.verts, vec=(0, 0, 1), space=Matrix.Rotation(pi * 0.25 * node.rotate / node.elements, 4, 'X'))

    for idx, child in enumerate(node.children):
        if idx < len(node.children) - 1:
            new_circle = bmesh.ops.duplicate(mesh, geom=[last_circle] + last_circle.edges[:] + last_circle.verts[:])['face_map'][last_circle]
        draw_node(last_circle, child, mesh, settings)
        if idx < len(node.children) - 1:
            last_circle = new_circle


def ensure_bmesh(mesh):
    if not isinstance(mesh, bmesh.types.BMesh):
        bm = bmesh.new(use_operators=False)
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()
        mesh = bm

    return mesh