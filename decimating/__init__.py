import bpy

from .panel import DecimatePanel
from .decimate import DecimateOperator

classes = (DecimatePanel, DecimateOperator)

def register_decimating():
  for cls in classes:
    bpy.utils.register_class(cls)

def unregister_decimating():
  for cls in classes:
    bpy.utils.unregister_class(cls)