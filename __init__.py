from .decimating import register_decimating, unregister_decimating
from .exporting import register_exporting, unregister_exporting
from .resizing import register_resizing, unregister_resizing
from .rendering import register_rendering, unregister_rendering
from .baking import register_baking, unregister_baking
import os

bl_info = {
    'name': 'Postgrammetry',
    'author': 'Florian Ludewig',
    'description':
    'Automation tools for post photogrammetry asset creation',
    'blender': (3, 0, 0),
    'version': (0, 8, 0),
    'location': 'View3D',
    'category': 'Automation'
}


def register():
    print('Register Postgrammetry addon')
    register_baking()
    register_exporting()
    register_resizing()
    register_rendering()
    register_decimating()
    print('Successfully registered Postgrammetry addon')


def unregister():
    print('Unregister Postgrammetry addon')
    unregister_decimating()
    unregister_rendering()
    unregister_resizing()
    unregister_exporting()
    unregister_baking()
    print('Successfully unregistered Postgrammetry addon')


if __name__ == '__main__':
    register()
