bl_info = {
    'name': 'Postgrammetry',
    'author': 'Florian Ludewig',
    'description':
    'Automation tools for post photogrammetry asset creation',
    'blender': (2, 80, 0),
    'version': (0, 6, 0),
    'location': 'View3D',
    'category': 'Automation'
}

import bpy
import os


from .baking.panel import *
from .baking.bake import *
from .baking.generate_cages import *

from .export.panel import *
from .export.export import *

from .rendering import register_rendering, unregister_rendering

from .resizing.panel import *
from .resizing.resize import *

classes = []
classes += (BatchBakeOperator, BakePanel, GnerateCagesOperator, OpenBakeDirectoryOperator)
classes += (ResizePanel, BatchResizeTexturesOperator)
classes += (ExportPanel, BatchExportOperator, OpenExportDirectoryOperator)

def register():
    print("Register Postgrammetry addon")
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

    bpy.types.Scene.bake_size_2k = bpy.props.BoolProperty(name='bake_size_2k',
                                                          default=False)
    bpy.types.Scene.bake_size_4k = bpy.props.BoolProperty(name='bake_size_4k',
                                                          default=False)
    bpy.types.Scene.bake_size_8k = bpy.props.BoolProperty(name='bake_size_8k',
                                                          default=True)
    bpy.types.Scene.bake_size_16k = bpy.props.BoolProperty(
        name='bake_size_16k', default=False)


    # export
    bpy.types.Scene.export_out_path = bpy.props.StringProperty(
        name="export_out_path",
        default='//',
        description="The folder your models will be saved to",
        subtype='DIR_PATH')
    bpy.types.Scene.export_type_obj = bpy.props.BoolProperty(name='export_type_obj',
                                                          default=True)
    bpy.types.Scene.export_type_fbx = bpy.props.BoolProperty(name='export_type_fbx',
                                                          default=True)
    bpy.types.Scene.export_type_glb = bpy.props.BoolProperty(name='export_type_glb',
                                                          default=False)

    # resize
    bpy.types.Scene.resize_path = bpy.props.StringProperty(
        name="resize_path",
        default='//',
        description="The directory your source images are located",
        subtype='DIR_PATH')

    register_rendering()
    print("Successfully registered Postgrammetry addon")

def unregister():
    print("Unregister Postgrammetry addon")
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
    del bpy.types.Scene.bake_size_2k
    del bpy.types.Scene.bake_size_4k
    del bpy.types.Scene.bake_size_8k
    del bpy.types.Scene.bake_size_16k

    del bpy.types.Scene.export_out_path
    del bpy.types.Scene.export_type_obj
    del bpy.types.Scene.export_type_fbx
    del bpy.types.Scene.export_type_glb

    del bpy.types.Scene.resize_path

    unregister_rendering()
    print("Successfully unregistered Postgrammetry addon")


if __name__ == '__main__':
    register()
