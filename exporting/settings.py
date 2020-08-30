import bpy


class ExportSettings(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name='path',
        default='//',
        description='The directory your models will be saved to',
        subtype='DIR_PATH')
    type_obj: bpy.props.BoolProperty(name='type_obj', default=True)
    type_fbx: bpy.props.BoolProperty(name='type_fbx', default=True)
    type_glb: bpy.props.BoolProperty(name='type_glb', default=True)
