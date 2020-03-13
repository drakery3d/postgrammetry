import bpy


class BatchBakerPanel(bpy.types.Panel):
    bl_label = 'Batch Baking'
    bl_idname = 'batch_baker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bake'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        layout.prop_search(context.scene,
                           'highpoly_bake_obj',
                           context.scene,
                           'objects',
                           text='Highpoly')

        row = layout.row()
        row.prop(context.scene,
                 'bake_multiple',
                 text='Bake onto multiple meshes')
        row = layout.row()
        if (context.scene.bake_multiple):
            layout.prop_search(context.scene,
                               'lowpoly_bake_obj',
                               bpy.data,
                               'collections',
                               text='Lowpoly')
        else:
            layout.prop_search(context.scene,
                               'lowpoly_bake_obj',
                               context.scene,
                               'objects',
                               text='Lowpoly')

        row = layout.row()
        row.prop(context.scene, 'bake_diffuse', text='Diffuse')
        row = layout.row()
        row.prop(context.scene, 'bake_normal', text='Normal')
        row = layout.row()
        row.prop(context.scene, 'bake_ao', text='Ambient Occlusion')

        col = layout.column()
        col.prop(context.scene, 'bake_out_path', text='Output')

        row = layout.row()
        op = row.operator('bb.bake', text='Bake')