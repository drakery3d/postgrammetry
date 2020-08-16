import bpy


class ExportPanel(bpy.types.Panel):
    bl_label = 'Exporting'
    bl_idname = 'MAIN_PT_batch_exporter'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Postgrammetry'

    def draw(self, context):
        layout = self.layout

        row = layout.column()
        row.prop(context.scene, 'export_out_path', text='Output')
        row = layout.row()
        row.operator('postgrammetry.export_open_directory', text='Open directory')

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "export_type_obj", icon="BLANK1", text="obj")
        row.prop(context.scene, "export_type_fbx", icon="BLANK1", text="fbx")
        row.prop(context.scene, "export_type_glb", icon="BLANK1", text="glb")
        row = col.row(align=True)

        row = layout.row()
        row.operator('postgrammetry.export', text='Export')