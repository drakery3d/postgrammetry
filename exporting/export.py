import bpy

from ..utils import get_absolute_path, open_os_directory


class BatchExportOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.export'
    bl_label = 'batch export'
    bl_options = {'UNDO'}

    def execute(self, context):
        Export()
        return {'FINISHED'}


class Export():
    def __init__(self):
        objects = bpy.context.selected_objects
        self.base_filepath = bpy.context.scene.export_out_path

        for obj in objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            if (bpy.context.scene.export_type_fbx):
                self.fbx(obj)
            if (bpy.context.scene.export_type_obj):
                self.obj(obj)
            if (bpy.context.scene.export_type_glb):
                self.glb(obj)

        for obj in objects:
            obj.select_set(True)

    def fbx(self, obj):
        filepath = bpy.path.abspath(self.base_filepath + obj.name + '.fbx')
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)

    def obj(self, obj):
        filepath = bpy.path.abspath(self.base_filepath + obj.name + '.obj')
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=True)

    def glb(self, obj):
        filepath = bpy.path.abspath(self.base_filepath + obj.name + '.glb')
        bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True)


class OpenExportDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.export_open_directory'
    bl_label = 'open export directory'
    bl_options = {'UNDO'}

    def execute(self, context):
        path = get_absolute_path(bpy.context.scene.export_out_path)
        open_os_directory(path)
        return {'FINISHED'}
