bl_info = {
    "name": "Remote Render Server",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 0, 0),
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
import threading
import time
from bpy.app.handlers import persistent

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

class ClientHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.daemon = True

    def run(self):
        print("ClientHandler started")
        try:
            # Receive file size
            file_size = int(self.client_socket.recv(1024).decode().strip())
            self.client_socket.send(b"READY")
            
            # Receive blend file
            temp_blend = tempfile.mktemp(suffix='.blend')
            received_size = 0
            
            with open(temp_blend, 'wb') as f:
                while received_size < file_size:
                    chunk = self.client_socket.recv(min(1024, file_size - received_size))
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)
            
            # Queue the file for processing
            bpy.app.timers.register(
                lambda: process_blend_file(temp_blend, self.client_socket),
                first_interval=0.1
            )
            
        except Exception as e:
            try:
                self.client_socket.send(str(e).encode())
                self.client_socket.close()
            except:
                pass

def process_blend_file(temp_blend, client_socket):
    try:
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
    return None

class StartServerOperator(bpy.types.Operator):
    bl_idname = "render.start_server"
    bl_label = "Start Server"
    
    _timer = None
    _server_socket = None
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            if not context.scene.render_server_settings.is_running:
                self.cancel(context)
                return {'CANCELLED'}
            
            try:
                # Non-blocking accept
                self._server_socket.settimeout(0)
                try:
                    client_socket, _ = self._server_socket.accept()
                    handler = ClientHandler(client_socket)
                    handler.start()
                except socket.error:
                    pass  # No connection available
            except Exception as e:
                print(f"Server error: {str(e)}")
                self.cancel(context)
                return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        if not context.scene.render_server_settings.is_running:
            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.bind(('0.0.0.0', context.scene.render_server_settings.port))
                self._server_socket.listen(1)
                print("Server started")

                context.scene.render_server_settings.is_running = True
                
                wm = context.window_manager
                self._timer = wm.event_timer_add(0.1, window=context.window)
                wm.modal_handler_add(self)
                
                return {'RUNNING_MODAL'}
            
            except Exception as e:
                self.report({'ERROR'}, f"Failed to start server: {str(e)}")
                print(f"Failed to start server: {str(e)}")
                return {'CANCELLED'}
        
        return {'CANCELLED'}
    
    def cancel(self, context):
        if self._timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
        
        if self._server_socket is not None:
            self._server_socket.close()
        
        context.scene.render_server_settings.is_running = False

class StopServerOperator(bpy.types.Operator):
    bl_idname = "render.stop_server"
    bl_label = "Stop Server"
    
    def execute(self, context):
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