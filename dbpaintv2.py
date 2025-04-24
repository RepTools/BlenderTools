bl_info = {
    "name": "DB Paint V2",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "Properties > World > DB Paint V2",
    "description": "Paint objects based on database mapping",
    "category": "Paint",
}

import bpy 
import sqlite3
import os

def find_path():
    end = 'OneDrive - Rep Fitness/Documents - Product and Engineering/Internal Docs/ID Team/paint.db'
    start = os.path.dirname(os.path.realpath(__file__))
    start = start.split('\\')
    first = '\\'.join(start[:3])
    path = first + '\\' + end
    return path

class PAINT_OT_db_paint(bpy.types.Operator):
    bl_idname = "paint.db_paint"
    bl_label = "Paint"
    bl_description = "Apply paint to objects based on database mapping"
    
    def execute(self, context):
        scene = context.scene
        dbpath = find_path()
        paint_type = scene.paint_type.lower()
        color_name = scene.paint_color.lower()
        map = {'lowq': 1, 'highq': 2}
        
        try:
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            
            collection = bpy.data.collections.get("Model")
            if not collection:
                self.report({'ERROR'}, "No 'Model' collection found!")
                return {'CANCELLED'}
            
            # Clear existing materials
            for obj in collection.objects:
                obj.data.materials.clear()
                
            # Apply new materials
            for obj in collection.objects:
                name = obj.name.split(" ")[0]
                index = cursor.execute("SELECT * FROM obj_color_map WHERE name = ?", (name,)).fetchone()
                
                if index is not None:
                    index = index[map[paint_type]]
                    
                    try:
                        if index == 'UC':
                            color = cursor.execute("SELECT * FROM color_indices WHERE color = ?", (color_name,)).fetchone()
                            if color is None or len(color) < 3:  # Check if color is None or doesn't have enough elements
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
            
            conn.close()
            self.report({'INFO'}, "Paint applied successfully!")
            return {'FINISHED'}
            
        except Exception as e:
            if conn:
                conn.close()
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}

class PAINT_PT_db_paint_panel(bpy.types.Panel):
    bl_label = "DB Paint V2"
    bl_idname = "PAINT_PT_db_paint_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Paint type selection
        layout.prop(scene, "paint_type")
        
        # Color selection
        layout.prop(scene, "paint_color")
        
        # Paint button
        layout.operator("paint.db_paint")

def register():
    bpy.types.Scene.paint_type = bpy.props.EnumProperty(
        name="Paint Type",
        description="Choose the paint quality type",
        items=[
            ('LOWQ', "Low Quality", "Low quality paint"),
            ('HIGHQ', "High Quality", "High quality paint"),
        ],
        default='LOWQ'
    )
    
    bpy.types.Scene.paint_color = bpy.props.EnumProperty(
        name="Color",
        description="Choose the paint color",
        items=[
            ('RED', "Red", "Red paint"),
            ('BLUE', "Blue", "Blue paint"),
            ('WHITE', "White", "White paint"),
            ('OLIVE', "Olive", "Olive paint"),
            ('BLACK', "Black", "Black paint"),
            ('MAT', "Mat", "Mat paint"),
            ('CLEAR', "Clear Coat", "Clear coat"),
        ],
        default='RED'
    )
    
    bpy.utils.register_class(PAINT_OT_db_paint)
    bpy.utils.register_class(PAINT_PT_db_paint_panel)

def unregister():
    bpy.utils.unregister_class(PAINT_OT_db_paint)
    bpy.utils.unregister_class(PAINT_PT_db_paint_panel)
    
    del bpy.types.Scene.paint_type
    del bpy.types.Scene.paint_color

if __name__ == "__main__":
    register()
    
