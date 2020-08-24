# TODO decimate mode "decimate until less than X vertices"

import bpy

from ..utils import copy_object, select_obj


class DecimateOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.decimate'
    bl_label = 'batch decimate'
    bl_options = {'UNDO'}

    def execute(self, context):
        selected_obj = bpy.context.view_layer.objects.active
        if selected_obj == None:
            print('no ojbect selected')
            return

        base_name = selected_obj.name.replace(
            '_lod0', '') if '_lod0' in selected_obj.name else selected_obj.name
        decimation_steps = bpy.context.scene.decimate_count
        decimation_ratio = bpy.context.scene.decimate_ratio
        count = 1
        temp_obj = selected_obj
        while count <= decimation_steps:
            temp_obj = copy_object(
                temp_obj, base_name + '_lod' + str(count))
            select_obj(temp_obj)
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = decimation_ratio
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
            count += 1

        return {'FINISHED'}
