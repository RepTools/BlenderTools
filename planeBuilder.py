bl_info = {
    "name": "Plane Builder",
    "author": "AJ Frio",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Plane Builder",
    "description": "Build a plane with dimensions converted from feet to Blender units",
    "category": "Utilities",
}

import bpy

# Conversion factor
FEET_TO_BLENDER = 0.9  # 1 foot = 0.9 Blender units

class PlaneBuilderProperties(bpy.types.PropertyGroup):
    x_ft: bpy.props.FloatProperty(name="X (ft)", default=10.0, min=0.0)
    y_ft: bpy.props.FloatProperty(name="Y (ft)", default=10.0, min=0.0)

class OBJECT_OT_build_scaled_plane(bpy.types.Operator):
    bl_idname = "object.build_scaled_plane"
    bl_label = "Build Scaled Plane"
    bl_description = "Build a plane with dimensions converted from feet to Blender units"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.plane_builder_props
        x_blender = props.x_ft * FEET_TO_BLENDER
        y_blender = props.y_ft * FEET_TO_BLENDER

        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = context.active_object
        plane.scale = (x_blender, y_blender, 1)  # Plane default size is 2x2

        plane.name = f"Plane_{props.x_ft}ft_{props.y_ft}ft"
        return {'FINISHED'}

class VIEW3D_PT_scaled_plane_panel(bpy.types.Panel):
    bl_label = "Plane Builder"
    bl_idname = "VIEW3D_PT_scaled_plane_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Plane Builder'

    def draw(self, context):
        layout = self.layout
        props = context.scene.plane_builder_props

        layout.prop(props, "x_ft")
        layout.prop(props, "y_ft")
        layout.operator("object.build_scaled_plane", text="Build Plane")

classes = (
    PlaneBuilderProperties,
    OBJECT_OT_build_scaled_plane,
    VIEW3D_PT_scaled_plane_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.plane_builder_props = bpy.props.PointerProperty(type=PlaneBuilderProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.plane_builder_props

if __name__ == "__main__":
    register()
