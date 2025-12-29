import bpy
import os

# Output directory
output_path = r'C:\Users\AJFrio\OneDrive - Rep Fitness\Desktop\NewRackRenders'

# Ensure output directory exists
os.makedirs(output_path, exist_ok=True)

# Define all collections
ALL_COLLECTIONS = [
    'WH93', 'WH80', 'SS', 'FDS', '6ATH93', '6ATH80', '6ARE93', '6ARE80',
    'MGPB93', 'MGPB80', 'CATH', 'CARE', 'MFFF', 'FSJ', 'FSJR'
]

# Define render configurations
# Format: (image_name, [list of visible collections])
RENDER_CONFIGS = [
    ('REP-ATH-80', ['6ATH80', 'MGPB80', 'WH80', 'SS', 'FSJ']),
    ('REP-ATH-93', ['6ATH93', 'MGPB93', 'WH93', 'SS', 'FSJ']),
    ('REP-ARS2-80', ['6ARE80', 'MGPB80', 'WH80', 'FDS', 'FSJ']),
    ('REP-ARS2-93', ['6ARE93', 'MGPB93', 'WH93', 'FDS', 'FSJ']),
    ('REP-ATH-C-93', ['CATH', 'WH93', 'FSJR']),
    ('REP-ARS2-C-93', ['CARE', 'MFFF', 'FSJR']),
]

# Camera names
CAMERA_NAMES = ['Camera', 'Camera.001', 'Camera.002']


def get_view_layer_collection(collection):
    """Get the view layer collection for a given collection."""
    def find_layer_collection(layer_coll, target_coll):
        if layer_coll.collection == target_coll:
            return layer_coll
        for child in layer_coll.children:
            result = find_layer_collection(child, target_coll)
            if result:
                return result
        return None
    
    return find_layer_collection(bpy.context.view_layer.layer_collection, collection)


def set_collection_visibility(collection, visible):
    """Set collection visibility for viewport and render."""
    if collection:
        # Set collection-level visibility
        collection.hide_viewport = not visible
        collection.hide_render = not visible
        
        # Set the view layer exclude property (important for rendering)
        layer_coll = get_view_layer_collection(collection)
        if layer_coll:
            layer_coll.exclude = not visible
        
        # Set visibility on all objects in the collection
        for obj in collection.objects:
            obj.hide_viewport = not visible
            obj.hide_render = not visible
        
        # Recursively handle child collections
        for child_coll in collection.children:
            set_collection_visibility(child_coll, visible)


def setup_render_config(visible_collections):
    """Hide all collections, then show only the specified ones."""
    # First, hide all collections
    for coll_name in ALL_COLLECTIONS:
        collection = bpy.data.collections.get(coll_name)
        if collection:
            set_collection_visibility(collection, False)
    
    # Then show only the collections specified for this config
    for coll_name in visible_collections:
        collection = bpy.data.collections.get(coll_name)
        if collection:
            set_collection_visibility(collection, True)
            print(f"  Showing collection: {coll_name}")
        else:
            print(f"  Warning: Collection '{coll_name}' not found!")


def get_cameras():
    """Get all cameras from the Cameras collection."""
    cameras = []
    cameras_collection = bpy.data.collections.get('Cameras')
    
    if cameras_collection:
        for obj in cameras_collection.objects:
            if obj.type == 'CAMERA':
                cameras.append(obj)
    else:
        # Fallback: search all objects for cameras with matching names
        print("  Warning: 'Cameras' collection not found, searching all objects...")
        for cam_name in CAMERA_NAMES:
            cam_obj = bpy.data.objects.get(cam_name)
            if cam_obj and cam_obj.type == 'CAMERA':
                cameras.append(cam_obj)
    
    return cameras


def show_all_collections():
    """Make all collections visible in viewport and render."""
    print("Making all collections visible...")
    
    # Show all defined collections
    for coll_name in ALL_COLLECTIONS:
        collection = bpy.data.collections.get(coll_name)
        if collection:
            set_collection_visibility(collection, True)
            print(f"  Showing collection: {coll_name}")
    
    # Also show all other collections in the scene
    for collection in bpy.data.collections:
        if collection.name not in ALL_COLLECTIONS and collection.name != 'Cameras':
            set_collection_visibility(collection, True)
            print(f"  Showing collection: {collection.name}")
    
    # Make sure all objects are visible too
    for obj in bpy.data.objects:
        obj.hide_viewport = False
        obj.hide_render = False
    
    print("All collections and objects are now visible!")


def render_all_configs():
    """Render all configurations from all cameras."""
    scene = bpy.context.scene
    render = scene.render
    
    # Store original camera
    original_camera = scene.camera
    
    # Set render settings
    render.image_settings.file_format = 'PNG'
    
    # Get all cameras
    cameras = get_cameras()
    if not cameras:
        print("ERROR: No cameras found!")
        return
    
    print(f"Found {len(cameras)} cameras")
    
    # Process each configuration
    for config_name, visible_collections in RENDER_CONFIGS:
        print(f"\nProcessing configuration: {config_name}")
        print(f"  Visible collections: {', '.join(visible_collections)}")
        
        # Setup collection visibility for this config
        setup_render_config(visible_collections)
        
        # Render from each camera
        for cam_idx, camera in enumerate(cameras):
            # Set the active camera
            scene.camera = camera
            
            # Determine camera suffix
            if cam_idx == 0:
                camera_suffix = ""
            else:
                camera_suffix = f"_{cam_idx}"
            
            # Set output path
            output_filename = f"{config_name}{camera_suffix}.png"
            render.filepath = os.path.join(output_path, output_filename)
            
            # Render
            print(f"  Rendering from camera: {camera.name} -> {output_filename}")
            bpy.ops.render.render(write_still=True)
    
    # Restore original camera
    scene.camera = original_camera
    
    print(f"\nAll renders complete! Output saved to: {output_path}")


# Run the script
if __name__ == "__main__":
    render_all_configs()

