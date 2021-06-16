import bpy

from .lsystem import LSystemSettings


class VIEW3D_MT_add_lsystem(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "add.lsystem"
    bl_label = "L-System"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.select_all(action='DESELECT')
        mesh = bpy.data.meshes.new('mesh')
        obj = bpy.data.objects.new("l_system", mesh)
        obj.lsystem.is_lsystem = True
        obj.lsystem.object = obj
        bpy.context.collection.objects.link(obj)

        return {'FINISHED'}


class OBJECT_PT_lsystem_properties(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lsystem_properties"
    bl_label = "L-System Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.lsystem.is_lsystem

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            lsystem = obj.lsystem
            if lsystem is not None:
                row.prop(lsystem, "formula")


def add_mesh_button(self, context):
    self.layout.operator(VIEW3D_MT_add_lsystem.bl_idname)


classes = (
    VIEW3D_MT_add_lsystem,
    OBJECT_PT_lsystem_properties,
    LSystemSettings,
)
do_register, do_unregister = bpy.utils.register_classes_factory(classes)


def register():
    do_register()
    bpy.types.Object.lsystem = bpy.props.PointerProperty(type=LSystemSettings)
    bpy.types.VIEW3D_MT_mesh_add.append(add_mesh_button)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(add_mesh_button)
    do_unregister()
    del bpy.types.Object.lsystem
