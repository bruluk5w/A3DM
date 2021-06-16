import bpy


def update_formula(self, context):
    lsystem(context.object, context)


class LSystemSettings(bpy.types.PropertyGroup):
    is_lsystem: bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    object: bpy.props.PointerProperty(type=bpy.types.Object, options={'HIDDEN'})
    formula: bpy.props.StringProperty(name="Formula", update=update_formula)
    my_float: bpy.props.FloatProperty()
    my_string: bpy.props.StringProperty()


def lsystem(object: bpy.types.Object, settings: LSystemSettings):
    print("Creating L-system with {} and {}".format(object.name, str(settings)))


def register():
    pass


def unregister():
    pass
