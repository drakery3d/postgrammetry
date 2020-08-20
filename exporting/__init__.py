import bpy

from .panel import ExportPanel
from .export import BatchExportOperator, OpenExportDirectoryOperator

classes = (ExportPanel, BatchExportOperator, OpenExportDirectoryOperator)


def register_exporting():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.export_out_path = bpy.props.StringProperty(
        name="export_out_path",
        default='//',
        description="The folder your models will be saved to",
        subtype='DIR_PATH')
    bpy.types.Scene.export_type_obj = bpy.props.BoolProperty(name='export_type_obj',
                                                             default=True)
    bpy.types.Scene.export_type_fbx = bpy.props.BoolProperty(name='export_type_fbx',
                                                             default=True)
    bpy.types.Scene.export_type_glb = bpy.props.BoolProperty(name='export_type_glb',
                                                             default=False)


def unregister_exporting():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.export_out_path
    del bpy.types.Scene.export_type_obj
    del bpy.types.Scene.export_type_fbx
    del bpy.types.Scene.export_type_glb
