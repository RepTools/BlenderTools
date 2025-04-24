import bpy
import os

# Get the output directory (same as blend file location)
output_dir = os.path.dirname(bpy.data.filepath)
if not output_dir:
    output_dir = os.path.expanduser("~")  # Fallback to home directory if blend file not saved

# Function to render a specific collection
def render_collection(collection_name):
    # Hide all collections first
    for coll in bpy.data.collections:
        if coll.name.startswith("Model"):
            # Set collection visibility to hidden
            layer_collection = find_layer_collection(bpy.context.view_layer.layer_collection, coll.name)
            if layer_collection:
                layer_collection.exclude = True
    
    # Show only the target collection
    layer_collection = find_layer_collection(bpy.context.view_layer.layer_collection, collection_name)
    if layer_collection:
        layer_collection.exclude = False
        
        # Set output path
        bpy.context.scene.render.filepath = os.path.join(output_dir, collection_name)
        
        # Render
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {collection_name}")
    else:
        print(f"Collection {collection_name} not found")

# Helper function to find a layer collection by name
def find_layer_collection(layer_collection, name):
    if layer_collection.name == name:
        return layer_collection
    
    for child in layer_collection.children:
        result = find_layer_collection(child, name)
        if result:
            return result
    
    return None

# Main execution
def main():
    # Ensure we're using Cycles or another renderer that supports collections
    bpy.context.scene.render.engine = 'CYCLES'
    
    # Render each Model collection
    for i in range(8):  # 0 through 7
        if i == 0:
            collection_name = "Model"
        else:
            collection_name = f"Model.{i:03d}"
        
        # Check if collection exists
        if collection_name in bpy.data.collections:
            render_collection(collection_name)
        else:
            print(f"Collection {collection_name} does not exist, skipping")

# Run the script
if __name__ == "__main__":
    main()
