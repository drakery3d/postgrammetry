import bpy

from .panel import ExportPanel
from .operator import BatchExportOperator, OpenExportDirectoryOperator
from .settings import ExportSettings

classes = (ExportPanel, BatchExportOperator,
           OpenExportDirectoryOperator, ExportSettings)


def register_exporting():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.postgrammetry_export = bpy.props.PointerProperty(
        type=ExportSettings)


def unregister_exporting():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.postgrammetry_export
