import bpy

from .utils import un_hide


class BB_OT_GenerateCages(bpy.types.Operator):
    bl_idname = 'bb.generate_cages'
    bl_label = 'generate cages'
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        low_objects_names = [
            obj.name for obj in bpy.data.collections[
                context.scene.lowpoly_bake_obj].all_objects
        ]
        # TODO try with multiple objects
        for obj_name in low_objects_names:
            self.delete_old_cage(obj_name)
            self.generate_cage(obj_name)

        return {'FINISHED'}

    def delete_old_cage(self, obj_name):
        old_cage = bpy.data.objects.get(obj_name + '_cage')
        if old_cage is not None:
            bpy.data.objects.remove(old_cage)

    def generate_cage(self, obj_name):
        cage = bpy.data.objects.get(obj_name).copy()
        cage.name = obj_name + '_cage'
        bpy.context.scene.collection.objects.link(cage)
        un_hide(cage.name)

        bpy.context.view_layer.objects.active = cage
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        bpy.ops.mesh.select_all(action='SELECT')