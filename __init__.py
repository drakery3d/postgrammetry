bl_info = {
    'name': 'Batch Baker',
    'author': 'Florian Ludewig',
    'description':
    'Batch baking from low to high poly to multiple low poly meshes',
    'blender': (2, 80, 0),
    'version': (0, 4, 0),
    'location': 'View3D',
    'category': 'Generic'
}

import bpy
import os

from .panel import BatchBakerPanel
from .bake import BatchBake

classes = (BatchBake, BatchBakerPanel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.highpoly_bake_obj = bpy.props.StringProperty(
        name='highpoly_bake_obj',
        description='The object you want to bake from')

    bpy.types.Scene.lowpoly_bake_obj = bpy.props.StringProperty(
        name='lowpoly_bake_obj',
        description='The object you want to bake onto')

    bpy.types.Scene.bake_diffuse = bpy.props.BoolProperty(
        name='bake_diffuse',
        description='Check if you want to bake a diffuse map',
        default=True)
    bpy.types.Scene.bake_normal = bpy.props.BoolProperty(
        name='bake_normal',
        description='Check if you want to bake a normal map',
        default=True)
    bpy.types.Scene.bake_ao = bpy.props.BoolProperty(
        name='bake_ao',
        description='Check if you want to bake an ambient occlusion map',
        default=True)

    bpy.types.Scene.bake_out_path = bpy.props.StringProperty(
        name="bake_out_path",
        default='//',
        description="The folder your maps will be saved to",
        subtype='DIR_PATH')

    bpy.types.Scene.output_size = bpy.props.IntProperty(
        name='output_size',
        subtype="PIXEL",
        description='Output size of texture maps in pixels',
        default=2**10 * 8)

    bpy.types.Scene.ao_samples = bpy.props.IntProperty(
        name='ao_samples',
        description='Samples for Ambient Occlusion baking',
        default=64)

    bpy.types.Scene.output_format = bpy.props.StringProperty(
        name="output_format",
        default='TIFF',
        description="Format the textures will be saved as")

    bpy.types.Scene.baking_done = bpy.props.BoolProperty(name='baking_done',
                                                         default=False)
    bpy.types.Scene.baking_time = bpy.props.IntProperty(name='baking_time',
                                                        default=-1)

    bpy.types.Scene.use_cages = bpy.props.BoolProperty(
        name='use_cages',
        description='Check if you want to bake from cages)',
        default=True)
    bpy.types.Scene.ray_distance = bpy.props.IntProperty(name='ray_distance',
                                                         default=0)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.highpoly_bake_obj
    del bpy.types.Scene.lowpoly_bake_obj
    del bpy.types.Scene.bake_diffuse
    del bpy.types.Scene.bake_normal
    del bpy.types.Scene.bake_ao
    del bpy.types.Scene.bake_out_path
    del bpy.types.Scene.output_size
    del bpy.types.Scene.output_format
    del bpy.types.Scene.baking_done
    del bpy.types.Scene.baking_time
    del bpy.types.Scene.use_cages
    del bpy.types.Scene.ray_distance


if __name__ == '__main__':
    register()
