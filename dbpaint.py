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

dbpath = find_path()

paint_type = 'lowq'
map = {'lowq': 1, 'highq': 2}
obj_color_map_options = ['mapped_index_lowq', 'mapped_index_highq']
color_indices_options = ['lowq_index', 'highq_index']
color_name = 'red'

conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

collection = bpy.data.collections.get("Model")
for obj in collection.objects:
    # Clear all existing materials. Blender gets angry when you start stacking a bunch of colors on top of each other that weren't meant to be stackedd
    obj.data.materials.clear()
    print("Materials cleared from", obj.name, "successfully!")

for obj in collection.objects:
    print(obj.name)
    name = obj.name.split(" ")[0]
    index = cursor.execute("SELECT * FROM obj_color_map WHERE name = ?", (name,)).fetchone()
    print(index)
    if not type(index) == type(None):
        index = index[map[paint_type]]

        try:
            obj.data.materials.append(bpy.data.materials[index])
            print(index, obj.name)
        except:
            if index == 'UC':
                color = cursor.execute("SELECT * FROM color_indices WHERE color = ?", (color_name,)).fetchone()
                obj.data.materials.append(bpy.data.materials[color[1]])
                print(index, obj.name)
            else:
                obj.data.materials.append(bpy.data.materials[0])
                print(index, obj.name)
    else:
        print(index, obj.name)

    print("Material assigned to ", obj.name, " successfully!")


conn.close()
