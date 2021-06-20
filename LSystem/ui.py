import bpy

from .lsystem import lsystem
from .lsystem_settings import ALPHABET, VARIABLES


class VIEW3D_MT_add_lsystem(bpy.types.Operator):
    """Add an L-System to the scene"""
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


class LSYSTEM_OT_add_rule(bpy.types.Operator):
    """Add a rule the the selected L-System"""
    bl_idname = "lsystem.add_rule"
    bl_label = "Add Rule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        settings = getattr(obj, 'lsystem', None)
        if settings is None:
            return {'CANCELLED'}
        if not settings.is_lsystem:
            return {'CANCELLED'}

        obj.lsystem.rules.add()

        return {'FINISHED'}


class LSYSTEM_OT_remove_rule(bpy.types.Operator):
    """Add a rule the the selected L-System"""
    bl_idname = "lsystem.remove_rule"
    bl_label = "Remove Rule"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(name='index')

    def execute(self, context):
        obj = context.active_object
        settings = getattr(obj, 'lsystem', None)
        if settings is None:
            return {'CANCELLED'}
        if not settings.is_lsystem:
            return {'CANCELLED'}

        obj.lsystem.rules.remove(self.index)

        return {'FINISHED'}


class LSYSTEM_OT_regenerate_lsystem(bpy.types.Operator):
    """Regenerate an L-System"""
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

        bpy.ops.object.mode_set(mode='OBJECT')

        lsystem(obj, settings)

        # bpy.ops.object.mode_set(mode='OBJECT') # todo: remove

        return {'FINISHED'}


class OBJECT_PT_lsystem:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'


class OBJECT_PT_lsystem_properties(OBJECT_PT_lsystem, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_lsystem_properties'
    bl_label = 'L-System Properties'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.lsystem.is_lsystem

    def draw(self, context):
        layout = self.layout
        layout.row().label(text='Variables: ' + ', '.join(VARIABLES))
        layout.row().label(text='Alphabet: ' + ', '.join(ALPHABET))
        layout.row().operator(LSYSTEM_OT_regenerate_lsystem.bl_idname)
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            lsystem = obj.lsystem
            if lsystem is not None:
                layout.row().prop(lsystem, 'depth', slider=True)
                layout.row().prop(lsystem, 'formula')
                layout.row().operator(LSYSTEM_OT_add_rule.bl_idname)
                for idx, rule in enumerate(lsystem.rules):
                    split = layout.split(factor=0.15)
                    col = split.column()
                    row = col.row()
                    row.prop(rule, 'src', text='')
                    row.label(icon='FORWARD')
                    split = split.column().split(factor=0.9)
                    split.column().prop(rule, 'target', text='')
                    op = split.column().operator(LSYSTEM_OT_remove_rule.bl_idname, text="X")
                    op.index = idx


class OBJECT_PT_lsystem_geometry_properties(OBJECT_PT_lsystem, bpy.types.Panel):
    bl_parent_id = 'OBJECT_PT_lsystem_properties'
    bl_label = 'Geometry settings'

    def draw(self, context):
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            lsystem = obj.lsystem
            if lsystem is not None:
                layout = self.layout
                layout.row().prop(lsystem, 'tube_segments', slider=True)


def add_mesh_button(self, context):
    self.layout.operator(VIEW3D_MT_add_lsystem.bl_idname)


classes = (
    VIEW3D_MT_add_lsystem,
    LSYSTEM_OT_add_rule,
    LSYSTEM_OT_remove_rule,
    LSYSTEM_OT_regenerate_lsystem,
    OBJECT_PT_lsystem_properties,
    OBJECT_PT_lsystem_geometry_properties,
)
do_register, do_unregister = bpy.utils.register_classes_factory(classes)


def register():
    do_register()
    bpy.types.VIEW3D_MT_mesh_add.append(add_mesh_button)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(add_mesh_button)
    do_unregister()
