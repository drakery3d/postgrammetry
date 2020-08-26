import bpy
import uuid
import time

from ..utils import un_hide, hide, remove_all_materials_from, remove_unused_images, remove_unused_materials, get_absolute_path, open_os_directory


class BatchBakeOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    def execute(self, context):
        start_time = time.time()
        bpy.context.scene.baking_done = False
        high = context.scene.highpoly_bake_obj

        remove_unused_images()
        remove_unused_materials()

        for obj_name in [obj.name for obj in bpy.data.objects]:
            hide(obj_name)

        self.low_objects_names = [
            obj.name for obj in bpy.data.collections[
                context.scene.lowpoly_bake_obj].all_objects
        ]
        for obj_name in self.low_objects_names:
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

        self.output_sizes = []
        if bpy.context.scene.bake_size_2k:
            self.output_sizes.append(2**11)
        if bpy.context.scene.bake_size_4k:
            self.output_sizes.append(2**12)
        if bpy.context.scene.bake_size_8k:
            self.output_sizes.append(2**13)
        if bpy.context.scene.bake_size_16k:
            self.output_sizes.append(2**14)

        self.max_output_size = max(self.output_sizes)
        self.bake_image = bpy.data.images.new(self.low + str(uuid.uuid4()),
                                              width=self.max_output_size,
                                              height=self.max_output_size)
        self.bake_node.image = self.bake_image

        bpy.data.objects.get(self.high).select_set(True)
        bpy.context.view_layer.objects.active = low

    def bake(self):
        if (bpy.context.scene.bake_albedo):
            self.bake_albedo()
        if (bpy.context.scene.bake_normal):
            self.bake_normal()
        if (bpy.context.scene.bake_ao):
            self.bake_ao()

    def apply_textures(self):
        if bpy.context.scene.bake_albedo:
            self.apply_albedo_texture()
        if bpy.context.scene.bake_normal:
            self.apply_normal_texture()

    def clean(self):
        un_hide(self.low)
        bpy.ops.object.select_all(action='DESELECT')
        self.nodes.remove(self.bake_node)
        bpy.data.images.remove(self.bake_image)

    def apply_albedo_texture(self):
        bpy.data.images.load(self.albedo_image_path)
        albedo_texture_node = self.nodes.new('ShaderNodeTexImage')

        image = bpy.data.images[self.albedo_image_name]
        albedo_texture_node.image = image
        image.reload()

        albedo_texture_node.location = (-300, 300)
        principled = self.nodes.get('Principled BSDF')
        self.material.node_tree.links.new(
            albedo_texture_node.outputs['Color'],
            principled.inputs['Base Color'])

    def apply_normal_texture(self):
        bpy.data.images.load(self.normal_image_path)
        normal_texture_node = self.nodes.new('ShaderNodeTexImage')

        image = bpy.data.images[self.normal_image_name]
        image.colorspace_settings.name = 'Non-Color'
        normal_texture_node.image = image
        image.reload()

        normal_texture_node.location = (-500, 0)

        normal_map_node = self.nodes.new('ShaderNodeNormalMap')
        self.material.node_tree.links.new(normal_texture_node.outputs['Color'],
                                          normal_map_node.inputs['Color'])
        normal_map_node.location = (-200, -50)

        principled = self.nodes.get('Principled BSDF')
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
        if bpy.context.scene.use_cages:
            bpy.context.scene.render.bake.cage_extrusion = bpy.context.scene.cage_extrusion
        else:
            bpy.context.scene.render.bake.cage_extrusion = bpy.context.scene.ray_distance

    def bake_albedo(self):
        self.setup_baking_settings()

        TYPE = 'DIFFUSE'
        bake_type = 'albedo'
        file_format_extension = 'tif'

        bpy.ops.object.bake(type=TYPE)

        self.albedo_image_name = f'{self.low}_{bake_type}_{self.get_size_abbreviation(self.max_output_size)}.{file_format_extension}'
        self.albedo_image_path = f'{bpy.context.scene.bake_out_path}{self.albedo_image_name}'
        self.bake_image.filepath_raw = self.albedo_image_path
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

        self.resize_image(bake_type)

    def bake_normal(self):
        self.setup_baking_settings()

        TYPE = 'NORMAL'
        bake_type = TYPE.lower()
        file_format_extension = 'tif'

        bpy.ops.object.bake(type=TYPE)

        self.normal_image_name = f'{self.low}_{bake_type}_{self.get_size_abbreviation(self.max_output_size)}.{file_format_extension}'
        self.normal_image_path = f'{bpy.context.scene.bake_out_path}{self.normal_image_name}'
        self.bake_image.filepath_raw = self.normal_image_path
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

        self.resize_image(bake_type)

    def bake_ao(self):
        self.setup_baking_settings()
        bpy.context.scene.cycles.samples = bpy.context.scene.ao_samples

        TYPE = 'AO'
        bake_type = TYPE.lower()
        file_format_extension = 'tif'

        bpy.ops.object.bake(type=TYPE)

        self.ao_image_name = f'{self.low}_{bake_type}_{self.get_size_abbreviation(self.max_output_size)}.{file_format_extension}'
        self.ao_image_path = f'{bpy.context.scene.bake_out_path}{self.ao_image_name}'
        self.bake_image.filepath_raw = self.ao_image_path
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

        self.resize_image(bake_type)

    def resize_image(self, type):
        resizes = self.output_sizes.copy()
        resizes.remove(max(self.output_sizes))
        if len(resizes) >= 1:
            # FIXME don't get image from self.bake_image, but rather from type?!
            master_copy = bpy.data.images.get(self.bake_image.name).copy()
            master_copy.name = f'{self.low}_{type}_copy.tif'

            for size in resizes:
                resized = bpy.data.images.get(master_copy.name).copy()
                resized.scale(size, size)
                size_abbreviation = self.get_size_abbreviation(size)

                name = self.low
                if len(self.low_objects_names) == 1:
                    name.replace('lod0', '')
                filepath_raw = f'{bpy.context.scene.bake_out_path}{name}_{type}'
                if len(resized) != 1:
                    filepath_raw = f'{filepath_raw}_{size_abbreviation}'
                filepath_raw = f'{filepath_raw}.tif'

                resized.save()
        # FIXME delete copied images

    def get_size_abbreviation(self, size_in_pixels):
        if size_in_pixels == 2**11:
            return '2k'
        if size_in_pixels == 2**12:
            return '4k'
        if size_in_pixels == 2**13:
            return '8k'
        if size_in_pixels == 2**14:
            return '16k'
        else:
            return ''


class OpenBakeDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.bake_open_directory'
    bl_label = 'open bake directory'
    bl_options = {'UNDO'}

    def execute(self, context):
        path = get_absolute_path(bpy.context.scene.bake_out_path)
        open_os_directory(path)
        return {'FINISHED'}
