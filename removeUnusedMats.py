import bpy

def remove_unused_material_slots(collection_name='WorkBench'):
    # Retrieve the specified collection
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        print(f"Collection '{collection_name}' not found.")
        return

    # Store the original active object and selection
    original_active = bpy.context.view_layer.objects.active
    original_selection = bpy.context.selected_objects.copy()

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Iterate through all objects in the collection
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue  # Skip non-mesh objects

        # Set the object as active and selected
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Remove unused material slots
        bpy.ops.object.material_slot_remove_unused()
        print(f"Removed unused material slots from '{obj.name}'.")

        # Deselect the object
        obj.select_set(False)

    # Restore original active object and selection
    bpy.context.view_layer.objects.active = original_active
    for obj in original_selection:
        obj.select_set(True)

    print("Unused material slots removal complete.")

if __name__ == "__main__":
    remove_unused_material_slots()
