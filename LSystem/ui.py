import bpy

from .lsystem import lsystem


class VIEW3D_MT_add_lsystem(bpy.types.Operator):
    """Add an L-system to the scene"""
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


class LSYSTEM_OT_regenerate_lsystem(bpy.types.Operator):
    """Regenerate an L-system"""
    bl_idname = 'lsystem.regenerate'
    bl_label = 'Regenerate L-System'
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor.location
        obj = context.active_object
        settings = getattr(obj, 'lsystem', None)
        if settings is None:
            return {'CANCELLED'}
        if not settings.is_lsystem:
            return {'CANCELLED'}

        lsystem(obj, settings)
        return {'FINISHED'}


class OBJECT_PT_lsystem_properties(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_lsystem_properties'
    bl_label = 'L-System Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.lsystem.is_lsystem

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(LSYSTEM_OT_regenerate_lsystem.bl_idname)
        row = layout.row()
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            lsystem = obj.lsystem
            if lsystem is not None:
                row.prop(lsystem, 'formula')


def add_mesh_button(self, context):
    self.layout.operator(VIEW3D_MT_add_lsystem.bl_idname)


classes = (
    VIEW3D_MT_add_lsystem,
    LSYSTEM_OT_regenerate_lsystem,
    OBJECT_PT_lsystem_properties,
)
do_register, do_unregister = bpy.utils.register_classes_factory(classes)


def register():
    do_register()
    bpy.types.VIEW3D_MT_mesh_add.append(add_mesh_button)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(add_mesh_button)
    do_unregister()
