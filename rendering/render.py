# TODO maybe save images with non-transparent background as jpg
# TODO ability to render multiple cameras

import bpy
import gpu
import bgl
import math
import time
import os
import io_mesh_uv_layout
from io_mesh_uv_layout.export_uv_png import *

from ..utils import get_absolute_path, open_os_directory, un_hide, hide, deselect_all, hide_all_except, select_obj


class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render'
    bl_label = 'batch render'
    bl_options = {'UNDO'}

    def execute(self, context):
        start_time = time.time()
        render.render()
        end_time = time.time()
        print('Rendering done in ' + str(end_time - start_time) + ' seconds')
        return {'FINISHED'}


class Render():
    def render(self):
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
        if bpy.context.scene.render_uv_layout:
            self.render_uv_layout()

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

        self.render_layer_node = bpy.context.scene.node_tree.nodes.get(
            'Render Layers')
        if self.render_layer_node == None:
            self.render_layer_node = tree.nodes.new(
                type='CompositorNodeRLayers')
            self.render_layer_node.location = 0, 0

        self.node_output_file = tree.nodes.get('NodeOutputFile')
        if self.node_output_file == None:
            self.node_output_file = tree.nodes.new(
                type='CompositorNodeOutputFile')
            self.node_output_file.name = 'NodeOutputFile'
            self.node_output_file.format.file_format = 'JPEG'

        self.node_output_file.base_path = bpy.context.scene.render_out_path
        self.rename_file_out_ms('render')

    def rename_file_out_ms(self, name):
        prefix = self.get_file_name_prefix(name)
        self.rename_compositing_file_outputs(prefix)

    def get_file_name_prefix(self, name):
        ms = int(round(time.time() * 1000))
        return f'{str(ms)}_{name}_'

    def rename_compositing_file_outputs(self, prefix):
        render_name = prefix

        tree = bpy.context.scene.node_tree

        self.node_output_file.file_slots.remove(
            self.node_output_file.inputs[0])
        self.node_output_file.file_slots.new(render_name)
        tree.links.new(
            self.render_layer_node.outputs['Image'], self.node_output_file.inputs[render_name])

    def render_turntable(self):
        self.setup_cycles()
        number_of_pics = bpy.context.scene.turntable_image_count
        bpy.context.object.rotation_euler[2] = 0
        count = 0
        for _ in range(number_of_pics):
            self.rename_file_out_ms('turntable_' + str(count))
            bpy.ops.render.render(write_still=True)
            bpy.context.object.rotation_euler[2] += 2 * \
                math.pi / number_of_pics
            count += 1
        bpy.context.object.rotation_euler[2] = 0

    def render_full(self):
        self.setup_cycles()
        bpy.ops.render.render(write_still=True)

    # TODO avoid rendering same texture twice
    def render_textures(self):
        self.setup_evee()
        material = bpy.context.object.material_slots[0].material
        textures = []
        for n in material.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                textures.append(n.image)

        nodes = material.node_tree.nodes
        diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_shader_node.location = (100, 500)

        output_node = nodes.get('Material Output')
        material.node_tree.links.new(
            diffuse_shader_node.outputs['BSDF'], output_node.inputs['Surface'])

        shader_node = nodes.get('Principled BSDF')
        textures = []
        self.traverse_node_images(shader_node, textures, None)

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

        principled_bsdf = nodes.get('Principled BSDF')
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        nodes.remove(diffuse_shader_node)
        self.teardown_evee()

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
        self.render_wireframe_for_objects(bpy.context.selected_objects)
        base_obj_name = bpy.context.object.name[:-1]
        if bpy.context.scene.render_wireframe_look_for_lods:
            for o in bpy.data.objects:
                if bpy.context.object.name != o.name and base_obj_name in o.name:
                    self.render_wireframe_for_objects([o])
        self.teardown_evee()

    def render_wireframe_for_objects(self, objects):
        for obj in objects:
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

            bpy.data.linestyles['LineStyle'].color = (0, 0, 0)
            bpy.data.linestyles['LineStyle'].thickness = 2

            material = obj.material_slots[0].material
            nodes = material.node_tree.nodes
            diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
            diffuse_shader_node.location = (100, 500)
            diffuse_shader_node.inputs['Color'].default_value = (
                255, 255, 255, 1)
            ouput_node = nodes.get('Material Output')
            material.node_tree.links.new(
                diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_freestyle_edge()
            bpy.ops.object.mode_set(mode='OBJECT')

        self.rename_file_out_ms('wireframe')
        bpy.ops.render.render(write_still=True)

        principled_bsdf = nodes.get('Principled BSDF')
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
        nodes.remove(diffuse_shader_node)
        bpy.context.scene.render.use_freestyle = False

    def render_matcap(self):
        self.setup_cycles()
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

        # get normal map from material
        source_material = bpy.context.object.material_slots[0].material
        source_shader_node = source_material.node_tree.nodes.get(
            'Principled BSDF')
        source_normal_map_node = source_shader_node.inputs['Normal'].links[0].from_node
        source_normal_texture_node = source_normal_map_node.inputs['Color'].links[0].from_node

        # apply normal map to matcap
        normal_texture_node = nodes.new('ShaderNodeTexImage')
        normal_texture_node.image = source_normal_texture_node.image
        normal_map_node = nodes.new('ShaderNodeNormalMap')
        normal_texture_node.location = (-500, 0)
        material.node_tree.links.new(normal_texture_node.outputs['Color'],
                                     normal_map_node.inputs['Color'])
        normal_map_node.location = (-200, -50)
        material.node_tree.links.new(normal_map_node.outputs['Normal'],
                                     shader_node.inputs['Normal'])

        objects = bpy.context.selected_objects
        for obj in objects:
            current_material = obj.material_slots[0].material
            obj.material_slots[0].material = material

        self.rename_file_out_ms('matcap')
        bpy.ops.render.render(write_still=True)

        for obj in objects:
            obj.material_slots[0].material = current_material

    def render_uv_grid(self):
        self.setup_evee()

        material = bpy.context.object.material_slots[0].material
        nodes = material.node_tree.nodes
        diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_shader_node.location = (100, 500)

        ouput_node = nodes.get('Material Output')
        material.node_tree.links.new(
            diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

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
        principled_bsdf = nodes.get('Principled BSDF')
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
        nodes.remove(diffuse_shader_node)
        self.teardown_evee()

    def render_uv_layout(self):
        select_obj(bpy.context.object)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.select_all(action='TOGGLE')

        self.render_uv_layout_with_bg_color('white-bg', 1, 1, 1, 1)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='TOGGLE')

    def render_uv_layout_with_bg_color(self, file_name_suffix, red, green, blue, alpha):
        filepath = get_absolute_path(bpy.context.scene.render_out_path)
        filename = self.get_file_name_prefix('uv_layout')
        min_size = min(bpy.context.scene.render.resolution_x,
                       bpy.context.scene.render.resolution_y)
        res_perc = bpy.context.scene.render.resolution_percentage
        size = int(min_size * res_perc * 0.01)

        self.override_internal_uv_layout_export_method(red, green, blue, alpha)
        path = f'{filepath}/{filename}{file_name_suffix}.png'
        bpy.ops.uv.export_layout(
            filepath=path, size=(size, size), opacity=1)

    def override_internal_uv_layout_export_method(self, red, green, blue, alpha):
        def new_export(filepath, face_data, colors, width, height, opacity):
            offscreen = gpu.types.GPUOffScreen(width, height)
            offscreen.bind()

            try:
                bgl.glClearColor(red, green, blue, alpha)
                bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)
                draw_image(face_data, opacity)

                pixel_data = get_pixel_data_from_current_back_buffer(
                    width, height)
                save_pixels(filepath, pixel_data, width, height)
            finally:
                offscreen.unbind()
                offscreen.free()

        io_mesh_uv_layout.export_uv_png.export = new_export

    def setup_cycles(self):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.view_layers[0].cycles.denoising_store_passes = True
        bpy.context.scene.cycles.use_adaptive_sampling = True
        bpy.context.scene.cycles.adaptive_threshold = 0.01
        bpy.context.scene.cycles.device = 'GPU'
        world = bpy.context.scene.world
        world.use_nodes = True

        background_node = world.node_tree.nodes.get('Background')
        if background_node == None:
            background_node = world.node_tree.nodes.new('ShaderNodeBackground')

        env_texture = world.node_tree.nodes.get('Environment Texture')
        if env_texture:
            world.node_tree.links.new(
                env_texture.outputs['Color'], background_node.inputs['Color'])

        self.setup_compositing_nodes()

    def setup_evee(self):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.render.use_freestyle = False

        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                hide(obj.name)

        world = bpy.context.scene.world
        world.use_nodes = True

        background_node = world.node_tree.nodes.get('Background')
        if background_node == None:
            background_node = world.node_tree.nodes.new('ShaderNodeBackground')
        background_node.inputs['Strength'].default_value = 1

        for link in background_node.inputs['Color'].links:
            world.node_tree.links.remove(link)
        background_node.inputs['Color'].default_value = (1, 1, 1, 1)

        self.setup_compositing_nodes()

    def teardown_evee(self):
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                un_hide(obj.name)


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
    env_texture = world.node_tree.nodes.get('Environment Texture')
    if env_texture == None:
        env_texture = world.node_tree.nodes.new('ShaderNodeTexEnvironment')

    filename = os.path.basename(bpy.context.scene.render_env_texture)
    hdri_image = bpy.data.images.get(filename)
    if hdri_image is None:
        hdri_image = bpy.data.images.load(bpy.context.scene.render_env_texture)
    env_texture.image = hdri_image


render = Render()
