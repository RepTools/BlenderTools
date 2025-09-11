import bpy

racks = {
    'PR-5000 80" x 30" 4 Post - Standard - Metallic Black': {
        "80, 4"
    },
    'PR-5000 93" x 30" 4 Post - Standard - Metallic Black': {
        "93, 4"
    },
    'PR-5000 80" x 30" 6 Post - Weight Storage & upgrades- Metallic Black': {
        "80, 6",
        "Straps"
    },
    'PR-5000 93" x 30" 6 Post - Weight Storage & upgrades- Metallic Black': {
        "93, 6",
        "Straps"
    },
    'PR-5000 80" 6-Post - With Ares and Upgrades - Metallic Black': {
        "80, 6",
        'Ares, 80, 6',
        "Straps"
    },
    'PR-5000 93" 6-Post - With Ares and Upgrades - Metallic Black': {
        "93, 6",
        "Ares 93, 6",
        "Straps"
    },
    'PR-5000 80" 6-Post - With Dual Athena and Upgrades - Metallic Black': {
        "80, 6",
        "Athena, 80, 6",
        "Straps"
    },
    'PR-5000 93" 6-Post - With Dual Athena and Upgrades - Metallic Black': {
        "93, 6",
        "Athena, 93, 6",
        "Straps"
    },
    'PR-5000 80" 4-Post - "Half Rack" With Dual Athena and Upgrades - Metallic Black': {
        "80 Half Athena",
        "Athena, 80, 4",
        "Spotter Arms",
        "Feet"
    },
    'PR-5000 93" 4-Post - "Half Rack" With Dual Athena and Upgrades - Metallic Black': {
        "93 Half Athena",
        "Athena, 93, 4",
        "Spotter Arms",
        "Feet"
    },
    'PR-5000 80" 4-Post - "Half Rack" With Ares and Upgrades - Metallic Black': {
        "80 Half Ares",
        "Ares, 80, 4",
        "Spotter Arms",
        "Mini Front Feet"
    },
    'PR-5000 93" 4-Post - "Half Rack" With Ares and Upgrades - Metallic Black': {
        "93 Half Ares",
        "Ares, 93, 4",
        "Spotter Arms",
        "Mini Front Feet"
    },
    'PR-5000 80" WALL MOUNTED DUAL ATHENA - Metallic Black': {
        "Athena, 80, 2",
        "Spotter Arms",
        "Feet"
    },
    'PR-5000 93" WALL MOUNTED DUAL ATHENA - Metallic Black': {
        "Athena, 93, 2",
        "Spotter Arms",
        "Feet"
    },
}

collections = bpy.data.collections
file_path = "C:\\Users\\AJFrio\\OneDrive - Rep Fitness\\Desktop\\Distrubutor Racks"

def render_cameras(image_name):
    # Sanitize the image_name to replace quotes, which are invalid in file paths.
    image_name = image_name.replace('"', ' ').replace("'", " ")
    image_number = 0
    scene = bpy.context.scene
    
    for camera in collections.get("Cameras").objects:
        # Set this camera as the active render camera
        scene.camera = camera
        
        # Set up render settings
        scene.render.engine = 'CYCLES'
        scene.render.image_settings.file_format = 'PNG'
        
        # Set output path
        image_number += 1
        scene.render.filepath = f"{file_path}/{image_name}_{image_number}.png"
        
        # Render the image
        bpy.ops.render.render(write_still=True)
 
def reset():
    for collection in collections:
        if collection.name != "Cameras" and collection.name != "Setting":
            collection.hide_render = True


def run():
    for rack_name, collection_names in racks.items():
        reset()

        for collection_name in collection_names:
            if collection_name in collections:
                collections[collection_name].hide_render = False
            else:
                print(f"Warning: Collection '{collection_name}' not found.")

        render_cameras(rack_name)

run()