import bpy


class ResizePanel(bpy.types.Panel):
    bl_label = 'Texture Resizing'
    bl_idname = 'MAIN_PT_batch_resizing'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Postgrammetry'

    def draw(self, context):
        layout = self.layout

        row = layout.column()
        row.prop(context.scene, 'resize_path', text='')
        row = layout.row()
        row.operator('postgrammetry.resize_open_directory', text='Open directory')

        row = layout.row()
        row.operator('postgrammetry.resize_textures', text='Resize Textures')