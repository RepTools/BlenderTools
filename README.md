## DBPaintV2 (Plugin)
Used to color the objects in a blender scene. Uses a prebuild color map from obj name to specific color. Only work in the Template.blend file. Pulls object-color data from sqlite database in sharepoint

## Rename (Plugin)
Renames files in a folder exported from Solidworks to reduce file name length and ensure paint plugin maps properly

## perCamRender 
Renders the scene from all cameras in the scene

## Offloader (Plugin)
(Need to Fix)
Renders all cameras on a sperate machine running the server. Sent from the client. Returns all images

## Update DB (Plugin)
Updates the sqlite database in sharepoint with an updated color-object map

## Set Origin
Sets the origin of each object to the center of its bounding box

## Decimate
Whole bunch of different algorithms and processes to reduce the amount of vertices in the scene 

## Adjust Lighting (Plugin)
Adjusts all lighting of the scene in specific increaments

## Plane Builder (Plugin)
Creates a plane with dimensions converted from feet to Blender units. Accessible from the sidebar in the 3D View

Decimate lists need to get moved to the paint.db, add a plugin to add to decimate, start decimate