import bpy
import os

from ..utils import get_absolute_path, open_os_directory


class BatchResizeTexturesOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.resize_textures'
    bl_label = 'batch resize textures'
    bl_options = {'UNDO'}

    def execute(self, context):
        path = get_absolute_path(bpy.context.scene.resize_path)
        files = os.listdir(path)
        for file in files:
            filepath = os.path.join(path, file)
            if os.path.isfile(filepath):
                extension = os.path.splitext(file)[1]
                if extension == '.tif':
                    image = None
                    index = bpy.data.images.find(file)
                    if index >= 0:
                        image = bpy.data.images[index]
                    else:
                        image = bpy.data.images.load(filepath)
                    self.process(image)

        return {'FINISHED'}

    def process(self, image):
        image_size = image.size[0]
        if image_size != image.size[1]:
            # FIXME show error popup
            print('image is not a square... skip')
            return

        SMALLEST_SIZE = 2**11  # 2048
        if image_size < SMALLEST_SIZE:
            print('image is to small to resize... skip')
            return

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
        # FIXME how to configure compression?
        # TODO also save as tif!?
        path = bpy.context.scene.bake_out_path
        temp.filepath_raw = os.path.join(path, f'{name}_{str(size)}px.jpg')
        temp.save()
        bpy.data.images.remove(temp)


class OpenResizeDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.resize_open_directory'
    bl_label = 'open resize directory'
    bl_options = {'UNDO'}

    def execute(self, context):
        path = get_absolute_path(bpy.context.scene.resize_path)
        open_os_directory(path)
        return {'FINISHED'}
