import bpy
import os

# Define render configurations based on pr-2000.md
RENDER_CONFIGS = [
    {
        "image_name": "LegRoller.png",
        "include": ["LegRoller"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "Shrouds93.png",
        "include": ["Shrouds93"],
        "holdout": []
    },
    {
        "image_name": "Shrouds80.png",
        "include": ["Shrouds80"],
        "holdout": []
    },
    {
        "image_name": "SmithMachine93.png",
        "include": ["SmithMachine93"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "SmithMachine80.png",
        "include": ["SmithMachine80"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "Jcups1.png",
        "include": ["Jcups1"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "Jcups2.png",
        "include": ["Jcups2"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "StrapSafeties.png",
        "include": ["StrapSafeties"],
        "holdout": []
    },
    {
        "image_name": "FlipDownSafeties.png",
        "include": ["FlipDownSafeties"],
        "holdout": []
    },
    {
        "image_name": "CableMachine93.png",
        "include": ["CableMachine93"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "CableMachine80.png",
        "include": ["CableMachine80"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "Rack93.png",
        "include": ["Rack93", "15-005071 1168"],
        "holdout": []
    },
    {
        "image_name": "Rack80.png",
        "include": ["Rack80", "15-005056 1168"],
        "holdout": []
    }
]

# All collections in the Racks folder
ALL_RACK_COLLECTIONS = [
    "Shrouds80", "Shrouds93", "SmithMachine80", "SmithMachine93",
    "Jcups1", "Jcups2", "StrapSafeties", "FlipDownSafeties",
    "CableMachine80", "CableMachine93", "Rack80", "Rack93",
    "LegRoller", "Dip"
]

# All models in the Model folder
ALL_MODELS = [
    "15-005056 1168",  # 80 in uprights model
    "15-005071 1168"   # 93 in uprights model
]


def get_collection(name):
    """Get a collection by name, searching in the Racks collection."""
    # First check if it's a direct child of Racks collection
    racks_collection = bpy.data.collections.get("Racks")
    if racks_collection:
        for coll in racks_collection.children:
            if coll.name == name:
                return coll
    # Also check top-level collections
    return bpy.data.collections.get(name)


def get_object(name):
    """Get an object by name. Models are in the Model collection."""
    # First try direct lookup
    obj = bpy.data.objects.get(name)
    if obj:
        return obj
    
    # Also check in Model collection
    model_collection = bpy.data.collections.get("Model")
    if model_collection:
        for obj in model_collection.objects:
            if obj.name == name:
                return obj
    
    return None

def find_layer_collection(layer_collection, target_collection):
    """Recursively find a layer collection that matches the target collection."""
    if layer_collection.collection == target_collection:
        return layer_collection
    for child in layer_collection.children:
        result = find_layer_collection(child, target_collection)
        if result:
            return result
    return None


def set_collection_visibility(collection, visible, render_visible=True):
    """Set collection visibility for viewport and render.
    Also recursively sets visibility on all objects in the collection.
    Handles both collection properties and view layer instances."""
    if collection:
        # Set collection-level visibility
        collection.hide_viewport = not visible
        collection.hide_render = not render_visible
        
        # Also set visibility in view layers (important for rendering)
        for view_layer in bpy.context.scene.view_layers:
            layer_collection = find_layer_collection(view_layer.layer_collection, collection)
            if layer_collection:
                layer_collection.hide_viewport = not visible
                layer_collection.hide_render = not render_visible
        
        # Also set visibility on all objects in the collection
        for obj in collection.objects:
            obj.hide_viewport = not visible
            obj.hide_render = not render_visible
        
        # Recursively handle child collections
        for child_coll in collection.children:
            set_collection_visibility(child_coll, visible, render_visible)


def set_object_visibility(obj, visible, render_visible=True):
    """Set object visibility for viewport and render."""
    if obj:
        obj.hide_viewport = not visible
        obj.hide_render = not render_visible


def set_holdout_property(collection_or_object, holdout_enabled):
    """Set holdout property on a collection or object.
    Holdout is set on individual objects, not collections.
    The is_holdout property is directly on the object."""
    def set_obj_holdout(obj):
        """Set holdout on a single object."""
        if obj.type == 'MESH':
            # Set holdout directly on the object
            if hasattr(obj, 'is_holdout'):
                obj.is_holdout = holdout_enabled
    
    if isinstance(collection_or_object, bpy.types.Collection):
        # Set holdout on all objects in the collection
        for obj in collection_or_object.objects:
            set_obj_holdout(obj)
        # Also check child collections
        for child_coll in collection_or_object.children:
            set_holdout_property(child_coll, holdout_enabled)
    elif isinstance(collection_or_object, bpy.types.Object):
        set_obj_holdout(collection_or_object)


def setup_render_config(config):
    """Configure the scene for a specific render configuration."""
    include_items = config["include"]
    holdout_items = config["holdout"]
    
    # Get all items that should be visible (include + holdout)
    visible_items = set(include_items) | set(holdout_items)
    
    # First, hide ALL rack collections and their objects
    racks_collection = bpy.data.collections.get("Racks")
    if racks_collection:
        for coll in racks_collection.children:
            should_be_visible = coll.name in visible_items
            set_collection_visibility(coll, should_be_visible)
            # Reset holdout for all collections
            set_holdout_property(coll, False)
    
    # Hide all rack collections by name (backup method)
    for coll_name in ALL_RACK_COLLECTIONS:
        collection = get_collection(coll_name)
        if collection:
            should_be_visible = coll_name in visible_items
            set_collection_visibility(collection, should_be_visible)
            # Reset holdout for all collections
            set_holdout_property(collection, False)
    
    # Hide all models first
    for model_name in ALL_MODELS:
        obj = get_object(model_name)
        if obj:
            set_object_visibility(obj, model_name in visible_items)
            # Reset holdout for all models
            set_holdout_property(obj, False)
        else:
            print(f"  Warning: Model '{model_name}' not found")
    
    # Set visibility for included items (make sure they're visible)
    for item_name in include_items:
        # Try as collection first
        collection = get_collection(item_name)
        if collection:
            set_collection_visibility(collection, True)
        else:
            # Try as object
            obj = get_object(item_name)
            if obj:
                set_object_visibility(obj, True)
            else:
                print(f"  Warning: Item '{item_name}' not found (neither collection nor object)")
    
    # Set holdout for holdout items
    for item_name in holdout_items:
        # Try as collection first
        collection = get_collection(item_name)
        if collection:
            set_collection_visibility(collection, True)
            set_holdout_property(collection, True)
        else:
            # Try as object
            obj = get_object(item_name)
            if obj:
                set_object_visibility(obj, True)
                set_holdout_property(obj, True)
            else:
                print(f"  Warning: Holdout item '{item_name}' not found (neither collection nor object)")


def render_all_configs(output_path):
    """Render all configurations defined in RENDER_CONFIGS."""
    scene = bpy.context.scene
    render = scene.render
    
    # Make sure output format is PNG
    render.image_settings.file_format = 'PNG'
    
    # Ensure output path exists
    os.makedirs(output_path, exist_ok=True)
    
    # Render each configuration
    for config in RENDER_CONFIGS:
        print(f"\nSetting up render for: {config['image_name']}")
        print(f"  Include: {', '.join(config['include'])}")
        print(f"  Holdout: {', '.join(config['holdout']) if config['holdout'] else 'None'}")
        
        # Setup the scene for this configuration
        setup_render_config(config)
        
        # Set the output path for this image
        image_path = os.path.join(output_path, config['image_name'])
        render.filepath = image_path
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        print(f"  Rendered: {image_path}")
    
    print("\nAll renders complete!")


# Main execution
if __name__ == "__main__":
    # Set your output path here
    output_path = 'C:/Users/AJFrio/OneDrive - Rep Fitness/Desktop/PR2000Renders'
    
    render_all_configs(output_path)

