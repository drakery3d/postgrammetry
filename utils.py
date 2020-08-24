import bpy
import subprocess
import sys
import platform
import os


def hide(obj_name):
    obj = bpy.data.objects.get(obj_name)
    obj.hide_render = True
    obj.hide_set(True)


def deselect_all():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


def hide_all_except(except_obj_name):
    for obj_name in [obj.name for obj in bpy.data.objects]:
        hide(obj_name)
    un_hide(except_obj_name)


def select_obj(obj):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def un_hide(obj_name):
    obj = bpy.data.objects.get(obj_name)
    obj.hide_render = False
    obj.hide_set(False)


def remove_all_materials_from(obj_name):
    obj = bpy.data.objects.get(obj_name)
    obj.data.materials.clear()


def remove_unused_images():
    for img in bpy.data.images:
        if not img.users:
            bpy.data.images.remove(img)


def remove_unused_materials():
    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)


def get_absolute_path(relative_path):
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    return os.path.abspath(directory + relative_path)


def open_os_directory(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def copy_object(source_obj, obj_copy_name):
    obj_copy = source_obj.copy()
    obj_copy.data = source_obj.data.copy()
    obj_copy.animation_data_clear()
    # bpy.context.scene.objects.link(obj_copy)
    # bpy.data.scenes[0].objects.link(obj_copy)
    # bpy.context.scene.objects.link(obj_copy)
    bpy.context.collection.objects.link(obj_copy)
    obj_copy.name = obj_copy_name
    return obj_copy
