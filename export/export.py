import bpy

class BatchExportOperator(bpy.types.Operator):
    bl_idname = 'batch_export.export'
    bl_label = 'batch export'
    bl_options = {'UNDO'} # TODO what?

    def execute(self, context):
      print("start export")
      return {'FINISHED'}
