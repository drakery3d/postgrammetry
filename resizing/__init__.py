import bpy

from .panel import ResizePanel
from .resize import BatchResizeTexturesOperator, OpenResizeDirectoryOperator

classes = (ResizePanel, BatchResizeTexturesOperator,
           OpenResizeDirectoryOperator)


def register_resizing():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.resize_path = bpy.props.StringProperty(
        name='resize_path',
        default='//',
        description='The directory your source images are located',
        subtype='DIR_PATH')


def unregister_resizing():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.resize_path
