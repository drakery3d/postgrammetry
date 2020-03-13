bl_info = {
    'name': 'Batch Baker',
    'author': 'Florian Ludewig',
    'description':
    'Batch baking from low to high poly to multiple low poly meshes',
    'blender': (2, 80, 0),
    'version': (0, 0, 1),
    'location': 'View3D',
    'category': 'Generic'
}

import bpy
import os


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


class BatchBake(bpy.types.Operator):
    bl_idname = 'bb.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    def execute(self, context):
        print('start baking')

        # TODO split into different methods which then serve as "comments"
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

        bake_material = bpy.data.materials.new(
            name=context.scene.lowpoly_bake_obj + '_bake')

        if bpy.context.active_object.data.materials:
            bpy.data.objects[context.scene.lowpoly_bake_obj].data.materials[
                0] = bake_material
        else:
            bpy.data.objects[
                context.scene.lowpoly_bake_obj].data.materials.append(
                    bake_material)

        bake_material.use_nodes = True
        nodes = bake_material.node_tree.nodes
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.select = True

        bake_image = bpy.data.images.new(context.scene.lowpoly_bake_obj +
                                         '_bake',
                                         width=1024,
                                         height=1024)
        bake_node.image = bake_image

        bpy.data.objects[context.scene.highpoly_bake_obj].select_set(True)
        bpy.data.objects[context.scene.lowpoly_bake_obj].select_set(True)

        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='DIFFUSE',
                            use_clear=True,
                            use_selected_to_active=True)

        bake_image.filepath_raw = context.scene.bake_out_path + context.scene.lowpoly_bake_obj + '_diffuse.jpg'
        bake_image.file_format = 'JPEG'
        bake_image.save()

        # remove stuff used for baking

        return {'FINISHED'}


classes = (BatchBake, BatchBakerPanel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.highpoly_bake_obj = bpy.props.StringProperty(
        name='highpoly_bake_obj',
        description='The object you want to bake from')
    # TODO multiple low poly objects (maybe use collection or multiselect)
    bpy.types.Scene.lowpoly_bake_obj = bpy.props.StringProperty(
        name='lowpoly_bake_obj',
        description='The object you want to bake onto')

    bpy.types.Scene.bake_diffuse = bpy.props.BoolProperty(
        name='bake_diffuse',
        description='Check if you want to bake a diffuse map',
        default=True,
    )
    bpy.types.Scene.bake_normal = bpy.props.BoolProperty(
        name='bake_normal',
        description='Check if you want to bake a normal map',
        default=True,
    )
    bpy.types.Scene.bake_ao = bpy.props.BoolProperty(
        name='bake_ao',
        description='Check if you want to bake an ambient occlusion map',
        default=True,
    )

    bpy.types.Scene.bake_out_path = bpy.props.StringProperty(
        name="bake_out_path",
        default='//',
        description="The folder your maps will be saved to",
        subtype='DIR_PATH')


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.highpoly_bake_obj
    del bpy.types.Scene.lowpoly_bake_obj
    del bpy.types.Scene.bake_diffuse
    del bpy.types.Scene.bake_normal
    del bpy.types.Scene.bake_ao
    del bpy.types.Scene.bake_out_path


if __name__ == '__main__':
    register()