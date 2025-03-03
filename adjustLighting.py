import bpy
from bpy.types import Panel, Operator

# Operators for different percentage adjustments
class LIGHT_OT_adjust_minus_50(Operator):
    bl_idname = "light.adjust_minus_50"
    bl_label = "-50%"
    bl_description = "Decrease light brightness by 50%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 0.5
        return {'FINISHED'}

class LIGHT_OT_adjust_minus_25(Operator):
    bl_idname = "light.adjust_minus_25"
    bl_label = "-25%"
    bl_description = "Decrease light brightness by 25%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 0.75
        return {'FINISHED'}

class LIGHT_OT_adjust_minus_10(Operator):
    bl_idname = "light.adjust_minus_10"
    bl_label = "-10%"
    bl_description = "Decrease light brightness by 10%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 0.9
        return {'FINISHED'}

class LIGHT_OT_adjust_plus_10(Operator):
    bl_idname = "light.adjust_plus_10"
    bl_label = "+10%"
    bl_description = "Increase light brightness by 10%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 1.1
        return {'FINISHED'}

class LIGHT_OT_adjust_plus_25(Operator):
    bl_idname = "light.adjust_plus_25"
    bl_label = "+25%"
    bl_description = "Increase light brightness by 25%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 1.25
        return {'FINISHED'}

class LIGHT_OT_adjust_plus_50(Operator):
    bl_idname = "light.adjust_plus_50"
    bl_label = "+50%"
    bl_description = "Increase light brightness by 50%"
    
    def execute(self, context):
        if "Setting" in bpy.data.collections:
            for obj in bpy.data.collections["Setting"].objects:
                if obj.type == 'LIGHT':
                    obj.data.energy *= 1.5
        return {'FINISHED'}

# Panel class for the UI
class LIGHT_PT_adjust_panel(Panel):
    bl_label = "Adjust Lighting"
    bl_idname = "LIGHT_PT_adjust_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        
        # Add buttons in two rows
        row1 = layout.row()
        row1.operator("light.adjust_minus_50")
        row1.operator("light.adjust_minus_25")
        row1.operator("light.adjust_minus_10")
        
        row2 = layout.row()
        row2.operator("light.adjust_plus_10")
        row2.operator("light.adjust_plus_25")
        row2.operator("light.adjust_plus_50")

# List of classes to register
classes = [
    LIGHT_OT_adjust_minus_50,
    LIGHT_OT_adjust_minus_25,
    LIGHT_OT_adjust_minus_10,
    LIGHT_OT_adjust_plus_10,
    LIGHT_OT_adjust_plus_25,
    LIGHT_OT_adjust_plus_50,
    LIGHT_PT_adjust_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
