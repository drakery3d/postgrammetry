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

def unregister_rendering():
  for cls in classes:
    bpy.utils.unregister_class(cls)

  del bpy.types.Scene.turntable_image_count
  del bpy.types.Scene.render_out_path