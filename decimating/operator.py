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
            self.by_threshold(self.settings.vertices_threshold)

        return {'FINISHED'}

    # Decimate object `steps` times
    def iteratively(self, steps):
        count = 1
        temp_obj = self.obj
        while count <= steps:
            temp_obj = copy_object(temp_obj, self.obj_base_name + '_lod' + str(count))
            select_obj(temp_obj)
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers['Decimate'].ratio = self.settings.ratio
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Decimate')
            count += 1

    # Decimate object until its vertices are below `vertices_threshold`
    def by_threshold(self, vertices_threshold):
        # TODO implement vertex threshold decimate mode
        print('Not implemented.')
