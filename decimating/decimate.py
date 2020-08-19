# TODO decimate addon

import bpy

class DecimateOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.decimate'
    bl_label = 'batch decimate'
    bl_options = {'UNDO'}

    def execute(self, context):
      return {'FINISHED'}