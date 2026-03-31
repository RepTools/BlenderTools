## Template Workflow

`TemplateV3.blend` is the base Blender file used for painting imported SolidWorks assemblies. It contains the premade materials that get assigned to parts after import, along with the material library needed for both final renders and glTF-compatible exports.

## What Each File Does

- `Template/TemplateV3.blend`: Base template file that holds the premade materials used by the workflow.
- `rename.py`: Blender add-on used to rename exported STL files and import them into the template scene.
- `updateDB.py`: Blender add-on used to store or overwrite the material mapping for a selected component name in `paint.db`.
- `dbpaintv2.py`: Blender add-on used to paint every object in the scene based on the saved database mapping.
- `paint.db`: SQLite database that stores component-to-material mappings.

## Workflow Overview

1. Export a SolidWorks assembly as individual STL files into a folder.
2. Open `Template/TemplateV3.blend`.
3. Use the `rename.py` add-on to select the STL folder and click `Rename Files`.
4. Still in `rename.py`, click `Import STL Files` to bring the renamed STL files into the template.
5. Use `updateDB.py` to assign material categories to parts and save that mapping into `paint.db`.
6. Use `dbpaintv2.py` to apply materials across the imported model using the saved database mapping.

## Renaming And Importing

The `rename.py` add-on is used after exporting a SolidWorks assembly as separate STL files. In Blender:

1. Enable or run `rename.py`.
2. In the `File Renamer` panel, choose the folder containing the exported STL files.
3. Click `Rename Files`.
4. Click `Import STL Files`.

This prepares the imported objects so their names can be matched against entries in the database.

## Database Mapping

The `updateDB.py` add-on is used to create or update the material mapping for a part.

1. Select an object in the scene.
2. Open the `DB Map Color Selector` panel.
3. Choose the correct material category from the dropdown.
4. Click `Add`.

The selected object's base name is used as the lookup key. That mapping is global for every component with the same name, not just the currently selected model. For example, if `15-003463` is mapped to `silverHardware`, every object named `15-003463` will continue using that material category until the database entry is overwritten.

## Material Quality Types

The template contains two material sets:

- High quality materials for rendering.
- Low quality materials for glTF-compatible output.

`dbpaintv2.py` lets you choose which material quality to apply before painting the model.

## Painting The Model

Use `dbpaintv2.py` after the model has been imported and the database mapping is ready.

1. Open the `DB Paint V2` panel.
2. Choose the `Paint Type`:
   - `Low Quality` for glTF-compatible materials.
   - `High Quality` for render materials.
3. Choose the `Color` for parts that use the generic color-mapped material category.
4. Click `Paint`.

The script iterates through the objects in the `Model` collection and applies the correct material based on:

- The selected quality level.
- The selected color for objects using the generic color slot.
- The object name and its mapping in `paint.db`.

If an object has no database mapping, the script falls back to the default material (bright pink).
