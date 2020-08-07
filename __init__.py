bl_info = {
    'name': 'Batch Baker',
    'author': 'Florian Ludewig',
    'description':
    'Batch baking from low to high poly to multiple low poly meshes',
    'blender': (2, 80, 0),
    'version': (0, 4, 1),
    'location': 'View3D',
    'category': 'Automation'
}

import bpy
import os

from .panel import BB_PT_Main
from .bake import BB_OT_BatchBake
from .generate_cages import BB_OT_GenerateCages

classes = (BB_OT_BatchBake, BB_PT_Main, BB_OT_GenerateCages)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.highpoly_bake_obj = bpy.props.StringProperty(
        name='highpoly_bake_obj',
        description='The object you want to bake from')

    bpy.types.Scene.lowpoly_bake_obj = bpy.props.StringProperty(
        name='lowpoly_bake_obj',
        description='The object you want to bake onto')

    bpy.types.Scene.bake_albedo = bpy.props.BoolProperty(
        name='bake_albedo',
        description='Check if you want to bake a albedo map',
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

    bpy.types.Scene.ray_distance = bpy.props.FloatProperty(name='ray_distance',
                                                           default=0,
                                                           subtype='DISTANCE')
    bpy.types.Scene.cage_extrusion = bpy.props.FloatProperty(
        name='cage_extrusion', default=0, subtype='DISTANCE')

    bpy.types.Scene.bake_size_512px = bpy.props.BoolProperty(
        name='bake_size_512px', default=False)
    bpy.types.Scene.bake_size_1k = bpy.props.BoolProperty(name='bake_size_1k',
                                                          default=False)
    bpy.types.Scene.bake_size_2k = bpy.props.BoolProperty(name='bake_size_2k',
                                                          default=True)
    bpy.types.Scene.bake_size_4k = bpy.props.BoolProperty(name='bake_size_4k',
                                                          default=True)
    bpy.types.Scene.bake_size_8k = bpy.props.BoolProperty(name='bake_size_8k',
                                                          default=True)
    bpy.types.Scene.bake_size_16k = bpy.props.BoolProperty(
        name='bake_size_16k', default=False)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.highpoly_bake_obj
    del bpy.types.Scene.lowpoly_bake_obj
    del bpy.types.Scene.bake_albedo
    del bpy.types.Scene.bake_normal
    del bpy.types.Scene.bake_ao
    del bpy.types.Scene.bake_out_path
    del bpy.types.Scene.output_format
    del bpy.types.Scene.baking_done
    del bpy.types.Scene.baking_time
    del bpy.types.Scene.use_cages
    del bpy.types.Scene.ray_distance
    del bpy.types.Scene.cage_extrusion
    del bpy.types.Scene.bake_size_512px
    del bpy.types.Scene.bake_size_1k
    del bpy.types.Scene.bake_size_2k
    del bpy.types.Scene.bake_size_4k
    del bpy.types.Scene.bake_size_8k
    del bpy.types.Scene.bake_size_16k


if __name__ == '__main__':
    register()
