# TODO maybe save images with non-transparent background as jpg
# TODO add sun with sun addon

import bpy
import addon_utils
import math
import time
import os

from ..utils import get_absolute_path, open_os_directory, un_hide, hide, deselect_all, hide_all_except, select_obj


class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render'
    bl_label = 'batch render'
    bl_options = {'UNDO'}

    def execute(self, context):
        start_time = time.time()
        render.render()
        end_time = time.time()
        print("Rendering done in " + str(end_time - start_time) + " seconds")
        return {'FINISHED'}


class RenderSetupOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render_setup'
    bl_label = 'setup render'
    bl_options = {'UNDO'}

    def execute(self, context):
        setup_addon()
        setup_defaults()
        return {'FINISHED'}


# TODO use of a render class might be useless here
class Render():
    def render(self):
        setup_addon()

        for obj_name in [obj.name for obj in bpy.data.objects]:
            hide(obj_name)

        self.obj = bpy.context.object
        un_hide(self.obj.name)
        bpy.context.scene.frame_set(0)

        if bpy.context.scene.render_full:
            self.render_full()
        if bpy.context.scene.render_turntable:
            self.render_turntable()

        if bpy.context.scene.render_matcap:
            self.render_matcap()
        if bpy.context.scene.render_texture_maps:
            self.render_textures()
        if bpy.context.scene.render_wireframe:
            self.render_wireframe()
        if bpy.context.scene.render_uv_grid:
            self.render_uv_grid()

        self.setup_cycles()

        path = get_absolute_path(bpy.context.scene.render_out_path)
        files = os.listdir(path)
        for file in files:
            filename, extension = os.path.splitext(file)
            if filename.endswith('0000'):
                new_filename = file.replace('0000', '')
                os.rename(os.path.join(path, file),
                          os.path.join(path, new_filename))

    def setup_compositing_nodes(self):
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        for node in tree.nodes:
            tree.nodes.remove(node)

        self.render_layer_node = tree.nodes.new(type='CompositorNodeRLayers')
        self.render_layer_node.location = 0, 0

        if bpy.context.scene.render.engine == 'CYCLES':
            self.denoise_node = tree.nodes.new(type='CompositorNodeDenoise')
            self.denoise_node.location = 300, 0

            self.hue_sat_node = tree.nodes.new('CompositorNodeHueSat')
            self.hue_sat_node.location = 500, 0
            tree.links.new(
                self.denoise_node.outputs['Image'], self.hue_sat_node.inputs['Image'])
            self.bright_contrast_node = tree.nodes.new(
                'CompositorNodeBrightContrast')
            self.bright_contrast_node.location = 700, 0
            tree.links.new(
                self.hue_sat_node.outputs['Image'], self.bright_contrast_node.inputs['Image'])
            render.hue_sat_node.inputs['Saturation'].default_value = bpy.context.scene.render_saturation
            render.bright_contrast_node.inputs['Contrast'].default_value = bpy.context.scene.render_contrast

            tree.links.new(
                self.denoise_node.inputs['Image'], self.render_layer_node.outputs['Noisy Image'])
            tree.links.new(
                self.denoise_node.inputs['Normal'], self.render_layer_node.outputs['Denoising Normal'])
            tree.links.new(
                self.denoise_node.inputs['Albedo'], self.render_layer_node.outputs['Denoising Albedo'])
            if bpy.context.scene.render_transparent:
                self.output_node_transparent = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_transparent.location = 900, 0
                self.output_node_transparent.base_path = bpy.context.scene.render_out_path

            if bpy.context.scene.render_black_bg:
                self.black_bg_mix_node = tree.nodes.new(
                    type='CompositorNodeMixRGB')
                self.black_bg_mix_node.location = 700, -200
                tree.links.new(
                    self.render_layer_node.outputs['Alpha'], self.black_bg_mix_node.inputs[0])
                tree.links.new(
                    self.bright_contrast_node.outputs['Image'], self.black_bg_mix_node.inputs[2])
                black = 0.0012
                self.black_bg_mix_node.inputs[1].default_value = (
                    black, black, black, 1)
                self.output_node_black_bg = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_black_bg.location = 900, -200
                self.output_node_black_bg.base_path = bpy.context.scene.render_out_path

            if bpy.context.scene.render_white_bg:
                self.white_bg_mix_node = tree.nodes.new(
                    type='CompositorNodeMixRGB')
                self.white_bg_mix_node.location = 700, -400
                tree.links.new(
                    self.render_layer_node.outputs['Alpha'], self.white_bg_mix_node.inputs[0])
                tree.links.new(
                    self.bright_contrast_node.outputs['Image'], self.white_bg_mix_node.inputs[2])
                self.white_bg_mix_node.inputs[1].default_value = (
                    1, 1, 1, 1)  # TODO this isn't really white
                self.output_node_white_bg = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_white_bg.location = 900, -400
                self.output_node_white_bg.base_path = bpy.context.scene.render_out_path

        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            if bpy.context.scene.render_transparent:
                self.output_node_transparent = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_transparent.location = 500, 0
                self.output_node_transparent.base_path = bpy.context.scene.render_out_path

            if bpy.context.scene.render_black_bg:
                self.black_bg_mix_node = tree.nodes.new(
                    type='CompositorNodeMixRGB')
                self.black_bg_mix_node.location = 500, -300
                tree.links.new(
                    self.render_layer_node.outputs['Alpha'], self.black_bg_mix_node.inputs[0])
                tree.links.new(
                    self.render_layer_node.outputs['Image'], self.black_bg_mix_node.inputs[2])
                black = 0.0012
                self.black_bg_mix_node.inputs[1].default_value = (
                    black, black, black, 1)
                self.output_node_black_bg = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_black_bg.location = 700, -300
                self.output_node_black_bg.base_path = bpy.context.scene.render_out_path

            if bpy.context.scene.render_white_bg:
                self.white_bg_mix_node = tree.nodes.new(
                    type='CompositorNodeMixRGB')
                self.white_bg_mix_node.location = 500, -600
                tree.links.new(
                    self.render_layer_node.outputs['Alpha'], self.white_bg_mix_node.inputs[0])
                tree.links.new(
                    self.render_layer_node.outputs['Image'], self.white_bg_mix_node.inputs[2])
                self.white_bg_mix_node.inputs[1].default_value = (1, 1, 1, 1)
                self.output_node_white_bg = tree.nodes.new(
                    type='CompositorNodeOutputFile')
                self.output_node_white_bg.location = 700, -600
                self.output_node_white_bg.base_path = bpy.context.scene.render_out_path

        self.rename_file_out_ms('render')

    def rename_file_out_ms(self, name):
        ms = int(round(time.time() * 1000))
        self.rename_compositing_file_outputs(f'{str(ms)}_{name}_')

    def rename_compositing_file_outputs(self, prefix):
        transparent_name = prefix + 'transparent'
        black_background_name = prefix + 'black-bg'
        white_background_name = prefix + 'white-bg'

        tree = bpy.context.scene.node_tree

        if bpy.context.scene.render.engine == 'CYCLES':
            if bpy.context.scene.render_transparent:
                self.output_node_transparent.file_slots.remove(
                    self.output_node_transparent.inputs[0])
                self.output_node_transparent.file_slots.new(transparent_name)
                tree.links.new(
                    self.bright_contrast_node.outputs['Image'], self.output_node_transparent.inputs[transparent_name])

            if bpy.context.scene.render_black_bg:
                self.output_node_black_bg.file_slots.remove(
                    self.output_node_black_bg.inputs[0])
                self.output_node_black_bg.file_slots.new(black_background_name)
                tree.links.new(
                    self.black_bg_mix_node.outputs['Image'], self.output_node_black_bg.inputs[black_background_name])

            if bpy.context.scene.render_white_bg:
                self.output_node_white_bg.file_slots.remove(
                    self.output_node_white_bg.inputs[0])
                self.output_node_white_bg.file_slots.new(white_background_name)
                tree.links.new(
                    self.white_bg_mix_node.outputs['Image'], self.output_node_white_bg.inputs[white_background_name])

        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            if bpy.context.scene.render_transparent:
                self.output_node_transparent.file_slots.remove(
                    self.output_node_transparent.inputs[0])
                self.output_node_transparent.file_slots.new(transparent_name)
                tree.links.new(
                    self.render_layer_node.outputs['Image'], self.output_node_transparent.inputs[transparent_name])

            if bpy.context.scene.render_black_bg:
                self.output_node_black_bg.file_slots.remove(
                    self.output_node_black_bg.inputs[0])
                self.output_node_black_bg.file_slots.new(black_background_name)
                tree.links.new(
                    self.black_bg_mix_node.outputs['Image'], self.output_node_black_bg.inputs[black_background_name])

            if bpy.context.scene.render_white_bg:
                self.output_node_white_bg.file_slots.remove(
                    self.output_node_white_bg.inputs[0])
                self.output_node_white_bg.file_slots.new(white_background_name)
                tree.links.new(
                    self.white_bg_mix_node.outputs['Image'], self.output_node_white_bg.inputs[white_background_name])

    def render_turntable(self):
        self.setup_cycles()
        number_of_pics = bpy.context.scene.turntable_image_count
        count = 0
        for _ in range(number_of_pics):
            self.obj.rotation_euler[2] += 2 * math.pi / number_of_pics
            self.rename_file_out_ms('turntable_' + str(count))
            bpy.ops.render.render(write_still=True)
            count += 1
        self.obj.rotation_euler[2] = 0

    def render_full(self):
        self.setup_cycles()
        bpy.ops.render.render(write_still=True)

    def render_textures(self):
        self.setup_evee()
        material = self.obj.material_slots[0].material
        textures = []
        for n in material.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                textures.append(n.image)

        nodes = material.node_tree.nodes
        diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_shader_node.location = (100, 500)

        ouput_node = nodes.get("Material Output")
        material.node_tree.links.new(
            diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

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
            material.node_tree.links.new(
                image_texture_node.outputs['Color'], diffuse_shader_node.inputs['Color'])
            self.rename_file_out_ms(
                texture_input_name.lower().replace(' ', '-'))
            bpy.ops.render.render(write_still=True)
            bpy.data.images.remove(image)
            nodes.remove(image_texture_node)

        principled_bsdf = nodes.get("Principled BSDF")
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
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

    def render_wireframe(self):
        self.setup_evee()
        self.render_wireframe_for_obj(self.obj)
        # cut off trailing "0" from <object-name_lod0>
        base_obj_name = self.obj.name[:-1]
        if bpy.context.scene.render_wireframe_look_for_lods:
            for o in bpy.data.objects:
                if self.obj.name != o.name and base_obj_name in o.name:
                    self.render_wireframe_for_obj(o)

        deselect_all()
        select_obj(self.obj)
        hide_all_except(self.obj.name)

    def render_wireframe_for_obj(self, obj):
        hide_all_except(obj.name)
        deselect_all()
        select_obj(obj)

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
        diffuse_shader_node.inputs['Color'].default_value = (255, 255, 255, 1)
        ouput_node = nodes.get("Material Output")
        material.node_tree.links.new(
            diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.mark_freestyle_edge()
        bpy.ops.object.mode_set(mode='OBJECT')

        self.rename_file_out_ms('wireframe')
        bpy.ops.render.render(write_still=True)

        principled_bsdf = nodes.get("Principled BSDF")
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
        nodes.remove(diffuse_shader_node)
        bpy.context.scene.render.use_freestyle = False

    def render_matcap(self):
        self.setup_evee()
        material_name = '__matcap_material'
        material = bpy.data.materials.get(material_name)
        if material != None:
            bpy.data.materials.remove(material)

        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        shader_node = nodes.get('Principled BSDF')
        shader_node.inputs['Metallic'].default_value = 1
        shader_node.inputs['Specular'].default_value = .5
        shader_node.inputs['Roughness'].default_value = .1

        geometry_node = nodes.new('ShaderNodeNewGeometry')
        geometry_node.location = -800, 200
        vector_node = nodes.new('ShaderNodeVectorTransform')
        vector_node.location = -600, 200
        vector_node.vector_type = 'NORMAL'
        vector_node.convert_from = 'OBJECT'
        vector_node.convert_to = 'CAMERA'
        mapping_node = nodes.new('ShaderNodeMapping')
        mapping_node.location = -400, 200
        mapping_node.inputs['Location'].default_value[0] = .5
        mapping_node.inputs['Location'].default_value[1] = .5
        mapping_node.inputs['Scale'].default_value[0] = .5
        mapping_node.inputs['Scale'].default_value[1] = .25
        mapping_node.inputs['Scale'].default_value[2] = -3
        hue_node = nodes.new('ShaderNodeHueSaturation')
        hue_node.inputs['Saturation'].default_value = 1.1
        hue_node.location = -200, 200

        material.node_tree.links.new(
            geometry_node.outputs['Normal'], vector_node.inputs['Vector'])
        material.node_tree.links.new(
            vector_node.outputs['Vector'], mapping_node.inputs['Vector'])
        material.node_tree.links.new(
            mapping_node.outputs['Vector'], hue_node.inputs['Color'])
        material.node_tree.links.new(
            hue_node.outputs['Color'], shader_node.inputs['Base Color'])

        current_material = self.obj.material_slots[0].material
        self.obj.material_slots[0].material = material

        self.rename_file_out_ms('matcap')
        bpy.ops.render.render(write_still=True)

        self.obj.material_slots[0].material = current_material

    def render_uv_grid(self):
        self.setup_evee()

        material = self.obj.material_slots[0].material
        nodes = material.node_tree.nodes
        diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_shader_node.location = (100, 500)

        ouput_node = nodes.get("Material Output")
        material.node_tree.links.new(
            diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])
        shader_node = nodes.get('Principled BSDF')

        image_name = 'uv-grid'
        image = bpy.data.images.get(image_name)
        if image is None:
            bpy.ops.image.new(name=image_name, generated_type='UV_GRID')
            image = bpy.data.images.get(image_name)
        image_texture_node = nodes.new('ShaderNodeTexImage')
        image_texture_node.image = image
        material.node_tree.links.new(
            image_texture_node.outputs['Color'], diffuse_shader_node.inputs['Color'])

        self.rename_file_out_ms('uv')
        bpy.ops.render.render(write_still=True)

        nodes.remove(image_texture_node)
        principled_bsdf = nodes.get("Principled BSDF")
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
        nodes.remove(diffuse_shader_node)

    def setup_cycles(self):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.view_layers[0].cycles.denoising_store_passes = True
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.cycles.use_adaptive_sampling = True
        bpy.context.scene.cycles.adaptive_threshold = 0.01
        bpy.context.scene.cycles.device = 'GPU'
        world = bpy.context.scene.world
        world.use_nodes = True

        background_node = world.node_tree.nodes.get("Background")
        if background_node == None:
            background_node = world.node_tree.nodes.new('ShaderNodeBackground')
        background_node.inputs['Strength'].default_value = 1
        background_node.location = -200, 0
        background_node.inputs['Strength'].default_value = bpy.context.scene.render_bg_strength

        env_texture = world.node_tree.nodes.get("Environment Texture")
        if env_texture == None:
            env_texture = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
            env_texture.location = -500, 0

        if env_texture.image == None and bpy.context.scene.render_env_texture != '':
            hdri_image = bpy.data.images.load(
                bpy.context.scene.render_env_texture)
            env_texture.image = hdri_image

        ouput_node = world.node_tree.nodes.get("World Output")
        ouput_node.location = 0, 0

        world.node_tree.links.new(
            env_texture.outputs['Color'], background_node.inputs['Color'])
        world.node_tree.links.new(
            background_node.outputs['Background'], ouput_node.inputs['Surface'])

        self.setup_compositing_nodes()

    def setup_evee(self):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.use_freestyle = False

        world = bpy.context.scene.world
        world.use_nodes = True

        background_node = world.node_tree.nodes.get("Background")
        if background_node == None:
            background_node = world.node_tree.nodes.new('ShaderNodeBackground')

        for link in background_node.inputs['Color'].links:
            world.node_tree.links.remove(link)
        background_node.inputs['Color'].default_value = (1, 1, 1, 1)

        background_node.location = -200, 0

        ouput_node = world.node_tree.nodes.get("World Output")
        ouput_node.location = 0, 0

        world.node_tree.links.new(
            background_node.outputs['Background'], ouput_node.inputs['Surface'])

        self.setup_compositing_nodes()


class OpenRenderDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render_open_directory'
    bl_label = 'open render directory'
    bl_options = {'UNDO'}

    def execute(self, context):
        path = get_absolute_path(bpy.context.scene.render_out_path)
        open_os_directory(path)
        return {'FINISHED'}


def on_env_texture_updated(self, context):
    world = bpy.context.scene.world
    world.use_nodes = True
    env_texture = world.node_tree.nodes.get("Environment Texture")
    if env_texture == None:
        env_texture = world.node_tree.nodes.new('ShaderNodeTexEnvironment')

    filename = os.path.basename(bpy.context.scene.render_env_texture)
    hdri_image = bpy.data.images.get(filename)
    if hdri_image is None:
        hdri_image = bpy.data.images.load(bpy.context.scene.render_env_texture)
    env_texture.image = hdri_image


def on_bg_strength_updated(self, context):
    world = bpy.context.scene.world
    world.use_nodes = True
    background_node = world.node_tree.nodes.get("Background")
    if background_node == None:
        background_node = world.node_tree.nodes.new('ShaderNodeBackground')
    background_node.inputs['Strength'].default_value = bpy.context.scene.render_bg_strength


def on_turntable_rotation_updated(self, context):
    obj = bpy.context.object
    obj.rotation_euler[2] = bpy.context.scene.render_turntable_rotation


def on_saturation_updated():
    print('heljo')


def on_contrast_updated():
    print('heljo')


def setup_defaults():
    bpy.context.scene.render.resolution_percentage = 200
    bpy.context.scene.cycles.samples = 32
    bpy.context.space_data.shading.use_scene_world = True
    bpy.context.space_data.shading.type = 'MATERIAL'

    camera_name = 'Camera'
    cam = bpy.data.cameras.get(camera_name)
    if cam == None:
        cam = bpy.data.cameras.new(camera_name)
    cam_obj = bpy.data.objects.get(camera_name)
    if cam_obj == None:
        cam_obj = bpy.data.objects.new(camera_name, cam)
        bpy.context.scene.collection.objects.link(cam_obj)
    if bpy.context.region_data.view_perspective in {'PERSP', 'ORTHO'}:
        bpy.context.region_data.view_perspective = 'CAMERA'
    bpy.context.space_data.lock_camera = True
    bpy.context.scene.camera = cam_obj
    cam_obj.data.clip_start = 0.001

    bpy.ops.view3d.view_selected()

    sun_name = 'Sun'
    sun = bpy.data.lights.get(sun_name)
    if sun == None:
        sun = bpy.data.lights.new(name=sun_name, type='SUN')
    sun_obj = bpy.data.objects.get(sun_name)
    if sun_obj == None:
        sun_obj = bpy.data.objects.new(
            name=sun_name, object_data=sun)
        bpy.context.collection.objects.link(sun_obj)
        bpy.context.view_layer.objects.active = sun_obj

        bpy.context.scene.sun_pos_properties.sun_object = sun_obj


def setup_addon():
    addon_utils.enable('sun_position', default_set=True, persistent=True)
    bpy.context.scene.sun_pos_properties.usage_mode = 'HDR'
    bpy.context.scene.sun_pos_properties.bind_to_sun = True
    bpy.context.scene.use_nodes = True
    render.setup_cycles()


def on_contrast_updated(self, context):
    if not hasattr(render, 'bright_contrast_node'):
        render.setup_cycles()
    render.bright_contrast_node.inputs['Contrast'].default_value = bpy.context.scene.render_contrast


def on_saturation_updated(self, context):
    if not hasattr(render, 'hue_sat_node'):
        render.setup_cycles()
    render.hue_sat_node.inputs['Saturation'].default_value = bpy.context.scene.render_saturation


render = Render()
