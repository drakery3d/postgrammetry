import bpy
import os

from ..utils import get_absolute_path, open_os_directory
from ..constants import addon_id, panel, texture_resize_idname, texture_resize_open_idname


class BatchResizeTexturesOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{texture_resize_idname}'
    bl_label = 'Resize Textures'

    def execute(self, context):
        self.settings = bpy.context.scene.postgrammetry_texture_resize
        path = get_absolute_path(self.settings.path)

        count = 0
        for file in os.listdir(path):
            filepath = os.path.join(path, file)
            if os.path.isfile(filepath):
                if os.path.splitext(file)[1] == '.tif':
                    index = bpy.data.images.find(file)
                    image = bpy.data.images[index] if index >= 0 else bpy.data.images.load(
                        filepath)
                    self.process(image)
                    count += 1

        self.report({'INFO'}, f'Resized {str(count)} images.')
        return {'FINISHED'}

    def process(self, image):
        image_size = image.size[0]
        if image_size != image.size[1]:
            return self.report(
                {'WARNING'}, f'Image is not a square. Skip {image.name}')

        SMALLEST_SIZE = 2**11  # 2048
        if image_size < SMALLEST_SIZE:
            return self.report(
                {'WARNING'}, f'Image is too small to reisze. Skip {image.name}')

        sizes = []
        s = SMALLEST_SIZE
        while s <= image_size:
            sizes.append(s)
            s *= 2
        sizes.reverse()

        name = os.path.splitext(image.name)[0]
        for size in sizes:
            self.resize(image, name, size)

    def resize(self, image, name, size):
        temp = bpy.data.images[image.name].copy()
        temp.scale(size, size)
        temp.file_format = 'JPEG'
        # FIXME how to configure compression / quality?
        # TODO also save as tif!?
        path = self.settings.path
        temp.filepath_raw = os.path.join(path, f'{name}_{str(size)}px.jpg')
        temp.save()
        bpy.data.images.remove(temp)


class OpenResizeDirectoryOperator(bpy.types.Operator):
    bl_idname = f'{addon_id}.{texture_resize_open_idname}'
    bl_label = 'Open'
    bl_options = {'UNDO'}

    def execute(self, context):
        settings = bpy.context.scene.postgrammetry_texture_resize
        path = get_absolute_path(settings.path)
        open_os_directory(path)
        return {'FINISHED'}
