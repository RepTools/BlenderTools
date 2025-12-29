import bpy
import os

# Define render configurations based on pr-2000.md
RENDER_CONFIGS = [
    {
        "image_name": "LegRoller.png",
        "include": ["LegRoller"],
        "holdout": ["Rack93", "15-005071 1168"]
    },
    {
        "image_name": "Shrouds93.png",
        "include": ["Shrouds93"],
        "holdout": ["Rack93", "15-005071 1168"]
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
        "holdout": ["Rack93"]
    },
    {
        "image_name": "CableMachine93withSmith.png",
        "include": ["CableMachine93"],
        "holdout": ["Rack93","SmithMachine93"]
    },
    {
        "image_name": "CableMachine80.png",
        "include": ["CableMachine80"],
        "holdout": ["Rack80"]
    },
    {
        "image_name": "CableMachine80withSmith.png",
        "include": ["CableMachine80"],
        "holdout": ["Rack80","SmithMachine80"]
    },
    {
        "image_name": "Rack93.png",
        "include": ["Rack93", "15-005071 1168", "WeightHorns80"],
        "holdout": []
    },
    {
        "image_name": "Rack80.png",
        "include": ["Rack80", "15-005056 1168", "WeightHorns80"],
        "holdout": []
    },
    {
        "image_name": "Dip.png",
        "include": ["Dip"],
        "holdout": ["Rack80", "15-005056 1168"]
    },
    {
        "image_name": "WeightHorns.png",
        "include": ["WeightHorns80"],
        "holdout": ["Rack80", "15-005056 1168"]
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

def get_view_layer_collection(collection, view_layer=None):
    """Get the view layer collection for a given collection.
    This is needed to set the exclude property."""
    if view_layer is None:
        view_layer = bpy.context.view_layer
    
    def find_layer_collection(layer_coll, target_coll):
        if layer_coll.collection == target_coll:
            return layer_coll
        for child in layer_coll.children:
            result = find_layer_collection(child, target_coll)
            if result:
                return result
        return None
    
    return find_layer_collection(view_layer.layer_collection, collection)


def set_collection_visibility(collection, visible):
    """Set collection visibility for viewport and render.
    Also recursively sets visibility on all objects in the collection."""
    if collection:
        # Set collection-level visibility (this is what controls rendering)
        collection.hide_viewport = not visible
        collection.hide_render = not visible  # Always match viewport visibility
        
        # Also set the view layer exclude property (the checkbox in outliner)
        # This is the most important one for hiding from renders!
        layer_coll = get_view_layer_collection(collection)
        if layer_coll:
            layer_coll.exclude = not visible
        
        # Also set visibility on all objects in the collection
        for obj in collection.objects:
            obj.hide_viewport = not visible
            obj.hide_render = not visible  # Always match viewport visibility
        
        # Recursively handle child collections
        for child_coll in collection.children:
            set_collection_visibility(child_coll, visible)


def get_object_collections(obj):
    """Get all collections that contain this object."""
    collections = []
    for coll in bpy.data.collections:
        if obj.name in coll.objects:
            collections.append(coll)
    return collections


def set_object_visibility(obj, visible):
    """Set object visibility for viewport and render.
    If making visible, also ensures parent collections are not excluded."""
    if obj:
        obj.hide_viewport = not visible
        obj.hide_render = not visible  # Always match viewport visibility
        
        # If we're making the object visible, ensure its parent collections are also visible
        # BUT only un-exclude the immediate parent collection, not all of them
        if visible:
            for coll in get_object_collections(obj):
                # Un-hide the collection but DON'T change other collections
                coll.hide_viewport = False
                coll.hide_render = False
                # Also un-exclude from view layer
                layer_coll = get_view_layer_collection(coll)
                if layer_coll:
                    layer_coll.exclude = False


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


def get_all_objects_in_collection(collection):
    """Recursively get ALL objects in a collection and all its child collections."""
    objects = []
    if not collection:
        return objects
    
    # Get direct objects
    for obj in collection.objects:
        objects.append(obj)
    
    # Recursively get objects from child collections
    for child_coll in collection.children:
        objects.extend(get_all_objects_in_collection(child_coll))
    
    return objects


def hide_all_in_collection(parent_collection, hide_parent=False):
    """Recursively hide ALL collections and objects within a parent collection.
    If hide_parent=True, also hides the parent collection itself."""
    if not parent_collection:
        return
    
    # Optionally hide the parent collection itself
    if hide_parent:
        set_collection_visibility(parent_collection, False)
        set_holdout_property(parent_collection, False)
    
    # Hide all direct child collections
    for coll in parent_collection.children:
        set_collection_visibility(coll, False)
        set_holdout_property(coll, False)
        # Recursively hide children (already handled by set_collection_visibility, but be thorough)
        hide_all_in_collection(coll, hide_parent=False)
    
    # Hide all direct objects in this collection
    for obj in parent_collection.objects:
        obj.hide_viewport = True
        obj.hide_render = True
        set_holdout_property(obj, False)
    
    # Also get ALL objects recursively and hide them (belt and suspenders approach)
    all_objects = get_all_objects_in_collection(parent_collection)
    for obj in all_objects:
        obj.hide_viewport = True
        obj.hide_render = True
        set_holdout_property(obj, False)


def setup_render_config(config):
    """Configure the scene for a specific render configuration."""
    include_items = config["include"]
    holdout_items = config["holdout"]
    
    # Get all items that should be visible (include + holdout)
    visible_items = set(include_items) | set(holdout_items)
    
    print(f"  Hiding all collections first...")
    
    # FIRST: Hide EVERYTHING in the Racks collection (all children, recursively)
    racks_collection = bpy.data.collections.get("Racks")
    if racks_collection:
        hide_all_in_collection(racks_collection)
    else:
        print(f"  Warning: 'Racks' collection not found!")
    
    # Also hide everything in the Model collection (including the collection itself)
    model_collection = bpy.data.collections.get("Model")
    if model_collection:
        # First, exclude the Model collection from the view layer
        model_layer_coll = get_view_layer_collection(model_collection)
        if model_layer_coll:
            model_layer_coll.exclude = True
            print(f"    Excluded Model collection from view layer")
        
        # Hide the collection itself
        model_collection.hide_viewport = True
        model_collection.hide_render = True
        
        # Hide all contents
        hide_all_in_collection(model_collection, hide_parent=True)
        
        # Explicitly hide all objects in Model collection
        all_model_objects = get_all_objects_in_collection(model_collection)
        for obj in all_model_objects:
            obj.hide_viewport = True
            obj.hide_render = True
            set_holdout_property(obj, False)
            print(f"    Hidden model: {obj.name}")
    
    # Backup: Hide all rack collections by name from predefined list
    for coll_name in ALL_RACK_COLLECTIONS:
        collection = get_collection(coll_name)
        if collection:
            set_collection_visibility(collection, False)
            set_holdout_property(collection, False)
    
    # Backup: Hide all models by name from predefined list
    for model_name in ALL_MODELS:
        obj = bpy.data.objects.get(model_name)  # Direct lookup
        if obj:
            obj.hide_viewport = True
            obj.hide_render = True
            set_holdout_property(obj, False)
            print(f"    Hidden model (by name): {model_name}")
        else:
            print(f"    Warning: Model '{model_name}' not found in bpy.data.objects")
    
    print(f"  Now showing only: {', '.join(visible_items)}")
    
    # SECOND: Show ONLY items that are explicitly in include list
    for item_name in include_items:
        # Try as collection first
        collection = get_collection(item_name)
        if collection:
            set_collection_visibility(collection, True)
            set_holdout_property(collection, False)  # Make sure holdout is off for included items
            print(f"    Showing collection: {item_name}")
        else:
            # Try as object
            obj = get_object(item_name)
            if obj:
                set_object_visibility(obj, True)
                set_holdout_property(obj, False)
                print(f"    Showing object: {item_name}")
            else:
                print(f"  Warning: Item '{item_name}' not found (neither collection nor object)")
    
    # THIRD: Show holdout items and enable holdout on them
    for item_name in holdout_items:
        # Try as collection first
        collection = get_collection(item_name)
        if collection:
            set_collection_visibility(collection, True)
            set_holdout_property(collection, True)
            print(f"    Showing as holdout: {item_name}")
        else:
            # Try as object
            obj = get_object(item_name)
            if obj:
                set_object_visibility(obj, True)
                set_holdout_property(obj, True)
                print(f"    Showing object as holdout: {item_name}")
            else:
                print(f"  Warning: Holdout item '{item_name}' not found (neither collection nor object)")
    
    # FOURTH: Final verification - hide any models NOT in the include list
    # This ensures models stay hidden even if their parent collection was un-excluded
    print(f"  Final verification - ensuring unwanted models are hidden...")
    for model_name in ALL_MODELS:
        if model_name not in visible_items:
            obj = bpy.data.objects.get(model_name)
            if obj:
                obj.hide_viewport = True
                obj.hide_render = True
                print(f"    Force hidden: {model_name}")


def render_all_configs(output_path):
    """Render all configurations defined in RENDER_CONFIGS."""
    scene = bpy.context.scene
    render = scene.render
    
    # Make sure output format is PNG with alpha (transparency)
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'  # Include alpha channel for transparency
    
    # Enable film transparency so holdout objects create transparent areas
    scene.render.film_transparent = True
    
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

