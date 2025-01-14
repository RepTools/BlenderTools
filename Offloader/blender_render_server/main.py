bl_info = {
    "name": "Remote Render Server",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Remote Render Server",
    "description": "Server addon for remote rendering",
    "warning": "",
    "category": "Render",
}

import bpy
import socket
import tempfile
import os
import json

class RenderServerSettings(bpy.types.PropertyGroup):
    is_running: bpy.props.BoolProperty(
        name="Server Running",
        default=False
    )
    port: bpy.props.IntProperty(
        name="Port",
        default=5000,
        min=1024,
        max=65535
    )

class RemoteRenderServerPanel(bpy.types.Panel):
    bl_label = "Remote Render Server"
    bl_idname = "VIEW3D_PT_remote_render_server"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Remote Render Server'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.render_server_settings

        # Server settings
        layout.prop(settings, "port")
        
        if not settings.is_running:
            layout.operator("render.start_server")
        else:
            layout.operator("render.stop_server")
            layout.label(text="Server is running...")

class StartServerOperator(bpy.types.Operator):
    bl_idname = "render.start_server"
    bl_label = "Start Server"
    
    _stop_server = False
    
    def handle_client(self, client_socket):
        try:
            # Receive file size
            file_size = int(client_socket.recv(1024).decode().strip())
            client_socket.send(b"READY")
            
            # Receive blend file
            temp_blend = tempfile.mktemp(suffix='.blend')
            received_size = 0
            
            with open(temp_blend, 'wb') as f:
                while received_size < file_size:
                    chunk = client_socket.recv(min(1024, file_size - received_size))
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)
            
            # Load the file
            bpy.ops.wm.open_mainfile(filepath=temp_blend)
            
            # Create temp directory for renders
            temp_dir = tempfile.mkdtemp()
            original_filepath = bpy.context.scene.render.filepath
            original_camera = bpy.context.scene.camera
            
            # Get list of all cameras
            cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
            render_results = {}
            
            # Render each camera
            for cam in cameras:
                try:
                    # Set current camera
                    bpy.context.scene.camera = cam
                    
                    # Set output path for this camera
                    output_path = os.path.join(temp_dir, f"{cam.name}.png")
                    bpy.context.scene.render.filepath = output_path
                    
                    # Render
                    bpy.ops.render.render(write_still=True)
                    
                    # Read the rendered image
                    with open(output_path, 'rb') as f:
                        image_data = f.read()
                    
                    render_results[cam.name] = image_data
                    
                except Exception as e:
                    render_results[cam.name] = str(e)
            
            # Restore original settings
            bpy.context.scene.render.filepath = original_filepath
            bpy.context.scene.camera = original_camera
            
            # Send results count
            client_socket.send(str(len(render_results)).encode() + b'\n')
            client_socket.recv(1024)  # Wait for acknowledgment
            
            # Send each result
            for cam_name, data in render_results.items():
                # Send camera name
                client_socket.send(cam_name.encode() + b'\n')
                client_socket.recv(1024)  # Wait for acknowledgment
                
                if isinstance(data, bytes):
                    # Send success status and image size
                    client_socket.send(b"SUCCESS\n" + str(len(data)).encode() + b'\n')
                    client_socket.recv(1024)  # Wait for acknowledgment
                    
                    # Send image data
                    client_socket.send(data)
                else:
                    # Send error status and message
                    client_socket.send(b"ERROR\n" + str(data).encode() + b'\n')
                
                client_socket.recv(1024)  # Wait for final acknowledgment
            
            # Clean up
            os.remove(temp_blend)
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
        except Exception as e:
            try:
                client_socket.send(str(e).encode())
            except:
                pass
        finally:
            client_socket.close()
    
    def execute(self, context):
        if not context.scene.render_server_settings.is_running:
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind(('0.0.0.0', context.scene.render_server_settings.port))
                server_socket.listen(1)  # Only allow 1 connection at a time
                context.scene.render_server_settings.is_running = True
                
                while not self._stop_server:
                    # Accept one client at a time
                    client_socket, _ = server_socket.accept()
                    self.handle_client(client_socket)
                    
            except Exception as e:
                self.report({'ERROR'}, f"Server error: {str(e)}")
            finally:
                server_socket.close()
                context.scene.render_server_settings.is_running = False
                
        return {'FINISHED'}

class StopServerOperator(bpy.types.Operator):
    bl_idname = "render.stop_server"
    bl_label = "Stop Server"
    
    def execute(self, context):
        StartServerOperator._stop_server = True
        context.scene.render_server_settings.is_running = False
        return {'FINISHED'}

# Registration
classes = (
    RenderServerSettings,
    RemoteRenderServerPanel,
    StartServerOperator,
    StopServerOperator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.render_server_settings = bpy.props.PointerProperty(type=RenderServerSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.render_server_settings

if __name__ == "__main__":
    register() 