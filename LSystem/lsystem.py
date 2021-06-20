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
    if not 0 <= settings.depth < 15:
        print('Error: Invalid recursion depth specified: {}\nShould be between 0 and 15.'.format(settings.depth))
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

    if settings.print_formula:
        print(formula)

    tree = LSystem()
    tree.build_tree(formula, settings)
    draw_tree(obj, tree, settings)


def draw_tree(obj: bpy.types.Object, tree: LSystem, settings: LSystemSettings):
    if not obj or obj.type != 'MESH':
        print('Invalid object passed. There is no mesh.')
        return
    mesh = bmesh.new(use_operators=True)

    # recursively draw the tree
    bmesh.ops.create_circle(mesh, cap_ends=True, radius=0.2, segments=settings.tube_segments)
    mesh.faces.ensure_lookup_table()
    draw_node(mesh.faces[0], tree.root, mesh, settings)

    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()


def draw_node(last_circle, node: Node, mesh: bmesh.types.BMesh, settings: LSystemSettings,
              transform=Matrix.Identity(4)):
    assert len(node.children) == len(node.child_offsets)

    def duplicate_face(f):
        return bmesh.ops.duplicate(mesh, geom=[f] + f.edges[:] + f.verts[:])['face_map'][f]

    def get_rotations(segment: int):
        angle_x, angle_z = node.rotations[segment]
        angle_x = angle_x * pi * settings.default_rotation_x
        angle_z = angle_z * pi * settings.default_rotation_z
        rot = Matrix.Rotation(angle_z * 0.5, 4, 'Z') @ Matrix.Rotation(angle_x * 0.5, 4, 'X')
        return rot, rot

    children_done = 0

    def draw_children(last_circle, joint_idx: int, transform):
        nonlocal children_done
        while children_done != len(node.child_offsets) and node.child_offsets[children_done] == joint_idx:
            draw_node(duplicate_face(last_circle), node.children[children_done], mesh, settings, transform)
            children_done += 1

    for idx, rotate in enumerate(node.rotations):
        # draw children that branch from the current joint
        draw_children(last_circle, idx, transform)

        # joint_r is rotation of joint from last segment, segment_r is rotation of next segment from this joint
        joint_r, segment_r = get_rotations(idx)
        # orient joint
        bmesh.ops.transform(mesh, verts=last_circle.verts, matrix=joint_r, space=transform.inverted())
        # orient direction for next segment
        transform = transform @ segment_r @ joint_r

        # draw current branch segment
        last_circle = bmesh.ops.extrude_discrete_faces(mesh, faces=[last_circle])['faces'][0]

        t = Matrix.Translation((0, 0, 1))
        bmesh.ops.transform(mesh, verts=last_circle.verts, matrix=t @ segment_r, space=transform.inverted())
        transform = transform @ t

    # draw children that branch from the last joint
    draw_children(last_circle, len(node.rotations), transform)

    assert children_done == len(node.children)

    return


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