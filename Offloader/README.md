# Blender Remote Render

This project consists of two Blender addons that enable distributed rendering between two computers:
1. A client addon that sends blend files to a render server
2. A server addon that receives blend files and performs the rendering

## Installation

### Server Computer
1. Zip the contents of the `blender_render_server` folder
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the zip file
4. Enable the addon by checking the box next to "Render: Remote Render Server"

### Client Computer
1. Zip the contents of the `blender_render_client` folder
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the zip file
4. Enable the addon by checking the box next to "Render: Remote Render Client"

## Usage

### Server Setup
1. Open Blender on the server computer
2. In the 3D Viewport's sidebar (press N if not visible), find the "Remote Render Server" tab
3. Set the desired port number (default is 5000)
4. Click "Start Server"
5. The server will now listen for incoming render requests

### Client Usage
1. Open your blend file in Blender on the client computer
2. In the 3D Viewport's sidebar, find the "Remote Render" tab
3. Enter the server's IP address and port number
4. Click "Render with Server"
5. Wait for the render to complete

## Notes
- Ensure both computers are on the same network or can reach each other
- The server computer must have sufficient RAM to handle the blend files
- Firewall settings may need to be adjusted to allow the connection
- The server can handle multiple clients sequentially

## Requirements
- Blender 4.0 or newer on both computers
- Network connectivity between client and server
- Sufficient storage space for temporary files 