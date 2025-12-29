import bpy
import sys
import sqlite3
import os
import argparse

def find_db_path():
    """Find the database path using the same logic as dbpaintv2.py"""
    # First try the current format
    end = 'OneDrive - Rep Fitness/Documents - Product and Engineering/Internal Docs/ID Team/paint.db'
    start = os.path.dirname(os.path.realpath(__file__))
    start = start.split('\\')
    first = '\\'.join(start[:3])
    path = first + '\\' + end
    
    # Check if the file exists
    if os.path.exists(path):
        return path
    
    # If not found, try alternative path format
    alt_end = 'Rep Fitness\\Product and Engineering - Documents\\Internal Docs\\ID Team\\paint.db'
    alt_path = first + '\\' + alt_end
    
    # Check if alternative path exists
    if os.path.exists(alt_path):
        return alt_path
    
    # Return the original path as fallback
    return path

def apply_colors_to_collection(collection, dbpath, color_name, paint_type='lowq'):
    """Apply colors to all objects in a collection and its sub-collections"""
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    map = {'lowq': 1, 'highq': 2}
    
    try:
        # Clear existing materials and apply new ones to objects in this collection
        for obj in collection.objects:
            obj.data.materials.clear()
            
            name = obj.name.split(" ")[0]
            index = cursor.execute("SELECT * FROM obj_color_map WHERE name = ?", (name,)).fetchone()
            
            if index is not None:
                index = index[map[paint_type]]
                
                try:
                    if index == 'UC':
                        color = cursor.execute("SELECT * FROM color_indices WHERE color = ?", (color_name,)).fetchone()
                        if color is None or len(color) < 3:
                            obj.data.materials.append(bpy.data.materials[0])
                        else:
                            material_index = color[1] if paint_type == 'lowq' else color[2]
                            obj.data.materials.append(bpy.data.materials[material_index])
                    else:
                        obj.data.materials.append(bpy.data.materials[index])
                except:
                    obj.data.materials.append(bpy.data.materials[0])
            else:
                # If no mapping found in database, set to material index 0
                obj.data.materials.append(bpy.data.materials[0])
        
        # Recursively apply to sub-collections
        for sub_collection in collection.children:
            apply_colors_to_collection(sub_collection, dbpath, color_name, paint_type)
            
    finally:
        conn.close()

def get_all_collections_recursive(collection):
    """Get all collections including sub-collections"""
    collections = [collection]
    for sub_collection in collection.children:
        collections.extend(get_all_collections_recursive(sub_collection))
    return collections

def parse_arguments():
    """Parse command line arguments"""
    # Blender passes arguments after '--'
    argv = sys.argv
    if '--' not in argv:
        argv = []
    else:
        argv = argv[argv.index('--') + 1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-file', required=True, help='Path to base .blend file')
    parser.add_argument('--component-file', required=True, help='Path to component .blend file')
    parser.add_argument('--post-count', required=True, choices=['4', '6'], help='Number of posts')
    parser.add_argument('--color', required=True, choices=['red', 'blue', 'white'], help='Color selection')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--spacing', type=float, default=2.0, help='Spacing between posts')
    
    return parser.parse_args(argv)

def calculate_grid_positions(post_count, spacing):
    """Calculate grid positions for posts"""
    if post_count == '4':
        # 2x2 grid
        positions = [
            (-spacing/2, -spacing/2, 0),
            (spacing/2, -spacing/2, 0),
            (-spacing/2, spacing/2, 0),
            (spacing/2, spacing/2, 0),
        ]
    else:  # 6 post
        # 3x2 grid
        positions = [
            (-spacing, -spacing/2, 0),
            (0, -spacing/2, 0),
            (spacing, -spacing/2, 0),
            (-spacing, spacing/2, 0),
            (0, spacing/2, 0),
            (spacing, spacing/2, 0),
        ]
    return positions

def main():
    try:
        args = parse_arguments()
        
        print(f"Loading base file: {args.base_file}")
        # Open the base file
        if not os.path.exists(args.base_file):
            print(f"Error: Base file not found: {args.base_file}")
            sys.exit(1)
        
        bpy.ops.wm.open_mainfile(filepath=args.base_file)
        
        # Get the Model collection (or create it if it doesn't exist)
        model_collection = bpy.data.collections.get("Model")
        if not model_collection:
            model_collection = bpy.data.collections.new("Model")
            bpy.context.scene.collection.children.link(model_collection)
        
        # Calculate grid positions
        positions = calculate_grid_positions(args.post_count, args.spacing)
        
        print(f"Appending {len(positions)} component(s) from {args.component_file}")
        # Append collections from component file and position them
        appended_collections = []
        
        # First, check what collections are available in the component file
        if not os.path.exists(args.component_file):
            print(f"Error: Component file not found: {args.component_file}")
            sys.exit(1)
        
        with bpy.data.libraries.load(args.component_file) as (data_from, data_to):
            # The collection to append must be named "Model"
            collection_name = "Model"
            if "Model" not in data_from.collections:
                print("Error: 'Model' collection not found in component file")
                print(f"Available collections: {data_from.collections}")
                sys.exit(1)
        
        print(f"Appending collection: {collection_name}")
        
        for i, pos in enumerate(positions):
            try:
                # Append the collection using bpy.ops.wm.append()
                # The filepath format for collections is: blendfile/Collection/collection_name
                filepath = os.path.join(args.component_file, "Collection", collection_name)
                directory = os.path.join(args.component_file, "Collection")
                filename = collection_name
                
                # Append the collection
                bpy.ops.wm.append(
                    filepath=filepath,
                    directory=directory,
                    filename=filename
                )
                
                # Find the appended collection (it will have the same name, or be renamed if conflict)
                appended_collection = None
                # Check for exact match first
                if collection_name in bpy.data.collections:
                    appended_collection = bpy.data.collections[collection_name]
                else:
                    # If it was renamed due to conflict, find the newest collection
                    # Collections are appended in order, so find the one that matches our pattern
                    for coll in bpy.data.collections:
                        if coll.name == collection_name or coll.name.startswith(collection_name + "."):
                            appended_collection = coll
                            break
                
                if appended_collection:
                    # Rename to avoid conflicts for next iteration
                    new_name = f"{collection_name}_{i}"
                    appended_collection.name = new_name
                    
                    # Remove from scene collection if it was added there
                    if appended_collection.name in bpy.context.scene.collection.children:
                        bpy.context.scene.collection.children.unlink(appended_collection)
                    
                    # Link to Model collection
                    model_collection.children.link(appended_collection)
                    
                    appended_collections.append(appended_collection)
                    
                    # Position all objects in the collection (including sub-collections)
                    for obj in appended_collection.all_objects:
                        if obj.type == 'MESH':
                            obj.location = pos
                            print(f"Positioned {obj.name} at {pos}")
                else:
                    print(f"Error: Could not find appended collection after append operation")
                    sys.exit(1)
            except Exception as e:
                print(f"Error appending component {i}: {str(e)}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        
        # Apply colors to all collections
        print(f"Applying color: {args.color}")
        dbpath = find_db_path()
        
        if not os.path.exists(dbpath):
            print(f"Warning: Database file not found: {dbpath}")
            print("Continuing without color application...")
        else:
            # Apply colors to main Model collection
            apply_colors_to_collection(model_collection, dbpath, args.color, 'lowq')
            
            # Apply colors to all appended collections
            for collection in appended_collections:
                apply_colors_to_collection(collection, dbpath, args.color, 'lowq')
        
        # Set render engine to Eevee
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        print("Render engine set to Eevee")
        
        # Set output path
        bpy.context.scene.render.filepath = args.output
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Render
        print(f"Rendering to {args.output}")
        bpy.ops.render.render(write_still=True)
        
        print("Render complete!")
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

