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


render_from_all_cameras(output_path)
