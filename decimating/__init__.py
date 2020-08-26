import bpy

from .panel import DecimatePanel
from .operator import DecimateOperator
from .settings import DecimateSettings


classes = (DecimatePanel, DecimateOperator, DecimateSettings)


def register_decimating():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.postgrammetry_decimate = bpy.props.PointerProperty(
        type=DecimateSettings)


def unregister_decimating():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.postgrammetry_decimate
