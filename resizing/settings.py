import bpy


class TextureResizeSettings(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name='path',
        default='//',
        description='The directory of images.',
        subtype='DIR_PATH')
