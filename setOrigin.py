import bpy
import math

# get all objects in collection "Model"
collection = bpy.data.collections.get("Model")



#For all opbjects in collection, set origin to geometry
for obj in collection.objects:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    print("Origin set to geometry for", obj.name, "successfully!")
