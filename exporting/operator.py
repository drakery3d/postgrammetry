import bpy

from ..utils import get_absolute_path, open_os_directory
from ..constants import addon_id, panel, export_idname, export_open_idname


class BatchExportOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{export_idname}'
    bl_label = 'Export'

    def execute(self, context):
        self.settings = bpy.context.scene.postgrammetry_export

        formats = []
        objects = bpy.context.selected_objects
        for obj in objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            if (self.settings.type_fbx):
                self.fbx(obj)
                formats.append('fbx')
            if (self.settings.type_obj):
                self.obj(obj)
                formats.append('obj')
            if (self.settings.type_glb):
                self.glb(obj)
                formats.append('glb')

        for obj in objects:
            obj.select_set(True)

        formats_str = ', '.join(formats)
        self.report(
            {'INFO'}, f'Exported {len(objects)} {"object" if len(objects) == 1 else "objects"} as {formats_str}.')
        return {'FINISHED'}

    def fbx(self, obj):
        filepath = bpy.path.abspath(self.settings.path + obj.name + '.fbx')
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)

    def obj(self, obj):
        filepath = bpy.path.abspath(self.settings.path + obj.name + '.obj')
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=True)

    def glb(self, obj):
        filepath = bpy.path.abspath(self.settings.path + obj.name + '.glb')
        bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True)


class OpenExportDirectoryOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{export_open_idname}'
    bl_label = 'Open'

    def execute(self, context):
        settings = bpy.context.scene.postgrammetry_export
        open_os_directory(settings.path)
        return {'FINISHED'}
