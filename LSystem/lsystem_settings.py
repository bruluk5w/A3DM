import bpy
from math import pi

VARIABLES = {'F', 'X'}
PUSH_STATE = '['
POP_STATE = ']'
ROTATE_X_POS = '+'
ROTATE_X_NEG = '-'
ROTATE_Z_POS = '*'
ROTATE_Z_NEG = '/'
IMPLICIT_SYMBOLS = {'(', ')', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
ALPHABET = VARIABLES | IMPLICIT_SYMBOLS | {PUSH_STATE, POP_STATE, ROTATE_X_POS, ROTATE_X_NEG, ROTATE_Z_POS, ROTATE_Z_NEG}


def get_rule_src(self):
    if 'src' in self:
        return self['src']

    return ''


def set_rule_src(self, src: str):
    print(src)
    if src in VARIABLES:
        self['src'] = src


def get_rule_target(self):
    if 'target' in self:
        return self['target']

    return ''


def set_rule_target(self, target: str):
    if all(x in ALPHABET for x in target):
        self['target'] = target


def get_formula(self):
    if 'formula' in self:
        return self['formula']

    return ''


def set_formula(self, formula):
    if all(x in ALPHABET for x in formula):
        self['formula'] = formula


class ProductionRuleProperty(bpy.types.PropertyGroup):
    src: bpy.props.StringProperty(name='src', maxlen=1, get=get_rule_src, set=set_rule_src, options={'TEXTEDIT_UPDATE'})
    target: bpy.props.StringProperty(name='target', maxlen=500, get=get_rule_target, set=set_rule_target, options={'TEXTEDIT_UPDATE'})


class LSystemSettings(bpy.types.PropertyGroup):
    is_lsystem: bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    object: bpy.props.PointerProperty(type=bpy.types.Object, options={'HIDDEN'})
    depth: bpy.props.IntProperty(name='Depth', default=3, min=0, max=15)
    formula: bpy.props.StringProperty(name='Axiom', get=get_formula, set=set_formula)
    print_formula: bpy.props.BoolProperty(name='Print Expanded String')
    rules: bpy.props.CollectionProperty(name='Rules', type=ProductionRuleProperty, override={'USE_INSERTION'})

    tube_segments: bpy.props.IntProperty(name='Tube Segments', default=6, min=3, max=100)
    default_rotation_x: bpy.props.FloatProperty(name='Default X Rot', default=0.25, min=-1, max=1)
    default_rotation_z: bpy.props.FloatProperty(name='Default Z Rot', default=0.25, min=-1, max=1)


classes = (
    ProductionRuleProperty,
    LSystemSettings,
)
do_register, do_unregister = bpy.utils.register_classes_factory(classes)


def register():
    do_register()
    bpy.types.Object.lsystem = bpy.props.PointerProperty(type=LSystemSettings)


def unregister():
    do_unregister()
    del bpy.types.Object.lsystem

