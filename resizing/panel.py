import bpy

from ..constants import addon_id, panel, texture_resize_idname, texture_resize_open_idname


class ResizePanel(bpy.types.Panel):
    bl_idname = f'VIEW3D_PT_{texture_resize_idname}'
    bl_label = 'Texture Resizing'
    bl_space_type = panel['space_type']
    bl_region_type = panel['region_type']
    bl_category = panel['category']

    def draw(self, context):
        settings = context.scene.postgrammetry_texture_resize

        row = self.layout.column()
        row.prop(settings, 'path', text='Source')

        row = self.layout.row()
        row.operator(f'{addon_id}.{texture_resize_open_idname}', text='Open')

        self.layout.separator()
        row = self.layout.row()
        row.operator(f'{addon_id}.{texture_resize_idname}',
                     text='Resize Textures', icon='RENDER_RESULT')
