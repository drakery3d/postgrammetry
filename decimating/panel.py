import bpy

from ..constants import addon_id, panel, decimate_idname


class DecimatePanel(bpy.types.Panel):
    bl_idname = f'VIEW3D_PT_{decimate_idname}'
    bl_label = 'Decimation'
    bl_space_type = panel['space_type']
    bl_region_type = panel['region_type']
    bl_category = panel['category']

    def draw(self, context):
        settings = context.scene.postgrammetry_decimate

        row = self.layout.row()
        row.prop(settings, 'is_iterative_mode', text='Use Iterative Mode')

        row = self.layout.row()
        if settings.is_iterative_mode:
            row.prop(settings, 'iterations', text='Iterations')
            row = self.layout.row()
            row.prop(settings, 'ratio', text='Ratio')
        else:
            row.prop(settings, 'vertices_threshold', text='Vertices Threshold')

        row = self.layout.row()
        row.operator(f'{addon_id}.{decimate_idname}')
