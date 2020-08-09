import bpy
import subprocess
import sys
import platform
import os

def hide(obj_name):
    obj = bpy.data.objects.get(obj_name)
    obj.hide_render = True
    obj.hide_set(True)


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
