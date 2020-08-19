import bpy

class DecimatePanel(bpy.types.Panel):
    bl_label = 'Decimating'
    bl_idname = 'MAIN_PT_batch_decimate'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Postgrammetry'

    def draw(self, context):
        layout = self.layout

        row = layout.column()

        row = layout.row()
        row.operator('postgrammetry.decimate', text='Decimate')