import bpy
from mathutils import Vector
from math import radians
import os
import sqlite3
import bpy

col = "Model"

bolts = ['10-0030', '10-0025', '10-0475', '10-0476', '10-0232', '10-0550', '10-0208', '10-0133', '10-0620', '10-0033', '10-0341', '10-0620', '10-0314', '10-0146', '10-0428', '10-010035', '10-009016']
washers_nuts = ['10-0026', '10-0310', '10-0315', '10-0104', '10-0078', '10-0020', '10-0037', '10-0421', '10-0233', '10-0164', '10-0072', '10-0024', '10-0023', '10-0460']
stupid_parts = ['10-0006'] #bolts or high poly parts that I need to make smaller, but Im just deleting for rn since no one will notice
rectangles = ['15-1103', '15-0384']
cylinders = ['15-1068', '15-1077', '15-1078', '10-0166', '10-0526', '15-1044', '20-0055', '15-0839', '20-0056', '15-0548', '15-1213', '15-1211', '15-1212', '15-1247', '15-0298', '10-0796']
pulleys = ['10-0017', '10-0371', '10-0277', ]
delete_list = ['10-0360', '10-0370', '10-0171', '15-0369']

washers_nuts.extend(stupid_parts)

collection = bpy.data.collections.get(col)

debug_mode = True

def debug(text):
    if debug_mode:
        print(text)


def get_bounding_box(obj):
    local_bbox_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(coord.x for coord in local_bbox_coords)
    max_x = max(coord.x for coord in local_bbox_coords)
    min_y = min(coord.y for coord in local_bbox_coords)
    max_y = max(coord.y for coord in local_bbox_coords)
    min_z = min(coord.z for coord in local_bbox_coords)
    max_z = max(coord.z for coord in local_bbox_coords)
    return min_x, max_x, min_y, max_y, min_z, max_z

def make_hardware(height, depth, position, rotation, name, id):
    debug(f"Creating {name}.{id} ####################")
    # Create a circle mesh (hexagon) with 6 vertices
    bpy.ops.mesh.primitive_circle_add(
        vertices=6,
        radius=height/2,  # radius is half the diameter (height)
        fill_type='NGON',
        location=position
    )
    
    # Get the active object (our newly created hexagon)
    obj = bpy.context.active_object
    
    # Extrude the face in both directions along Z axis
    bpy.ops.object.mode_set(mode='EDIT')
    # Extrude in positive Z direction
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, depth/2)}
    )
    # Return to original face and extrude in negative Z direction
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, -depth/2)}
    )
    bpy.ops.object.mode_set(mode='OBJECT')

    # Convert rotation from degrees to radians
    rotation_rad = tuple(radians(angle) for angle in rotation)
    obj.rotation_euler = rotation_rad
    obj.name = f"{name}.{id}"
    debug(f"Created {obj.name} _#_#_#__#_#_#__#_#_#_#_#_#_#_#__#")

    return obj

def decimate_collection(obj, angle_limit: float = 0.11):
    if collection:
        # Ensure the object is a mesh
        if obj.type == 'MESH':
            # Set the active object
            bpy.context.view_layer.objects.active = obj
            # Create a decimate modifier
            decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
            # Set the decimate modifier to planar
            decimate_modifier.decimate_type = 'DISSOLVE'
            # Set the angle limit
            decimate_modifier.angle_limit = angle_limit
            # Apply the modifier
            bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)
            debug(f"Decimated {obj.name}")
    else:
        debug(f"Collection '{col}' not found when decimating.")

def apply_all_modifiers(obj):

    if collection:
        # Ensure the object is a mesh
        if obj.type == 'MESH':
            # Set the object as active
            bpy.context.view_layer.objects.active = obj
            # Apply all modifiers
            for modifier in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
    else:
        debug(f"Collection '{col}' not found when applying modifiers.")

def swap_rectangles(obj):
    '''
    Automatically creates a primative replica of a cuboid. Used for weight plates, frame type things
    '''
    if obj.name.split(" ")[0] in rectangles:
        debug(f"Swapping {obj.name} -----------------")
        delete_list.append(obj.name.split(" ")[0])
        name = obj.name.split(" ")[0]
        id = obj.name.split(" ")[1]
        min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(obj)
        x_size = max_x - min_x
        y_size = max_y - min_y
        z_size = max_z - min_z

        bpy.ops.mesh.primitive_cube_add(
            size=x_size,
            location=(min_x + (x_size/2), min_y + (y_size/2), min_z + (z_size/2))
        )

        cube = bpy.context.active_object
        cube.dimensions = (x_size, y_size, z_size)
        cube.name = f"{name}.{id}"
        debug(f"Created {cube.name} _#_#_#__#_#_#__#_#_#_#_#_#_#_#__#")

def swap_cylinders(obj):

    '''
    Automatically creates a primative replica of a cylinder. Used for guide rods, handles, etc. Largest bounding box dimension is the length
    '''
    if collection:
        if obj.name.split(" ")[0] in cylinders:
            debug(f"Swapping cylinder {obj.name} -----------------")
            delete_list.append(obj.name.split(" ")[0])
            name = obj.name.split(" ")[0]
            id = obj.name.split(" ")[1]
            min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(obj)
            debug(f"X bounds: {min_x:.4f} to {max_x:.4f}")
            debug(f"Y bounds: {min_y:.4f} to {max_y:.4f}")
            debug(f"Z bounds: {min_z:.4f} to {max_z:.4f}")

            x_size = max_x - min_x
            y_size = max_y - min_y
            z_size = max_z - min_z

            length = max(x_size, y_size, z_size)
            diameter = min(x_size, y_size, z_size)

            if length == x_size:
                rotate = (0, 90, 0)
            elif length == y_size:
                rotate = (90, 0, 0)
            elif length == z_size:
                rotate = (0, 0, 0)

            bpy.ops.mesh.primitive_circle_add(
                vertices=25,
                radius=diameter/2,  # radius is half the diameter (height)
                fill_type='NGON',
                location=(min_x + (x_size/2), min_y + (y_size/2), min_z + (z_size/2))
            )

            obj = bpy.context.active_object

            # Extrude the face in both directions along Z axis
            bpy.ops.object.mode_set(mode='EDIT')
            # Extrude in positive Z direction
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": (0, 0, length/2)}
            )
            # Return to original face and extrude in negative Z direction
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": (0, 0, -length/2)}
            )
            bpy.ops.object.mode_set(mode='OBJECT')

            # Convert rotation from degrees to radians
            rotation_rad = tuple(radians(angle) for angle in rotate)
            obj.rotation_euler = rotation_rad
            obj.name = f"{name}.{id}"
            debug(f"Created {obj.name} _#_#_#__#_#_#__#_#_#_#_#_#_#_#__#")


        else:
            debug(f"SKIPPING {obj.name}: Not a cylinder")

def swap_pulleys(obj):
    '''
    Automatically creates a primative replica of a cylinder. Used for pulleys. Inverse of cylinder, Largest bounding box dimension is the diameter
    '''
    if obj.name.split(" ")[0] in pulleys:
        debug(f"Swapping cylinder {obj.name} -----------------")
        delete_list.append(obj.name.split(" ")[0])
        name = obj.name.split(" ")[0]
        id = obj.name.split(" ")[1]
        min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(obj)
        debug(f"X bounds: {min_x:.4f} to {max_x:.4f}")
        debug(f"Y bounds: {min_y:.4f} to {max_y:.4f}")
        debug(f"Z bounds: {min_z:.4f} to {max_z:.4f}")

        x_size = max_x - min_x
        y_size = max_y - min_y
        z_size = max_z - min_z

        length = min(x_size, y_size, z_size)
        diameter = max(x_size, y_size, z_size)

        if length == x_size:
            rotate = (0, 90, 0)
        elif length == y_size:
            rotate = (90, 0, 0)
        elif length == z_size:
            rotate = (0, 0, 0)

        bpy.ops.mesh.primitive_circle_add(
            vertices=25,
            radius=diameter/2,  # radius is half the diameter (height)
            fill_type='NGON',
            location=(min_x + (x_size/2), min_y + (y_size/2), min_z + (z_size/2))
        )

        obj = bpy.context.active_object

        # Extrude the face in both directions along Z axis
        bpy.ops.object.mode_set(mode='EDIT')
        # Extrude in positive Z direction
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, length/2)}
        )
        # Return to original face and extrude in negative Z direction
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, -length/2)}
        )
        bpy.ops.object.mode_set(mode='OBJECT')

        # Convert rotation from degrees to radians
        rotation_rad = tuple(radians(angle) for angle in rotate)
        obj.rotation_euler = rotation_rad
        obj.name = f"{name}.{id}"
        debug(f"Created {obj.name} _#_#_#__#_#_#__#_#_#_#_#_#_#_#__#")


    else:
        debug(f"SKIPPING {obj.name}: Not a pulley")

def swap_bolts(obj):
    try:
        name = obj.name.split(" ")[0]
        id = obj.name.split(" ")[1]
        if name in bolts:
                debug(f"Swapping {obj.name} -----------------")
                delete_list.append(obj.name.split(" ")[0])
                # Get local bounding box coordinates
                min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(obj)

                x_size = max_x - min_x
                y_size = max_y - min_y
                z_size = max_z - min_z
                rotate = (0, 0, 0)

                depth = x_size
                rotate = (0, 90, 0)
                if y_size > x_size:
                    depth = y_size
                    rotate = (90, 0, 0)
                elif z_size > x_size:
                    depth = z_size
                    rotate = (0, 0, 0)

                height = x_size
                if y_size < x_size and y_size < z_size:
                    height = y_size
                elif z_size < x_size and z_size < y_size:
                    height = z_size

                debug(f"Object: {obj.name}")
                debug(f"X bounds: {min_x:.4f} to {max_x:.4f}")
                debug(f"Y bounds: {min_y:.4f} to {max_y:.4f}")
                debug(f"Z bounds: {min_z:.4f} to {max_z:.4f}")
                debug(f"X size: {x_size:.4f}")
                debug(f"Y size: {y_size:.4f}")
                debug(f"Z size: {z_size:.4f}")

                origin = obj.location
                '''obj.select_set(True)
                bpy.ops.object.delete()'''

                make_hardware(height, depth, origin, rotate, name, id)
        else:
            debug(f"SKIPPING {obj.name}: Not a bolt")
    except:
        debug(f"SKIPPING {obj.name}: Not formated <name> <id>")

def remove_washers_nuts(obj):
    if obj.name.split(" ")[0] in washers_nuts:
        debug(f"Deleting {obj.name}")
        obj.select_set(True)
        bpy.ops.object.delete()

def remove_delete_list(obj):
    if obj.name.split(" ")[0] in delete_list:
        debug(f"Deleting {obj.name}")
        obj.select_set(True)
        bpy.ops.object.delete()
    else:
        debug(f"SKIPPING {obj.name}: Not in delete list")

def rename_objects(obj):
    try:
        name = obj.name.split(".")[0]
        id = obj.name.split(".")[1]
        obj.name = f"{name} {id}"
        debug(f"Renaming {obj.name} to {name} {id}")
    except:
        debug(f"{obj.name}: Already formmated")

def decimate():
    # First pass - remove objects we don't want to process
    debug(f"First pass - remove objects we don't want to process")
    for obj in collection.objects:  # Create a copy of the list to iterate
        remove_washers_nuts(obj)

    # Second pass - process remaining objects
    debug(f"Second pass - process remaining objects")
    for obj in collection.objects:  # Create a copy of the list to iterate
        decimate_collection(obj)
        apply_all_modifiers(obj)
        swap_rectangles(obj)
        swap_cylinders(obj)
        swap_pulleys(obj)
        swap_bolts(obj)
        


    # Final pass - cleanup
    debug(f"Final pass - cleanup")
    for obj in collection.objects:  # Create a copy of the list to iterate
        remove_delete_list(obj)
    for obj in collection.objects:
        rename_objects(obj)

decimate()