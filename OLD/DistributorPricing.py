import bpy

racks = {
    'PR-5000 80" x 30" 4 Post - Standard - Metallic Black': {
        "80, 4"
    },
    'PR-5000 93" x 30" 4 Post - Standard - Metallic Black': {
        "93, 4"
    },
    'PR-5000 80" x 30" 6 Post - Weight Storage & upgrades- Metallic Black': {
        "80, 6"
    },
    'PR-5000 93" x 30" 6 Post - Weight Storage & upgrades- Metallic Black': {
        "93, 6"
    },
    'PR-5000 80" 6-Post - With Ares and Upgrades - Metallic Black': {
        "80, 6",
        'Ares, 80, 6'
    },
    'PR-5000 93" 6-Post - With Ares and Upgrades - Metallic Black': {
        "93, 6",
        "Ares 93, 6"
    },
    'PR-5000 80" 6-Post - With Dual Athena and Upgrades - Metallic Black': {
        "80, 6",
        "Athena, 80, 6"
    },
    'PR-5000 93" 6-Post - With Dual Athena and Upgrades - Metallic Black': {
        "93, 6",
        "Athena, 93, 6"
    },
    'PR-5000 80" 4-Post - "Half Rack" With Dual Athena and Upgrades - Metallic Black': {
        "V2, 80, 16",
        "Athena, 80, 4",
        "Spotter Arms",
        "Feet"
    },
    'PR-5000 93" 4-Post - "Half Rack" With Dual Athena and Upgrades - Metallic Black': {
        "V2, 93, 16",
        "Athena, 93, 4",
        "Spotter Arms",
        "Feet"
    },
    'PR-5000 80" 4-Post - "Half Rack" With Ares and Upgrades - Metallic Black': {
        "V2, 80, 16",
        "Ares, 80, 4",
        "Spotter Arms",
        "Mini Feet"
    },
    'PR-5000 93" 4-Post - "Half Rack" With Ares and Upgrades - Metallic Black': {
        "V2, 93, 16",
        "Ares, 93, 16",
        "Spotter Arms",
        "Mini Feet"
    },
    'PR-5000 80" WALL MOUNTED DUAL ATHENA - Metallic Black',
    'PR-5000 93" WALL MOUNTED DUAL ATHENA - Metallic Black',
    }

collections = bpy.data.collections
def reset():
    for collection in collections:
        collection.hide_render(True)

def run():
    for rack in racks:
        reset()