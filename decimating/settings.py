import bpy


class DecimateSettings(bpy.types.PropertyGroup):
    iterations: bpy.props.IntProperty(name='iterations', default=4)
    ratio: bpy.props.FloatProperty(name='ratio', default=.5, soft_min=0.01, soft_max=.99)
