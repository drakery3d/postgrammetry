import bpy
import math

from ..utils import get_absolute_path, open_os_directory, un_hide, hide

class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render'
    bl_label = 'batch render'
    bl_options = {'UNDO'}

    def execute(self, context):
      Render()
      return {'FINISHED'}

class Render():
  def __init__(self):
    bpy.context.scene.use_nodes = True

    for obj_name in [obj.name for obj in bpy.data.objects]:
      hide(obj_name)

    obj = bpy.context.object
    un_hide(obj.name)

    # switch on nodes and get reference
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    # clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    # create input image node
    render_layer_node = tree.nodes.new(type='CompositorNodeRLayers')
    render_layer_node.location = 0,0
    denoise_node = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node.location = 300,0
    tree.links.new(denoise_node.inputs['Image'], render_layer_node.outputs['Noisy Image'])
    tree.links.new(denoise_node.inputs['Normal'], render_layer_node.outputs['Denoising Normal'])
    tree.links.new(denoise_node.inputs['Albedo'], render_layer_node.outputs['Denoising Albedo'])
    output_node_transparent = tree.nodes.new(type='CompositorNodeOutputFile')
    output_node_transparent.location = 500,0
    output_node_transparent.base_path = bpy.context.scene.render_out_path
    output_node_transparent.file_slots.remove(output_node_transparent.inputs[0])
    output_node_transparent.file_slots.new("transparent")
    tree.links.new(denoise_node.outputs['Image'], output_node_transparent.inputs['transparent'])

    black_bg_mix_node = tree.nodes.new(type='CompositorNodeMixRGB')
    black_bg_mix_node.location = 500,-300
    tree.links.new(render_layer_node.outputs['Alpha'], black_bg_mix_node.inputs[0])
    tree.links.new(denoise_node.outputs['Image'], black_bg_mix_node.inputs[2])
    black = 0.0012
    black_bg_mix_node.inputs[1].default_value = (black, black, black, 1)
    output_node_black_bg = tree.nodes.new(type='CompositorNodeOutputFile')
    output_node_black_bg.location = 700,-300
    output_node_black_bg.base_path = bpy.context.scene.render_out_path
    output_node_black_bg.file_slots.remove(output_node_black_bg.inputs[0])
    output_node_black_bg.file_slots.new("black-bg")
    tree.links.new(black_bg_mix_node.outputs['Image'], output_node_black_bg.inputs['black-bg'])

    white_bg_mix_node = tree.nodes.new(type='CompositorNodeMixRGB')
    white_bg_mix_node.location = 500,-600
    tree.links.new(render_layer_node.outputs['Alpha'], white_bg_mix_node.inputs[0])
    tree.links.new(denoise_node.outputs['Image'], white_bg_mix_node.inputs[2])
    white_bg_mix_node.inputs[1].default_value = (1, 1, 1, 1)
    output_node_white_bg = tree.nodes.new(type='CompositorNodeOutputFile')
    output_node_white_bg.location = 700,-300
    output_node_white_bg.base_path = bpy.context.scene.render_out_path
    output_node_white_bg.file_slots.remove(output_node_white_bg.inputs[0])
    output_node_white_bg.file_slots.new("white-bg")
    tree.links.new(white_bg_mix_node.outputs['Image'], output_node_white_bg.inputs['white-bg'])


    self.render_full(obj)
    # self.render_inspection(obj)
    # self.render_turntable(obj)

  def render_turntable(self, obj):
    self.setup_cycles()
    number_of_pics = bpy.context.scene.turntable_image_count
    count = 0
    for _ in range(number_of_pics):
      obj.rotation_euler[2] += 2 * math.pi / number_of_pics
      bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.render_out_path + 'turntable_' + str(count))
      bpy.ops.render.render(write_still = True)
      count += 1
    obj.rotation_euler[2] = 0

  def render_inspection(self, obj):
    self.render_textures(obj)
    self.render_wireframe(obj)
    # self.render_full(obj)

  def render_full(self, obj):
    self.setup_cycles()
    # TODO denoise (or button to setup compositing nodes)
    # bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.render_out_path + 'full')
    bpy.ops.render.render(write_still = True)


  def render_textures(self, obj):
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

    shader_node = nodes.get('Principled BSDF')
    textures = []
    self.traverse_node_images(shader_node, textures, None)

    self.setup_evee()
    for texture_info in textures:
      texture = texture_info[0]
      texture_input_name = texture_info[1]
      image_texture_node = nodes.new('ShaderNodeTexImage')
      image = bpy.data.images[texture.name].copy()
      image.colorspace_settings.name = 'sRGB'
      image_texture_node.image = image
      material.node_tree.links.new(image_texture_node.outputs['Color'], diffuse_shader_node.inputs['Color'])
      bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.render_out_path + texture_input_name.lower().replace(' ', '-'))
      bpy.ops.render.render(write_still = True)
      bpy.data.images.remove(image)
      nodes.remove(image_texture_node)

    principled_bsdf = nodes.get("Principled BSDF")
    material.node_tree.links.new(principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
    nodes.remove(diffuse_shader_node)

  def traverse_node_images(self, node, textures, origin_input):
    if node.type == 'TEX_IMAGE':
      texture_info = (node.image, origin_input.name)
      textures.append(texture_info)
    if len(node.inputs) == 0:
      return textures
    for input in node.inputs:
      origin = origin_input
      if origin == None:
        origin = input
      if len(input.links) == 0:
        continue
      for link in input.links:
        self.traverse_node_images(link.from_node, textures, origin)

  def render_wireframe(self, obj):
    bpy.context.scene.render.use_freestyle = True
    scene = bpy.context.scene
    freestyle = scene.view_layers[0].freestyle_settings
    linestyle = freestyle.linesets[0]
    scene.render.use_freestyle = True
    linestyle.select_silhouette = False
    linestyle.select_border = False
    linestyle.select_crease = False
    linestyle.select_edge_mark = True

    bpy.data.linestyles["LineStyle"].color = (0, 0, 0)
    bpy.data.linestyles["LineStyle"].thickness = 1.5

    material = obj.material_slots[0].material
    nodes = material.node_tree.nodes
    diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_shader_node.location = (100, 500)
    ouput_node = nodes.get("Material Output")
    material.node_tree.links.new(diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_freestyle_edge()
    bpy.ops.object.mode_set(mode='OBJECT')


    bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.render_out_path + 'wireframe')
    bpy.ops.render.render(write_still = True)

    principled_bsdf = nodes.get("Principled BSDF")
    material.node_tree.links.new(principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
    nodes.remove(diffuse_shader_node)
    bpy.context.scene.render.use_freestyle = False

  def setup_cycles(self):
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.cycles.use_adaptive_sampling = True
    bpy.context.scene.cycles.adaptive_threshold = 0.01
    bpy.context.scene.cycles.device = 'GPU'
    world = bpy.context.scene.world
    world.use_nodes = True
    # TODO hdri user input with rotation
    # TODO add sun with sun addon

    env_texture = world.node_tree.nodes.get("Environment Texture")
    if env_texture == None:
      env_texture = world.node_tree.nodes.new('ShaderNodeTexEnvironment')

    ouput_node = world.node_tree.nodes.get("World Output")
    world.node_tree.links.new(env_texture.outputs['Color'], ouput_node.inputs['Surface'])


  def setup_evee(self):
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.use_freestyle = False

    world = bpy.context.scene.world
    world.use_nodes = True

    background_node = world.node_tree.nodes.get("Background")
    if background_node == None:
      background_node = world.node_tree.nodes.new('ShaderNodeBackground')

    ouput_node = world.node_tree.nodes.get("World Output")
    world.node_tree.links.new(background_node.outputs['Background'], ouput_node.inputs['Surface'])

class OpenRenderDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render_open_directory'
    bl_label = 'open render directory'
    bl_options = {'UNDO'}

    def execute(self, context):
      path = get_absolute_path(bpy.context.scene.render_out_path)
      open_os_directory(path)
      return {'FINISHED'}