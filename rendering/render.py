import bpy

from ..utils import get_absolute_path, open_os_directory

class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render'
    bl_label = 'batch render'
    bl_options = {'UNDO'}

    def execute(self, context):
      Render()
      return {'FINISHED'}

class Render():
  def __init__(self):
    obj = bpy.context.object
    material = obj.material_slots[0].material
    textures = []
    for n in material.node_tree.nodes:
      if n.type == 'TEX_IMAGE':
        textures.append(n.image)

    nodes = material.node_tree.nodes
    diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_shader_node.location = (100, 500)

    ouput_node = nodes.get("Material Output")
    material.node_tree.links.new(diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

    self.setup_evee()
    for texture in textures:
      image_texture_node = nodes.new('ShaderNodeTexImage')
      image = bpy.data.images[texture.name]
      image.colorspace_settings.name = 'sRGB'
      image_texture_node.image = image
      material.node_tree.links.new(image_texture_node.outputs['Color'], diffuse_shader_node.inputs['Color'])
      bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.export_out_path + texture.name)
      bpy.ops.render.render(write_still = True)
      nodes.remove(image_texture_node)

    principled_bsdf = nodes.get("Principled BSDF")
    material.node_tree.links.new(principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
    nodes.remove(diffuse_shader_node)

  def setup_evee(self):
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True

    # TODO create node if not exists
    # world environment strength
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 20

class OpenRenderDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render_open_directory'
    bl_label = 'open render directory'
    bl_options = {'UNDO'}

    def execute(self, context):
      path = get_absolute_path(bpy.context.scene.render_out_path)
      open_os_directory(path)
      return {'FINISHED'}