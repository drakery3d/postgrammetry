import bpy

from .operator import on_preview_ratio_updated


class DecimateSettings(bpy.types.PropertyGroup):
    is_iterative_mode: bpy.props.BoolProperty(
        name='is_iterative_mode', default=True)
    iterations: bpy.props.IntProperty(name='iterations', default=4)
    ratio: bpy.props.FloatProperty(
        name='ratio', default=.5, soft_min=.01, soft_max=.99)
    vertices_threshold: bpy.props.IntProperty(
        name='vertices_threshold', default=1000, soft_min=1)

    preview_ratio: bpy.props.FloatProperty(
        name='preview_ratio', default=1.0, soft_min=.01, soft_max=.99, update=on_preview_ratio_updated)
