prefix = "REPPR"
midfix = 'AR2.0'
conversion_table = {'4K': '4000', '5K': '5000', 'BLACK': 'MBLK', 'RED': 'RED', 'CC': 'CC'}

import bpy

def findName(name: str, pro: bool):
    components = name.split(',')
    series = conversion_table[components[0].split('-')[0]]
    color = conversion_table[components[0].split('-')[1]]
    height = components[1].split('-')[0].strip()
    post = components[2].strip()
    
    if pro:
        compiledName = f"{prefix}{series}PRO{midfix}{post}{height}{color}"
        return compiledName
    else:
        compiledName = f"{prefix}{series}{midfix}{post}{height}{color}"
        return compiledName

def find4PostName(name: str, foot: bool):
    components = name.split(' ')
    height = components[0]
    color = components[1]

    if foot:
        compiledName = f"{prefix}{conversion_table['5K']}{midfix}4{height}{conversion_table[color.upper()]} with Feet"
        return compiledName
    else:
        compiledName = f"{prefix}{conversion_table['5K']}{midfix}4{height}{conversion_table[color.upper()]}"
        return compiledName
    

def process_collections():
    print('STARTING________________________________')
    # Get the 'Racks' collection
    racks_collection = bpy.data.collections.get('Racks')
    attachments_collection = bpy.data.collections.get('Attachments')
    pro_addons_93 = attachments_collection.children.get('Pro Addons 93')
    pro_addons_80 = attachments_collection.children.get('Pro Addons 80')
    basic_addons_93 = attachments_collection.children.get('Basic Addons 93')
    basic_addons_80 = attachments_collection.children.get('Basic Addons 80')

    
    if not racks_collection:
        print("'Racks' collection not found")
        return
    
    #Hide all Attachments
    for attachment in attachments_collection.children:
        attachment.hide_viewport = True
        attachment.hide_render = True

    # Iterate through all collections inside 'Racks'
    for collection in racks_collection.children:
        for hidden_collection in racks_collection.children:
            hidden_collection.hide_viewport = True
            hidden_collection.hide_render = True
        collection.hide_render = False

        name = collection.name
        if name.split(',')[1].split('-')[0] == ' 93':

            pro_addons_93.hide_render = False
            compiledName = findName(name, True)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)

            pro_addons_93.hide_render = True
            basic_addons_93.hide_render = False
            compiledName = findName(name, False)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)
            basic_addons_93.hide_render = True
        if name.split(',')[1].split('-')[0] == ' 80':
            collection.hide_render = False
            pro_addons_80.hide_render = False
            compiledName = findName(name, True)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)

            pro_addons_80.hide_render = True
            basic_addons_80.hide_render = False
            compiledName = findName(name, False)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)
            basic_addons_80.hide_render = True
        collection.hide_render = True
            

def hideRacks():
    racks_collection = bpy.data.collections.get('Racks')
    attachments_collection = bpy.data.collections.get('Attachments')
    pro_addons_93 = attachments_collection.children.get('Pro Addons 93')
    pro_addons_80 = attachments_collection.children.get('Pro Addons 80')
    basic_addons_93 = attachments_collection.children.get('Basic Addons 93')
    basic_addons_80 = attachments_collection.children.get('Basic Addons 80')
    fourracks_collection = bpy.data.collections.get('4 Post Racks')
    jcup_collection = bpy.data.collections.get('4 Jcups')
    feet = bpy.data.collections.get('Feet')

    racks_collection.hide_render = True
    attachments_collection.hide_render = True
    pro_addons_80.hide_render = True
    pro_addons_93.hide_render = True
    basic_addons_80.hide_render = True
    basic_addons_93.hide_render = True
    fourracks_collection.hide_render = True
    jcup_collection.hide_render = True
    feet.hide_render = True

def process_4posts():
    print('STARTING________________________________')
    # Get the 'Racks' collection
    racks_collection = bpy.data.collections.get('4 Post Racks')
    jcup_collection = bpy.data.collections.get('4 Jcups')
    feet = bpy.data.collections.get('Feet')

    if not racks_collection:
        print("'4 Post Racks' collection not found")
        return

    jcup_collection.hide_render = True
    feet.hide_render = True

    for collection in racks_collection.children:
        for hidden_collection in racks_collection.children:
            hidden_collection.hide_viewport = True
            hidden_collection.hide_render = True
        collection.hide_render = False
        jcup_collection.hide_render = False
        feet.hide_render = True
        
        name = collection.name

        if name.split(' ')[0] == "93":    

            compiledName = find4PostName(name, False)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)

            feet.hide_render = False
            compiledName = find4PostName(name, True)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)

        else:
            compiledName = find4PostName(name, False)
            bpy.context.scene.render.filepath = f"//renders/{compiledName}"
            bpy.ops.render.render(write_still=True)
            print(compiledName)
        collection.hide_render = True

process_4posts()