import bpy

from ..constants import addon_id, decimate_idname
from ..utils import copy_object, select_obj


class DecimateOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{decimate_idname}'
    bl_label = 'Decimate'
    bl_options = {'UNDO'}

    def execute(self, context):
        self.settings = bpy.context.scene.postgrammetry_decimate

        self.obj = bpy.context.view_layer.objects.active
        if self.obj == None:
            self.report({'WARNING'}, 'No object selected.')
            return {'CANCELLED'}
        self.obj_base_name = self.obj.name.replace(
            '_lod0', '') if '_lod0' in self.obj.name else self.obj.name

        if self.settings.is_iterative_mode:
            self.iteratively(self.settings.iterations)
        else:
            self.by_vertices_threshold(self.settings.vertices_threshold)

        return {'FINISHED'}

    def iteratively(self, steps):
        count = 1
        temp_obj = self.obj
        while count <= steps:
            temp_obj = self.copy_object_with_count(temp_obj, count)
            self.apply_decimate_modifier(temp_obj, self.settings.ratio)
            count += 1

    def by_vertices_threshold(self, vertices_threshold):
        count = 1
        temp_obj = self.obj
        while len(temp_obj.data.vertices) > vertices_threshold:
            temp_obj = self.copy_object_with_count(temp_obj, count)
            self.apply_decimate_modifier(temp_obj, self.settings.ratio)
            count += 1

    def apply_decimate_modifier(self, obj, ratio):
        select_obj(obj)
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers['Decimate'].ratio = ratio
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Decimate')

    def copy_object_with_count(self, obj, count):
        return copy_object(obj, self.obj_base_name + '_lod' + str(count))
