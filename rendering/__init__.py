import bpy

from .panel import RenderPanel
from .render import BatchRenderOperator, OpenRenderDirectoryOperator

classes = (RenderPanel, BatchRenderOperator, OpenRenderDirectoryOperator)


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

    bpy.types.Scene.render_wireframe = bpy.props.BoolProperty(name='render_wireframe',
                                                              default=True)
    bpy.types.Scene.render_texture_maps = bpy.props.BoolProperty(name='render_texture_maps',
                                                                 default=True)
    bpy.types.Scene.render_turntable = bpy.props.BoolProperty(name='render_turntable',
                                                              default=True)
    bpy.types.Scene.render_full = bpy.props.BoolProperty(name='render_full',
                                                         default=True)

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

    del bpy.types.Scene.render_wireframe
    del bpy.types.Scene.render_texture_maps
    del bpy.types.Scene.render_turntable
    del bpy.types.Scene.render_full

    del bpy.types.Scene.render_transparent
    del bpy.types.Scene.render_black_bg
    del bpy.types.Scene.render_white_bg
