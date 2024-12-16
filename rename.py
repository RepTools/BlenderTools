bl_info = {
    "name": "SW File Rename",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > File Renamer",
    "description": "Batch rename files with various patterns",
    "category": "Utilities",
}

import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator, Panel

class FILE_OT_import_stl_files(Operator):
    bl_idname = "file.import_stl_files"
    bl_label = "Import STL Files"
    bl_description = "Import all STL files from the selected directory"
    
    def execute(self, context):
        path = context.scene.rename_directory
        
        if not path:
            self.report({'ERROR'}, "Please select a directory first")
            return {'CANCELLED'}
            
        for file_name in os.listdir(path):
            if file_name.lower().endswith('.stl'):
                file_path = os.path.join(path, file_name)
                bpy.ops.wm.stl_import(
                    filepath=file_path,
                    global_scale=0.003,
                    forward_axis='NEGATIVE_Z',
                    up_axis='Y'
                )
                
        self.report({'INFO'}, f"Imported STL files from: {path}")
        return {'FINISHED'}

class FILE_OT_rename_files(Operator):
    bl_idname = "file.rename_files"
    bl_label = "Rename Files"
    bl_description = "Rename files in selected directory"
    
    def execute(self, context):
        path = context.scene.rename_directory
        mode = context.scene.rename_mode
        
        if mode == 'STANDARD':
            self.rename(path)
        elif mode == 'REMOVE_P':
            self.removeP(path)
        elif mode == 'SPLIT_MIDDLE':
            self.splitMiddle(path)
            
        self.report({'INFO'}, f"Files renamed in: {path}")
        return {'FINISHED'}
    
    def rename(self, path: str):
        for root, dirs, files in os.walk(path):
            num = 0
            for file_name in files:
                if '-' in file_name:
                    new_name = f"{file_name.split('-')[-3].strip().split(' ')[-1]}-{file_name.split('-')[-2].strip()} {str(num)}.stl"
                    old_path = os.path.join(root, file_name)
                    new_path = os.path.join(root, new_name)
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                    num += 1

    def removeP(self, path: str):
        for file_name in os.listdir(path):
            if "P" in file_name:
                new_name = file_name.replace("P", "")
                old_path = os.path.join(path, file_name)
                new_path = os.path.join(path, new_name)
                os.rename(old_path, new_path)
                print(new_name)

    def splitMiddle(self, path: str):
        for file_name in os.listdir(path):
            split_name = file_name.split(' ')
            if len(split_name[0]) > 7:
                first_index = split_name[0].strip()[:7]
                last_index = split_name[-1]
                new_name = f"{first_index} {last_index}.stl"
                old_path = os.path.join(path, file_name)
                new_path = os.path.join(path, new_name)
                os.rename(old_path, new_path)
                print(new_name)

class FILE_PT_rename_panel(Panel):
    bl_label = "File Renamer"
    bl_idname = "FILE_PT_rename_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'File Renamer'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene, "rename_directory")
        layout.prop(scene, "rename_mode")
        layout.operator("file.rename_files")
        layout.operator("file.import_stl_files")

def register():
    bpy.types.Scene.rename_directory = StringProperty(
        name="Directory",
        description="Choose directory to rename files",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.rename_mode = EnumProperty(
        name="Rename Mode",
        description="Choose the renaming method",
        items=[
            ('STANDARD', "Standard", "Standard renaming pattern"),
            ('REMOVE_P', "Remove P", "Remove 'P' from filenames"),
            ('SPLIT_MIDDLE', "Split Middle", "Split and truncate filenames"),
        ],
        default='STANDARD'
    )
    
    bpy.utils.register_class(FILE_OT_rename_files)
    bpy.utils.register_class(FILE_OT_import_stl_files)
    bpy.utils.register_class(FILE_PT_rename_panel)

def unregister():
    del bpy.types.Scene.rename_directory
    del bpy.types.Scene.rename_mode
    
    bpy.utils.unregister_class(FILE_OT_rename_files)
    bpy.utils.unregister_class(FILE_OT_import_stl_files)
    bpy.utils.unregister_class(FILE_PT_rename_panel)

if __name__ == "__main__":
    register()