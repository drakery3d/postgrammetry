import bpy


class BB_PT_Main(bpy.types.Panel):
    bl_label = 'Batch Baking'
    bl_idname = 'MAIN_PT_batch_baker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bake'

    def draw(self, context):
        layout = self.layout

        # objects
        row = layout.row()
        layout.prop_search(context.scene,
                           'highpoly_bake_obj',
                           context.scene,
                           'objects',
                           text='Highpoly')
        layout.prop_search(context.scene,
                           'lowpoly_bake_obj',
                           bpy.data,
                           'collections',
                           text='Lowpolys')
        # cages
        row = layout.row()
        row.prop(context.scene, 'use_cages', text='Use Cages')
        if context.scene.use_cages:
            row = layout.row()
            row.label(text='Name cages like: lod0_cage')
        row = layout.row()
        if context.scene.use_cages:
            row.prop(context.scene, 'cage_extrusion', text='Cage Extrusion')
        else:
            row.prop(context.scene, 'ray_distance', text='Ray Distacne')
        row = layout.row()
        row.prop(bpy.context.scene.render.bake, 'margin')
        row = layout.row()
        row.operator('bb.generate_cages', text='Generate cage meshes')

        # maps
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "bake_albedo", icon="BLANK1", text="Albedo")
        row = col.row(align=True)
        row.prop(context.scene, "bake_ao", icon="BLANK1", text="AO")
        if context.scene.bake_ao:
            row.prop(context.scene, "ao_samples", text="")
        row = col.row(align=True)
        row.prop(context.scene, "bake_normal", icon="BLANK1", text="Normal")

        # output
        row = layout.column()
        row.prop(context.scene, 'bake_out_path', text='Output')
        row = layout.row()
        row.operator('postgrammetry.bake_open_directory', text='Open directory')
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "bake_size_2k", icon="BLANK1", text="2k")
        row.prop(context.scene, "bake_size_4k", icon="BLANK1", text="4k")
        row.prop(context.scene, "bake_size_8k", icon="BLANK1", text="8k")
        row.prop(context.scene, "bake_size_16k", icon="BLANK1", text="16k")
        row = col.row(align=True)

        # bake
        row = layout.row()
        row.operator('bb.bake', text='Bake')
        if bpy.context.scene.baking_done:
            row = layout.row()
            row.label(text=f'Last bake took {bpy.context.scene.baking_time}s')