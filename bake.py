import bpy
import uuid
import time

from .utils import un_hide, hide, remove_all_materials_from, remove_unused_images, remove_unused_materials


class BB_OT_BatchBake(bpy.types.Operator):
    bl_idname = 'bb.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    def execute(self, context):
        start_time = time.time()
        bpy.context.scene.baking_done = False
        high = context.scene.highpoly_bake_obj

        for obj_name in [obj.name for obj in bpy.data.objects]:
            hide(obj_name)

        low_objects_names = [
            obj.name for obj in bpy.data.collections[
                context.scene.lowpoly_bake_obj].all_objects
        ]
        for obj_name in low_objects_names:
            Bake(high, obj_name)

        remove_unused_images()
        remove_unused_materials()
        hide(high)
        end_time = time.time()
        bpy.context.scene.baking_done = True
        bpy.context.scene.baking_time = end_time - start_time
        return {'FINISHED'}


class Bake():
    def __init__(self, high, low):
        self.high = high
        self.low = low

        self.prepare()
        self.bake()
        self.apply_textures()
        self.clean()

    def prepare(self):
        bpy.data.scenes[bpy.context.scene.name].render.engine = 'CYCLES'
        un_hide(self.low)
        un_hide(self.high)
        low = bpy.data.objects.get(self.low)

        remove_all_materials_from(self.low)
        self.material = bpy.data.materials.new(name=self.low + '_material')

        if bpy.data.objects[self.low].data.materials:
            bpy.data.objects[self.low].data.materials[0] = self.material
        else:
            bpy.data.objects[self.low].data.materials.append(self.material)

        self.material.use_nodes = True
        self.nodes = self.material.node_tree.nodes
        self.bake_node = self.nodes.new('ShaderNodeTexImage')
        self.bake_node.select = True

        self.bake_image = bpy.data.images.new(
            self.low + str(uuid.uuid4()),
            width=bpy.context.scene.output_size,
            height=bpy.context.scene.output_size)
        self.bake_node.image = self.bake_image

        bpy.data.objects.get(self.high).select_set(True)
        bpy.context.view_layer.objects.active = low

    def bake(self):
        if (bpy.context.scene.bake_diffuse):
            self.bake_diffuse()
        if (bpy.context.scene.bake_normal):
            self.bake_normal()
        if (bpy.context.scene.bake_ao):
            self.bake_ao()

    def apply_textures(self):
        if bpy.context.scene.bake_diffuse:
            self.apply_diffuse_texture()
        if bpy.context.scene.bake_normal:
            self.apply_normal_texture()

    def clean(self):
        hide(self.low)
        bpy.ops.object.select_all(action='DESELECT')
        self.nodes.remove(self.bake_node)
        bpy.data.images.remove(self.bake_image)

    def apply_diffuse_texture(self):
        bpy.data.images.load(self.diffuse_image_path)
        diffuse_texture_node = self.nodes.new('ShaderNodeTexImage')

        image_name = self.low + self.diffuse_image_name
        image = bpy.data.images[image_name]
        diffuse_texture_node.image = image
        image.reload()

        diffuse_texture_node.location = (-300, 300)
        principled = self.nodes.get("Principled BSDF")
        self.material.node_tree.links.new(
            diffuse_texture_node.outputs['Color'],
            principled.inputs['Base Color'])

    def apply_normal_texture(self):
        bpy.data.images.load(self.normal_image_path)
        normal_texture_node = self.nodes.new('ShaderNodeTexImage')

        image_name = self.low + self.normal_image_name
        image = bpy.data.images[image_name]
        image.colorspace_settings.name = 'Non-Color'
        normal_texture_node.image = image
        image.reload()

        normal_texture_node.location = (-500, 0)

        normal_map_node = self.nodes.new('ShaderNodeNormalMap')
        self.material.node_tree.links.new(normal_texture_node.outputs['Color'],
                                          normal_map_node.inputs['Color'])
        normal_map_node.location = (-200, -50)

        principled = self.nodes.get("Principled BSDF")
        self.material.node_tree.links.new(normal_map_node.outputs['Normal'],
                                          principled.inputs['Normal'])

    def setup_baking_settings(self):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.bake.use_cage = bpy.context.scene.use_cages
        if bpy.context.scene.use_cages:
            bpy.context.scene.render.bake.cage_object = bpy.data.objects[
                self.low + '_cage']

    def bake_diffuse(self):
        self.setup_baking_settings()
        bpy.ops.object.bake(type='DIFFUSE')

        self.diffuse_image_name = '_diffuse.tif'
        self.diffuse_image_path = bpy.context.scene.bake_out_path + self.low + self.diffuse_image_name
        self.bake_image.filepath_raw = self.diffuse_image_path
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

    def bake_normal(self):
        self.setup_baking_settings()
        bpy.ops.object.bake(type='NORMAL')

        self.normal_image_name = '_normal.tif'
        self.normal_image_path = bpy.context.scene.bake_out_path + self.low + self.normal_image_name
        self.bake_image.filepath_raw = self.normal_image_path
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

    def bake_ao(self):
        bpy.context.scene.cycles.samples = bpy.context.scene.ao_samples
        bpy.ops.object.bake(type='AO')

        self.ao_image_name = '_ao.tif'
        self.bake_image.filepath_raw = bpy.context.scene.bake_out_path + self.low + self.ao_image_name
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()