bl_info = {
    "name": "STEP Exporter",
    "author": "AJ Frio",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),  # Minimum Blender version
    "location": "File > Export > STEP (.step/.stp)",
    "description": "Exports selected meshes as STEP files using pythonocc-core",
    "warning": "Requires manual installation of pythonocc-core library.",
    "doc_url": "",
    "category": "Import-Export",
}

# Check for pythonocc-core and provide instructions if missing
try:
    from OCC.Core.gp import gp_Pnt
    from OCC.Core.TopoDS import TopoDS_Vertex, TopoDS_Edge, TopoDS_Wire, TopoDS_Face, TopoDS_Compound
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCC.Core.Interface import Interface_Static_SetCVal
    from OCC.Core.IFSelect import IFSelect_RetVoid
    pythonocc_core_available = True
    print("STEP Exporter: pythonocc-core library found.")
except ImportError:
    pythonocc_core_available = False
    print("STEP Exporter: pythonocc-core library not found. Addon will be registered but non-functional until installed.")
    # We still define dummy classes/functions if import fails so Blender can register the addon
    # This allows the user to see the menu item and get the error message upon trying to use it.
    gp_Pnt = None
    TopoDS_Vertex = None
    TopoDS_Edge = None
    TopoDS_Wire = None
    TopoDS_Face = None
    TopoDS_Compound = None
    BRepBuilderAPI_MakeVertex = None
    BRepBuilderAPI_MakeEdge = None
    BRepBuilderAPI_MakeWire = None
    BRepBuilderAPI_MakeFace = None
    BRep_Builder = None
    STEPControl_Writer = None
    STEPControl_AsIs = None
    Interface_Static_SetCVal = None
    IFSelect_RetVoid = -1 # Assign a dummy value

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import sys
import os

class STEPExporterOperator(Operator, ExportHelper):
    """Exports selected mesh objects to a STEP file"""
    bl_idname = "export_mesh.step"
    bl_label = "Export STEP"
    bl_description = "Export selected mesh objects to STEP (.step/.stp) format"

    # ExportHelper mixin class uses this
    filename_ext = ".step"
    filter_glob: StringProperty(
        default="*.step;*.stp",
        options={'HIDDEN'},
        maxlen=255,  # Max path length
    )

    def execute(self, context):
        if not pythonocc_core_available:
            self.report({'ERROR'}, "pythonocc-core not found. Please install it. See System Console.")
            # Try to provide more specific install instructions in the console
            print("-" * 50)
            print("ERROR: pythonocc-core library not found for STEP Exporter addon.")
            print("You need to install it into Blender's Python environment.")
            try:
                # Get Blender's Python executable path
                py_exec = sys.executable
                print(f"Detected Blender Python executable: {py_exec}")
                # Construct the pip command
                pip_cmd = f'"{py_exec}" -m pip install pythonocc-core'
                print("Run this command in your terminal (Command Prompt, PowerShell, bash, etc.):")
                print(pip_cmd)
                print("(You might need administrator/sudo privileges)")

            except Exception as e:
                print("Could not determine Blender's Python executable path automatically.")
                print("Please find python.exe within your Blender installation directory (e.g., in '3.6/python/bin').")
                print("Then run: path/to/blender/python.exe -m pip install pythonocc-core")
            print("-" * 50)
            return {'CANCELLED'}

        filepath = self.filepath
        # Ensure the directory exists
        try:
             os.makedirs(os.path.dirname(filepath), exist_ok=True)
        except OSError as e:
            self.report({'ERROR'}, f"Could not create directory: {os.path.dirname(filepath)}. Error: {e}")
            return {'CANCELLED'}


        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_objects:
            self.report({'WARNING'}, "No mesh objects selected for export.")
            return {'CANCELLED'}

        print(f"Exporting {len(selected_objects)} mesh objects to {filepath}...")

        writer = STEPControl_Writer()
        # Set STEP schema, AP214 is common for CAD compatibility
        Interface_Static_SetCVal("write.step.schema", "AP214")

        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        faces_added_count = 0

        for obj in selected_objects:
            print(f"Processing object: {obj.name}")
            try:
                # Get the evaluated mesh (applies modifiers)
                depsgraph = context.evaluated_depsgraph_get()
                ob_for_mesh = obj.evaluated_get(depsgraph)
                mesh = ob_for_mesh.to_mesh()
                if not mesh:
                    print(f"Warning: Could not get mesh data for object '{obj.name}'. Skipping.")
                    continue

                # Apply world transformation to the mesh data directly
                mesh.transform(obj.matrix_world)
                mesh.calc_loop_triangles() # Ensure triangulation for face processing

            except Exception as e:
                 print(f"Error getting evaluated mesh for '{obj.name}': {e}. Skipping object.")
                 continue # Skip this object if mesh evaluation fails

            # Create OCC geometry
            vertices = [gp_Pnt(v.co.x, v.co.y, v.co.z) for v in mesh.vertices]

            # Process faces (using loop triangles for simplicity)
            for tri in mesh.loop_triangles:
                v_indices = [mesh.loops[li].vertex_index for li in tri.loops]

                if len(set(v_indices)) < 3:
                    # print(f"Warning: Skipping degenerate triangle (duplicate vertices) in object '{obj.name}'. Indices: {v_indices}")
                    continue # Skip degenerate triangles

                pts = [vertices[i] for i in v_indices]

                # Check for coincident points which OCC dislikes
                if pts[0].IsEqual(pts[1], 1e-7) or pts[1].IsEqual(pts[2], 1e-7) or pts[2].IsEqual(pts[0], 1e-7):
                     # print(f"Warning: Skipping triangle with coincident vertices in object '{obj.name}'.")
                    continue

                try:
                    # Create vertices
                    occ_v1 = BRepBuilderAPI_MakeVertex(pts[0]).Vertex()
                    occ_v2 = BRepBuilderAPI_MakeVertex(pts[1]).Vertex()
                    occ_v3 = BRepBuilderAPI_MakeVertex(pts[2]).Vertex()

                    # Create edges
                    edge1 = BRepBuilderAPI_MakeEdge(occ_v1, occ_v2).Edge()
                    edge2 = BRepBuilderAPI_MakeEdge(occ_v2, occ_v3).Edge()
                    edge3 = BRepBuilderAPI_MakeEdge(occ_v3, occ_v1).Edge()

                    if edge1.IsNull() or edge2.IsNull() or edge3.IsNull():
                        # print(f"Warning: Failed to create one or more edges for a triangle in object '{obj.name}'. Skipping face.")
                        continue

                    # Create wire
                    wire_builder = BRepBuilderAPI_MakeWire()
                    wire_builder.Add(edge1)
                    wire_builder.Add(edge2)
                    wire_builder.Add(edge3)

                    if not wire_builder.IsDone():
                        # print(f"Warning: Failed to build wire for a triangle in object '{obj.name}'. Skipping face.")
                        continue

                    wire = wire_builder.Wire()
                    if wire.IsNull():
                         # print(f"Warning: Wire is null for a triangle in object '{obj.name}'. Skipping face.")
                         continue

                    # Create face
                    occ_face = BRepBuilderAPI_MakeFace(wire).Face()
                    if not occ_face.IsNull():
                        builder.Add(compound, occ_face)
                        faces_added_count += 1
                    # else:
                        # print(f"Warning: Failed to create face from wire in object '{obj.name}'.")

                except Exception as e:
                    # print(f"Error processing triangle in object '{obj.name}': {e}. Skipping face.")
                    continue # Skip this face and move to the next

            # Clean up temporary mesh data
            try:
                ob_for_mesh.to_mesh_clear()
            except Exception as e:
                 print(f"Warning: Could not clear temporary mesh data for '{obj.name}': {e}")

        if faces_added_count == 0:
             self.report({'ERROR'}, "No valid faces could be generated for STEP export from selected objects.")
             print("Export failed: No geometry was successfully converted.")
             return {'CANCELLED'}

        print(f"Successfully converted {faces_added_count} faces to OCC format.")
        print("Writing STEP file...")

        # Transfer the compound shape to the writer
        transfer_status = writer.Transfer(compound, STEPControl_AsIs)
        if transfer_status != IFSelect_RetVoid:
             self.report({'ERROR'}, f"STEP writer Transfer failed. Status code: {transfer_status}")
             print(f"Export failed: STEP writer Transfer returned status {transfer_status}")
             return {'CANCELLED'}

        # Write the STEP file
        write_status = writer.Write(filepath)

        if write_status == IFSelect_RetVoid:
            self.report({'INFO'}, f"Successfully exported {faces_added_count} faces to: {filepath}")
            print(f"Export finished successfully: {filepath}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Failed to write STEP file. Status code: {write_status}")
            print(f"Export failed: STEP writer Write returned status {write_status}")
            return {'CANCELLED'}


def menu_func_export(self, context):
    self.layout.operator(STEPExporterOperator.bl_idname, text="STEP (.step/.stp)")

def register():
    bpy.utils.register_class(STEPExporterOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    if not pythonocc_core_available:
        print("STEP Exporter addon registered, but pythonocc-core is missing.")
        print("Please install it following the instructions printed above or in the System Console upon export attempt.")

def unregister():
    bpy.utils.unregister_class(STEPExporterOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    print("STEP Exporter addon unregistered.")

# This allows the script to be run directly in Blender Text Editor
# to test registration/unregistration
if __name__ == "__main__":
    # Unregister previous version if exists
    try:
        unregister()
    except Exception:
        pass # Ignore errors if not registered
    register()
