import bpy
from .lsystem_settings import LSystemSettings, VARIABLES, ALPHABET


def register():
    pass


def unregister():
    pass


def lsystem(obj: bpy.types.Object, settings: LSystemSettings):
    print('Creating L-system with {} and {}'.format(obj.name, str(settings)))
    if not all((len(rule.src) == 1 and rule.src in VARIABLES) for rule in settings.rules):
        print('Invalid first field in a rule.')
        return

    rules = {rule.src: rule.target for rule in settings.rules}
    rules.update({c: c for c in (VARIABLES - rules.keys())})
    if not 0 < settings.depth < 15:
        print('Invalid recursion depth specified: {}\nShould be between 1 and 15.'.format(settings.depth))
        return

    if not all(x in ALPHABET for x in settings.formula):
        print('Invalid characters in axiom formula.')
        return

    # expand formula
    formula = settings.formula
    print(type(formula))
    for i in range(settings.depth):
        formula = ''.join([
            rules[c] if c in VARIABLES else c
            for c in formula
        ])

    draw_formula(obj, formula, settings)


def draw_formula(obj: bpy.types.Object, formula:str, setting: LSystemSettings):
    if not obj or obj.type != 'MESH':
        print('Invalid object passed. There is no mesh.')
        return
    mesh = ensure_bmesh(obj.data)


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