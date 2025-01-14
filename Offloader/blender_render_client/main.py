bl_info = {
    "name": "Remote Render Client",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Remote Render",
    "description": "Client addon for remote rendering",
    "warning": "",
    "category": "Render",
}

import bpy
import socket
import json
import tempfile
import os

class RemoteRenderClientPanel(bpy.types.Panel):
    bl_label = "Remote Render Client"
    bl_idname = "VIEW3D_PT_remote_render_client"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Remote Render'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Server connection settings
        layout.prop(scene, "remote_render_server_ip")
        layout.prop(scene, "remote_render_server_port")
        layout.prop(scene, "remote_render_output_dir")
        
        # Render button
        layout.operator("render.remote_render")

class RemoteRenderOperator(bpy.types.Operator):
    bl_idname = "render.remote_render"
    bl_label = "Render with Server"
    
    def execute(self, context):
        try:
            # Get server details
            server_ip = context.scene.remote_render_server_ip
            server_port = context.scene.remote_render_server_port
            output_dir = context.scene.remote_render_output_dir
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save current blend file to temp
            temp_blend = tempfile.mktemp(suffix='.blend')
            bpy.ops.wm.save_as_mainfile(filepath=temp_blend, copy=True)
            
            # Connect to server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                
                # Send file size first
                file_size = os.path.getsize(temp_blend)
                s.send(str(file_size).encode() + b'\n')
                s.recv(1024)  # Wait for ready signal
                
                # Send file data
                with open(temp_blend, 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        s.send(data)
                
                # Receive number of results
                num_results = int(s.recv(1024).decode().strip())
                s.send(b"OK")  # Acknowledge
                
                # Receive each result
                for _ in range(num_results):
                    # Receive camera name
                    camera_name = s.recv(1024).decode().strip()
                    s.send(b"OK")  # Acknowledge
                    
                    # Receive status and data
                    status_line = s.recv(1024).decode().strip()
                    status_parts = status_line.split('\n')
                    status = status_parts[0]
                    
                    if status == "SUCCESS":
                        # Get image size
                        image_size = int(status_parts[1])
                        s.send(b"OK")  # Acknowledge
                        
                        # Receive and save image
                        output_path = os.path.join(output_dir, f"{camera_name}.png")
                        received_size = 0
                        with open(output_path, 'wb') as f:
                            while received_size < image_size:
                                chunk = s.recv(min(1024, image_size - received_size))
                                if not chunk:
                                    break
                                f.write(chunk)
                                received_size += len(chunk)
                        
                        self.report({'INFO'}, f"Saved render for camera {camera_name}")
                    else:
                        # Handle error
                        error_msg = status_parts[1]
                        self.report({'ERROR'}, f"Failed to render camera {camera_name}: {error_msg}")
                    
                    s.send(b"OK")  # Final acknowledgment
            
            # Clean up temp file
            os.remove(temp_blend)
            
            self.report({'INFO'}, f"Remote rendering completed. Images saved to {output_dir}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Property definitions
def register_properties():
    bpy.types.Scene.remote_render_server_ip = bpy.props.StringProperty(
        name="Server IP",
        default="localhost"
    )
    bpy.types.Scene.remote_render_server_port = bpy.props.IntProperty(
        name="Server Port",
        default=5000,
        min=1024,
        max=65535
    )
    bpy.types.Scene.remote_render_output_dir = bpy.props.StringProperty(
        name="Output Directory",
        default="//renders",
        subtype='DIR_PATH'
    )

def unregister_properties():
    del bpy.types.Scene.remote_render_server_ip
    del bpy.types.Scene.remote_render_server_port
    del bpy.types.Scene.remote_render_output_dir

# Registration
classes = (
    RemoteRenderClientPanel,
    RemoteRenderOperator,
)

def register():
    register_properties()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    unregister_properties()
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register() 