import bpy

from ..constants import addon_id, panel, export_idname, export_open_idname


class ExportPanel(bpy.types.Panel):
    bl_idname = f'MAIN_PT_{export_idname}'
    bl_label = 'Exporting'
    bl_space_type = panel['space_type']
    bl_region_type = panel['region_type']
    bl_category = panel['category']

    def draw(self, context):
        settings = context.scene.postgrammetry_export

        row = self.layout.column()
        row.prop(settings, 'path')
        row = self.layout.row()
        row.operator(f'{addon_id}.{export_open_idname}')

        box = self.layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(settings, 'type_obj', icon='BLANK1', text='obj')
        row.prop(settings, 'type_fbx', icon='BLANK1', text='fbx')
        row.prop(settings, 'type_glb', icon='BLANK1', text='glb')
        row = col.row(align=True)

        self.layout.separator()
        row = self.layout.row()
        row.operator(f'{addon_id}.{export_idname}', icon='EXPORT')
