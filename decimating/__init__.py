import bpy

from .panel import DecimatePanel
from .decimate import DecimateOperator

classes = (DecimatePanel, DecimateOperator)


def register_decimating():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.decimate_count = bpy.props.IntProperty(
        name='decimate_count', default=4)

    bpy.types.Scene.decimate_ratio = bpy.props.FloatProperty(
        name='decimate_ratio', default=.5, soft_min=0.001, soft_max=0.999)


def unregister_decimating():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.decimate_count
