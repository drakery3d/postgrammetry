# TODO background option for environment

import bpy
import math

from .panel import RenderPanel
from .render import BatchRenderOperator, OpenRenderDirectoryOperator, RenderSetupOperator, on_env_texture_updated, on_bg_strength_updated, on_turntable_rotation_updated, on_contrast_updated, on_saturation_updated

classes = (RenderPanel, BatchRenderOperator,
           OpenRenderDirectoryOperator, RenderSetupOperator)


def register_rendering():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.render_out_path = bpy.props.StringProperty(
        name="render_out_path",
        default='//',
        description="The folder your images will be saved to",
        subtype='DIR_PATH')
    bpy.types.Scene.render_hdri = bpy.props.StringProperty(
        name="render_hdri",
        default='//',
        description="The hdri used for rendering",
        subtype='FILE_PATH')
    bpy.types.Scene.turntable_image_count = bpy.props.IntProperty(
        name='turntable_image_count',
        default=7)

    bpy.types.Scene.render_env_texture = bpy.props.StringProperty(
        name='render_env_texture', subtype='FILE_PATH', update=on_env_texture_updated)
    bpy.types.Scene.render_bg_strength = bpy.props.FloatProperty(
        name='render_bg_strength', default=1.0, update=on_bg_strength_updated)

    bpy.types.Scene.render_turntable_rotation = bpy.props.FloatProperty(
        name='render_turntable_rotation', default=0, subtype='ANGLE', step=30, soft_min=0, soft_max=math.radians(360), update=on_turntable_rotation_updated)

    bpy.types.Scene.render_contrast = bpy.props.FloatProperty(
        name='render_contrast', default=0.0, step=0.1, soft_min=-3, soft_max=3, update=on_contrast_updated)
    bpy.types.Scene.render_saturation = bpy.props.FloatProperty(
        name='render_saturation', default=1.0, step=0.1, soft_min=0, soft_max=3, update=on_saturation_updated)

    bpy.types.Scene.render_wireframe = bpy.props.BoolProperty(name='render_wireframe',
                                                              default=True)
    bpy.types.Scene.render_wireframe_look_for_lods = bpy.props.BoolProperty(
        name='render_wireframe_look_for_lods', default=True)
    bpy.types.Scene.render_matcap = bpy.props.BoolProperty(name='render_matcap',
                                                           default=True)
    bpy.types.Scene.render_uv_grid = bpy.props.BoolProperty(name='render_uv_grid',
                                                            default=True)
    bpy.types.Scene.render_texture_maps = bpy.props.BoolProperty(name='render_texture_maps',
                                                                 default=True)
    bpy.types.Scene.render_turntable = bpy.props.BoolProperty(name='render_turntable',
                                                              default=True)
    bpy.types.Scene.render_full = bpy.props.BoolProperty(name='render_full',
                                                         default=False)

    bpy.types.Scene.render_transparent = bpy.props.BoolProperty(name='render_transparent',
                                                                default=True)
    bpy.types.Scene.render_black_bg = bpy.props.BoolProperty(name='render_black_bg',
                                                             default=True)
    bpy.types.Scene.render_white_bg = bpy.props.BoolProperty(name='render_white_bg',
                                                             default=True)


def unregister_rendering():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.turntable_image_count
    del bpy.types.Scene.render_out_path

    del bpy.types.Scene.render_env_texture
    del bpy.types.Scene.render_bg_strength
    del bpy.types.Scene.render_contrast
    del bpy.types.Scene.render_saturation

    del bpy.types.Scene.render_wireframe
    del bpy.types.Scene.render_wireframe_look_for_lods
    del bpy.types.Scene.render_texture_maps
    del bpy.types.Scene.render_matcap
    del bpy.types.Scene.render_uv_grid
    del bpy.types.Scene.render_turntable
    del bpy.types.Scene.render_full

    del bpy.types.Scene.render_transparent
    del bpy.types.Scene.render_black_bg
    del bpy.types.Scene.render_white_bg
