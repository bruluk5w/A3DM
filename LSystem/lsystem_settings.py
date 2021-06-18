import bpy


class LSystemSettings(bpy.types.PropertyGroup):
    is_lsystem: bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    object: bpy.props.PointerProperty(type=bpy.types.Object, options={'HIDDEN'})
    formula: bpy.props.StringProperty(name="Formula")
    my_float: bpy.props.FloatProperty()
    my_string: bpy.props.StringProperty()


classes = (
    LSystemSettings,
)
do_register, do_unregister = bpy.utils.register_classes_factory(classes)


def register():
    do_register()
    bpy.types.Object.lsystem = bpy.props.PointerProperty(type=LSystemSettings)


def unregister():
    do_unregister()
    del bpy.types.Object.lsystem

