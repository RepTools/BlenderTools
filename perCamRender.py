bl_info = {
    "name": "Per Cam Render",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Render > Per Cam Render",
    "description": "Render the scene from every camera in the file to individual PNGs",
    "category": "Render",
}

import bpy
import os

output_path = 'C:/Users/AJFrio/OneDrive - Rep Fitness/Desktop/Fibo2025Renders'

def render_from_all_cameras(output_path):
    # Store the current active camera
    original_camera = bpy.context.scene.camera
    
    # Get the render settings
    scene = bpy.context.scene
    render = scene.render
    
    # Make sure output format is PNG
    render.image_settings.file_format = 'PNG'
    
    # Iterate through all objects in the scene
    for obj in bpy.data.objects:
        # Check if the object is a camera
        if obj.type == 'CAMERA':
            # Set the active camera
            scene.camera = obj
            
            # Set the output path for this camera
            camera_name = obj.name
            render.filepath = os.path.join(output_path, f"{camera_name}.png")
            
            # Render the scene
            bpy.ops.render.render(write_still=True)
            
            print(f"Rendered view from camera: {camera_name}")
    
    # Restore the original active camera
    scene.camera = original_camera



class RENDER_OT_per_cam_render(bpy.types.Operator):
    bl_idname = "render.per_cam_render"
    bl_label = "Render"
    bl_description = "Render the scene from every camera to individual PNG files"

    def execute(self, context):
        render_from_all_cameras(output_path)
        self.report({'INFO'}, f"Rendered all cameras to {output_path}")
        return {'FINISHED'}


class RENDER_PT_per_cam_render_panel(bpy.types.Panel):
    bl_label = "Per Cam Render"
    bl_idname = "RENDER_PT_per_cam_render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.operator("render.per_cam_render", icon='RENDER_STILL')


classes = (RENDER_OT_per_cam_render, RENDER_PT_per_cam_render_panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
