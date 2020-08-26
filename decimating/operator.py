# TODO decimate mode 'decimate until less than X vertices'

import bpy

from ..constants import addon_id, decimate_idname
from ..utils import copy_object, select_obj


class DecimateOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{decimate_idname}'
    bl_label = 'Decimate'
    bl_options = {'UNDO'}

    def execute(self, context):
        selected_obj = bpy.context.view_layer.objects.active
        if selected_obj == None:
            self.report({'WARNING'}, 'No object selected.')
            return {'CANCELLED'}

        base_name = selected_obj.name.replace(
            '_lod0', '') if '_lod0' in selected_obj.name else selected_obj.name
        decimation_steps = bpy.context.scene.postgrammetry_decimate.iterations
        decimation_ratio = bpy.context.scene.postgrammetry_decimate.ratio
        count = 1
        temp_obj = selected_obj
        while count <= decimation_steps:
            temp_obj = copy_object(
                temp_obj, base_name + '_lod' + str(count))
            select_obj(temp_obj)
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers['Decimate'].ratio = decimation_ratio
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Decimate')
            count += 1

        return {'FINISHED'}
