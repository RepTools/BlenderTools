bl_info = {
    "name": "DB Map Updater",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "World",
    "description": "Update the DB Map for the selected object",
    "category": "Object",
}

import bpy
import sqlite3
import os

simpleMats = {"plastic": 19, "silverHardware": 6, "blackHardware": 13, "chrome": 15, "permBlack": 13, "permMat": 17, "pulleys": 6, "rubber": 17, "cloth": 10, "UC": "UC"}
complexMats = {"plastic": 11, "silverHardware": 6, "blackHardware": 9, "chrome": 3, "permBlack": 9, "permMat": 10, "pulleys": 5, "rubber": 11, "cloth": 10, "UC": "UC"}

# Add this enum items list for the dropdown
color_items = [
    ('UC', "Color", ""),
    ('silverHardware', "Silver Hardware", ""),
    ('chrome', "Chrome", ""),
    ('blackHardware', "Black Hardware", ""),
    ('permMat', "Matte Black", ""),
    ('permBlack', "Black Powdercoat", ""),
    ('rubber', "Rubber", ""),
    ('plastic', "Plastic", ""),
    ('cloth', "Cloth", ""),
]

def get_selected_object_name():
    # Get the active (selected) object
    selected_obj = bpy.context.active_object
    
    # Check if there is an active object
    if selected_obj is not None:
        return str(selected_obj.name).split(' ')[0]
    else:
        return None
    
def find_path():
    end = 'OneDrive - Rep Fitness/Documents - Product and Engineering/Internal Docs/ID Team/paint.db'
    start = os.path.dirname(os.path.realpath(__file__))
    start = start.split('\\')
    first = '\\'.join(start[:3])
    path = first + '\\' + end
    print(path)
    return path
 

class ColorSelectorPanel(bpy.types.Panel):
    bl_label = "DB Map Color Selector"
    bl_idname = "WORLD_PT_db_map_updater"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Create dropdown for color selection
        layout.prop(scene, "color_dropdown")
        
        # Create Add button
        layout.operator("object.add_to_db", text="Add")

class SelectColorOperator(bpy.types.Operator):
    bl_idname = "object.select_color"
    bl_label = "Select Color"
    
    def execute(self, context):
        context.scene.selected_color = "UC"
        return {'FINISHED'}

class SelectSilverHardwareOperator(bpy.types.Operator):
    bl_idname = "object.select_silver_hardware"
    bl_label = "Select Silver Hardware"
    
    def execute(self, context):
        context.scene.selected_color = "silverHardware"
        return {'FINISHED'}

class SelectChromeOperator(bpy.types.Operator):
    bl_idname = "object.select_chrome"
    bl_label = "Select Chrome"
    
    def execute(self, context):
        context.scene.selected_color = "chrome"
        return {'FINISHED'}

class SelectBlackHardwareOperator(bpy.types.Operator):
    bl_idname = "object.select_black_hardware"
    bl_label = "Select Black Hardware"
    
    def execute(self, context):
        context.scene.selected_color = "blackHardware"
        return {'FINISHED'}

class SelectMatteBlackOperator(bpy.types.Operator):
    bl_idname = "object.select_matte_black"
    bl_label = "Select Matte Black"
    
    def execute(self, context):
        context.scene.selected_color = "permMat"
        return {'FINISHED'}

class SelectBlackPowdercoatOperator(bpy.types.Operator):
    bl_idname = "object.select_black_powdercoat"
    bl_label = "Select Black Powdercoat"
    
    def execute(self, context):
        context.scene.selected_color = "permBlack"
        return {'FINISHED'}

class SelectRubberOperator(bpy.types.Operator):
    bl_idname = "object.select_rubber"
    bl_label = "Select Rubber"
    
    def execute(self, context):
        context.scene.selected_color = "rubber"
        return {'FINISHED'}

class SelectPlasticOperator(bpy.types.Operator):
    bl_idname = "object.select_plastic"
    bl_label = "Select Plastic"
    
    def execute(self, context):
        context.scene.selected_color = "plastic"
        return {'FINISHED'}
    
class SelectClothOperator(bpy.types.Operator):
    bl_idname = "object.select_cloth"
    bl_label = "Select Cloth"
    
    def execute(self, context):
        context.scene.selected_color = "cloth"
        return {'FINISHED'}

class AddToDBOperator(bpy.types.Operator):
    bl_idname = "object.add_to_db"
    bl_label = "Add to DB"
    
    def execute(self, context):
        obj_name = get_selected_object_name()
        if obj_name:
            # Use the dropdown value instead of selected_color
            color = context.scene.color_dropdown
            print(f"Selected object: {obj_name}, Color: {color}")
            db_path = find_path()
            
            try:
                # Add timeout parameter and use with statement for proper connection handling
                conn = sqlite3.connect(db_path, timeout=10)
                with conn:  # This ensures proper closing even if an exception occurs
                    cur = conn.cursor()
                    
                    # Check if the object already exists in the database
                    cur.execute("SELECT * FROM obj_color_map WHERE name = ?", (obj_name,))
                    existing_record = cur.fetchone()
                    
                    if existing_record:
                        # Update existing record
                        cur.execute("UPDATE obj_color_map SET mapped_index_lowq = ?, mapped_index_highq = ? WHERE name = ?", 
                                  (simpleMats[color], complexMats[color], obj_name))
                        self.report({'INFO'}, f"Updated {obj_name} in DB")
                    else:
                        # Insert new record
                        cur.execute("INSERT INTO obj_color_map (name, mapped_index_lowq, mapped_index_highq) VALUES (?, ?, ?)", 
                                  (obj_name, simpleMats[color], complexMats[color]))
                        self.report({'INFO'}, "Object added to DB")
                # Connection is automatically closed when exiting the with block
            except sqlite3.Error as e:
                self.report({'ERROR'}, f"Database error: {str(e)}")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No object selected!")
        return {'FINISHED'}

def register():
    # Replace the string property with an enum property
    bpy.types.Scene.color_dropdown = bpy.props.EnumProperty(
        name="Select Color",
        description="Choose a color or material type",
        items=color_items,
        default='UC'
    )
    bpy.utils.register_class(ColorSelectorPanel)
    bpy.utils.register_class(SelectColorOperator)
    bpy.utils.register_class(SelectSilverHardwareOperator)
    bpy.utils.register_class(SelectChromeOperator)
    bpy.utils.register_class(SelectBlackHardwareOperator)
    bpy.utils.register_class(SelectMatteBlackOperator)
    bpy.utils.register_class(SelectBlackPowdercoatOperator)
    bpy.utils.register_class(SelectRubberOperator)
    bpy.utils.register_class(SelectPlasticOperator)
    bpy.utils.register_class(SelectClothOperator)
    bpy.utils.register_class(AddToDBOperator)

def unregister():
    # Update this line to remove the enum property
    del bpy.types.Scene.color_dropdown
    bpy.utils.unregister_class(ColorSelectorPanel)
    bpy.utils.unregister_class(SelectColorOperator)
    bpy.utils.unregister_class(SelectSilverHardwareOperator)
    bpy.utils.unregister_class(SelectChromeOperator)
    bpy.utils.unregister_class(SelectBlackHardwareOperator)
    bpy.utils.unregister_class(SelectMatteBlackOperator)
    bpy.utils.unregister_class(SelectBlackPowdercoatOperator)
    bpy.utils.unregister_class(SelectRubberOperator)
    bpy.utils.unregister_class(SelectPlasticOperator)
    bpy.utils.unregister_class(SelectClothOperator)
    bpy.utils.unregister_class(AddToDBOperator)

if __name__ == "__main__":
    register()
 

