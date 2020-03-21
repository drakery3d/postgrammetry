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
        layout.prop_search(context.scene,
                           'lowpoly_bake_obj',
                           bpy.data,
                           'collections',
                           text='Lowpolys')

        row = layout.row()
        row.prop(context.scene, 'use_cages', text='Use Cages')
        if context.scene.use_cages:
            row = layout.row()
            row.label(text='Name cages like: lod0_cage')

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "bake_diffuse", icon="BLANK1", text="Diffuse")

        row = col.row(align=True)
        row.prop(context.scene, "bake_ao", icon="BLANK1", text="AO")
        if context.scene.bake_ao:
            row.prop(context.scene, "ao_samples", text="")

        row = col.row(align=True)
        row.prop(context.scene, "bake_normal", icon="BLANK1", text="Normal")

        row = layout.column()
        row.prop(context.scene, 'bake_out_path', text='Output')
        row.prop(context.scene, 'output_size', text='Output size')

        row = layout.row()
        op = row.operator('bb.bake', text='Bake')

        if bpy.context.scene.baking_done:
            row = layout.row()
            row.label(text=f'Last bake took {bpy.context.scene.baking_time}s')