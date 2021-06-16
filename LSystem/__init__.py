import bpy
from . import developer_utils


bl_info = {
    "name": "A3DM LSystems",
    "description": "Creates L Systems",
    "author": "Lukas Brunner",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "View3D",
    "warning": "This addon is just a prototype.",
    "category": "Add Mesh"
}

modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
print("Managing modules: " + str(modules))
register, unregister = bpy.utils.register_submodule_factory(__name__, modules)
