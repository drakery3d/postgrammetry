import bpy


class RenderPanel(bpy.types.Panel):
    bl_label = 'Rendering'
    bl_idname = 'MAIN_PT_batch_renderer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Postgrammetry'

    def draw(self, context):
        layout = self.layout

        row = layout.column()
        row.prop(context.scene, 'render_out_path', text='Output')
        row = layout.row()
        row.operator('postgrammetry.render_open_directory', text='Open directory')

        row = layout.row()
        row.prop(bpy.context.scene.cycles, 'samples')

        row = layout.row()
        row.prop(context.scene, 'turntable_image_count')

        row = layout.row()
        row.operator('postgrammetry.render', text='Render')