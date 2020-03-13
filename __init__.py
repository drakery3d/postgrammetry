bl_info = {
    "name": "Batch Baker",
    "author": "Florian Ludewig",
    "description":
    "Batch baking from low to high poly to multiple low poly meshes",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D",
    "category": "Generic"
}

import bpy


class BatchBakerPanel(bpy.types.Panel):
    bl_label = 'Batch Baking'
    bl_idname = 'batch_baker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bake'

    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon="COLORSET_12_VEC")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        layout.prop_search(context.scene,
                           "bake_highpoly",
                           context.scene,
                           "objects",
                           text="Highpoly")

        row = layout.row()
        layout.prop_search(context.scene,
                           "bake_lowpoly",
                           context.scene,
                           "objects",
                           text="Lowpoly")

        row = layout.row()
        op = row.operator("bb.bake", text="Bake")


class BatchBake(bpy.types.Operator):
    bl_idname = "bb.bake"
    bl_label = "batch bake"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("goooO!!!")
        return {'FINISHED'}


classes = (BatchBake, BatchBakerPanel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bake_highpoly = bpy.props.StringProperty(
        name="bake_highpoly",
        default="",
        description="Object to bake from (highpoly)",
    )
    bpy.types.Scene.bake_lowpoly = bpy.props.StringProperty(
        name="bake_lowpoly",
        default="",
        description="Object to bake to (lowpoly)",
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bake_highpoly
    del bpy.types.Scene.bake_lowpoly


if __name__ == "__main__":
    register()