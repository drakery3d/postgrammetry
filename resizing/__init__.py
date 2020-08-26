import bpy

from .panel import ResizePanel
from .resize import BatchResizeTexturesOperator, OpenResizeDirectoryOperator
from .settings import TextureResizeSettings

classes = (ResizePanel, BatchResizeTexturesOperator,
           OpenResizeDirectoryOperator, TextureResizeSettings)


def register_resizing():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.postgrammetry_texture_resize = bpy.props.PointerProperty(
        type=TextureResizeSettings)


def unregister_resizing():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.postgrammetry_texture_resize
