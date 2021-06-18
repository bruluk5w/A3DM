import bpy
from .lsystem_settings import LSystemSettings


def register():
    pass


def unregister():
    pass


def lsystem(obj: bpy.types.Object, settings: LSystemSettings):
    print('Creating L-system with {} and {}'.format(obj.name, str(settings)))
