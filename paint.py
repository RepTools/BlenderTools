bl_info = {
    "name": "Rep Fitness Color Map",
    "blender": (3, 0, 0),
    "category": "World",
}

import bpy

class WorldPropertiesPanel(bpy.types.Panel):
    bl_label = "Auto Paint"
    bl_idname = "WORLD_PT_custom_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        world = context.scene.world

        # First group of buttons
        layout.label(text="Complexity:")
        row = layout.row()
        row.prop(world, "complexity", expand=True)

        # Second group of buttons
        layout.label(text="Color:")
        row = layout.row()
        row.prop(world, "color_choice", expand=True)

        # Paint button
        layout.operator("world.paint_action")

def paint_action(self, context):
    world = context.scene.world
    complexity = world.complexity
    color_choice = world.color_choice

    # Replace the following with your custom function
    print(f"Painting with complexity: {complexity} and color: {color_choice}")

class WORLD_OT_PaintAction(bpy.types.Operator):
    bl_label = "Paint"
    bl_idname = "world.paint_action"

    def execute(self, context):
        #paint_action(self, context)
        autoPaint(context.scene.world.color_choice, context.scene.world.complexity)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(WorldPropertiesPanel)
    bpy.utils.register_class(WORLD_OT_PaintAction)

    bpy.types.World.complexity = bpy.props.EnumProperty(
        name="Complexity",
        description="Choose the complexity: Simple for file conversions, Complex for rendering.",
        items=[
            ('SIMPLE', "Simple", ""),
            ('COMPLEX', "Complex", ""),
        ],
        default='SIMPLE'
    )

    bpy.types.World.color_choice = bpy.props.EnumProperty(
        name="Color",
        description="Choose the color",
        items=[
            ('RED', "Red", ""),
            ('BLUE', "Blue", ""),
            ('WHITE', "White", ""),
            ('BLACK', "Black", ""),
            ('MAT', "Mat Black", ""),
            ('OLIVE', "Olive", ""),
            ('CC/SS', "CC/SS", ""),
        ],
        default='RED'
    )

def unregister():
    bpy.utils.unregister_class(WorldPropertiesPanel)
    bpy.utils.unregister_class(WORLD_OT_PaintAction)
    del bpy.types.World.complexity
    del bpy.types.World.color_choice

def autoPaint(color: str, pallet: str) -> None:

    simpleColors = {"UC":{"black": 13, "blue": 14, "clear coat": 16, "mat": 17, "olive": 18, "red": 20, "white": 13}, "plastic": 19, "silverHardware": 6, "blackHardware": 13, "chrome": 15, "permBlack": 13, "permMat": 17, "pulleys": 6, "rubber": 17, "cloth": 10}
    complexColors = {"UC":{"black": 1, "blue": 2, "clear coat": 4, "mat": 7, "olive": 8, "red": 12, "white": 21}, "plastic": 11, "silverHardware": 6, "blackHardware": 9, "chrome": 3, "permBlack": 9, "permMat": 10, "pulleys": 5, "rubber": 11, "cloth": 10}
    color = color.lower()
    pallet = pallet.lower()
# Dictionary of colors and their respective index in the blender color list
    if pallet == "complex":
        colors = complexColors
    elif pallet == "simple":
        colors = simpleColors

    """UC = colors[color] #UC is uprights and crossmembers, anything that would change colorsa through configs if needed
    plastic = 11 #Plastic parts, upright caps, 
    silverHardware = 6
    blackHardware = 9
    chrome = 3 #Low Row bars, handles
    permBlack = 9 #Shrouds, trolleys, cable brackets, cables
    permMat = 10 #Pullup bars, LPC
    pulleys = 5 
    rubber = 11 #Weight horn bumpers, guide rod grommet
    cloth = 10 #Seat, backrest, leg roller, D handles"""


    # Dictionary of model names and their respective materials          ##### "": colors[""],
    # Move to a txt file for cleaner access
    materials = {"15-0318": colors["UC"][str(color)], "15-0217": colors["UC"][str(color)], "10-0315": colors["silverHardware"], "10-0310": colors["silverHardware"], "10-0026": colors["silverHardware"], "10-0030": colors["silverHardware"], "15-0327": colors["UC"][str(color)],
                "15-0320": colors["UC"][str(color)], "15-0321": colors["UC"][str(color)], "15-0319": colors["UC"][str(color)], "10-0003": colors["plastic"], "15-0564": colors["chrome"], "LINK": colors["silverHardware"], "10-0130": colors["silverHardware"], "15-0548": colors["chrome"], "15-0325": colors["chrome"], 
                "15-0329": colors["permMat"], "15-0326": colors["permMat"], "15-1070": colors["permBlack"], "15-1073": colors["permBlack"], "15-1063": colors["permBlack"], "15-1068": colors["chrome"], "15-0741": colors["permBlack"], "20-0117": colors["plastic"],
                "10-0025": colors["silverHardware"], "15-1075": colors["permBlack"], "15-1066": colors["permBlack"], "15-1133": colors["permBlack"], "15-1065": colors["permBlack"], "15-0349": colors["permBlack"], "10-0628": colors["silverHardware"],
                "15-0350": colors["permBlack"], "15-1047": colors["permBlack"], "15-0884": colors["permBlack"], "15-0345": colors["permBlack"], "15-0567": colors["permBlack"], "15-0570": colors["permBlack"], "15-1372": colors["permBlack"], "CABLE": colors["permBlack"],
                "LEFT": colors["permBlack"], "RIGHT": colors["permBlack"], "15-1057": colors["permBlack"], "15-0345": colors["permBlack"], "15-0347": colors["permBlack"], "15-0346": colors["permBlack"], "15-1067": colors["permBlack"], "15-1045": colors["permBlack"],
                "15-0814": colors["permBlack"], "20-0116": colors["plastic"], "15-0322": colors["permMat"], "15-0324": colors["permMat"], "15-0323": colors["permMat"], "10-0161": colors["chrome"], "10-0062": colors["silverHardware"], "15-1233": colors["permBlack"],
                "15-1237": colors["permBlack"], "15-1230": colors["permBlack"], "15-1064": colors["permBlack"], "15-1380": colors["permBlack"], "10-0332": colors["permBlack"], "15-1247": colors["chrome"], "15-1233": colors["permBlack"], "10-0371": colors["silverHardware"],
                "15-1233": colors["permBlack"], "10-0017": colors["silverHardware"], "15-0943": colors["permBlack"], "20-0050": colors["plastic"], "10-0375": colors["silverHardware"], "15-0392": colors["silverHardware"], "10-0583": colors["rubber"],
                "20-0056": colors["plastic"], "10-0177": colors["plastic"], "20-0055": colors["plastic"], "15-0394": colors["chrome"], "15-1077": colors["chrome"], "15-1079": colors["chrome"], "10-0006": colors["permBlack"], "10-0208": colors["silverHardware"],
                "10-0104": colors["silverHardware"], "10-0020": colors["silverHardware"], "10-0078": colors["silverHardware"], "10-0021": colors["silverHardware"], "10-0033": colors["silverHardware"], "15-0549": colors["chrome"], "10-0223": colors["chrome"], 
                "15-1078": colors["chrome"], "10-0166": colors["permBlack"], "10-0526": colors["permBlack"], "10-0421": colors["blackHardware"], "10-0445": colors["permBlack"], "10-0476": colors["permBlack"], "10-0171": colors["silverHardware"], 
                "10-0370": colors["silverHardware"], "10-0369": colors["silverHardware"], "15-0565": colors["permBlack"], "15-0566": colors["permBlack"], "10-0063": colors["plastic"], "15-0191": colors["chrome"], "10-0225": colors["rubber"], "15-0384": colors["permMat"],
                "15-0385": colors["permBlack"], "15-1103": colors["permMat"], "15-1105": colors["permBlack"], "15-1106": colors["permBlack"], "15-0667": colors["permBlack"], "15-0856": colors["permBlack"], "15-1379": colors["permBlack"], "15-0839": colors["permBlack"], 
                "10-0179": colors["chrome"], "15-1246": colors["permBlack"], "10-0072": colors["blackHardware"], "10-0475": colors["blackHardware"], "15-1072": colors["permBlack"], "15-1076": colors["permBlack"], "15-1074": colors["permBlack"],
                "10-0070": colors["plastic"], "15-0585": colors["permBlack"], "15-0554": colors["permBlack"], "15-1183": colors["permBlack"], "10-0167": colors["permBlack"], "10-0133": colors["silverHardware"], "10-0422": colors["blackHardware"],
                "10-0359": colors["permBlack"], "10-0015": colors["silverHardware"], "10-0172": colors["silverHardware"], "15-1236": colors["permBlack"], "15-1130": colors["permBlack"], "15-0557": colors["permBlack"], "15-1129": colors["permBlack"],
                "15-1214": colors["permBlack"], "10-0550": colors["permBlack"], "15-0552": colors["permBlack"], "15-0568": colors["permBlack"], "15-0553": colors["permBlack"], "15-1208": colors["permMat"], "15-1213": colors["permBlack"], "15-1211": colors["permBlack"],
                "15-1209": colors["permBlack"], "10-0253": colors["chrome"], "15-0344": colors["permBlack"], "15-0348": colors["permBlack"], "10-0294": colors["chrome"], "10-0620": colors["silverHardware"], "10-0527": colors["rubber"], "15-1044": colors["chrome"],
                "15-0817": colors["chrome"], "10-0327": colors["chrome"], "10-0098": colors["silverHardware"], "10-0349": colors["silverHardware"], "10-0515": colors["chrome"], "10-0508": colors["silverHardware"], "10-0016": colors["silverHardware"],
                "10-0331": colors["silverHardware"], "15-0341": colors["permBlack"], "20-0237": colors["cloth"], "20-0236": colors["rubber"], "15-0565": colors["permBlack"], "10-0036": colors["silverHardware"], "15-1215": colors["permBlack"], "15-1212": colors["chrome"],
                "10-0409": colors["permBlack"], "15-1218": colors["chrome"], "10-0314": colors["blackHardware"], "15-0560": colors["permBlack"], "15-0559": colors["permBlack"], "15-0558": colors["plastic"], "10-0164": colors["blackHardware"], "15-0556": colors["plastic"],
                "15-0832": colors["permBlack"], "10-0226": colors["plastic"], "15-0573": colors["permBlack"], "10-0227": colors["chrome"], "10-0126": colors["plastic"], "20-0240": colors["cloth"], "15-1444": colors["plastic"], "15-1210": colors["permBlack"], 
                "10-0232": colors["silverHardware"], "10-0233": colors["silverHardware"], "15-1217": colors["permMat"], "15-1446": colors["plastic"], "15-0393": colors["permBlack"], "15-1111": colors["permBlack"], "15-1112": colors["permBlack"], "15-1381": colors["permBlack"],
                "20-0296": colors["cloth"], "15-1962": colors["permBlack"], "15-1962": colors["permBlack"], "15-2071": colors["permBlack"], "15-2067": colors["permBlack"],"15-1971": colors["permBlack"], "15-1970": colors["permBlack"], "15-1963": colors["permBlack"], 
                "15-2068": colors["permBlack"], "10-0925": colors["permBlack"], "15-1942": colors["permBlack"], "15-1953": colors["permBlack"], "15-2074": colors["permBlack"], "15-1958": colors["permBlack"], "15-1952": colors["permBlack"], "15-1958": colors["permBlack"],
                "10-0065": colors["silverHardware"], "P15-1781": colors["chrome"], "15-0941": colors["chrome"], "15-0940": colors["chrome"], "15-0939": colors["chrome"], "15-1967": colors["chrome"], "10-0924": colors["permBlack"], "15-1972": colors["permBlack"],
                "15-1973": colors["permBlack"], "15-1975": colors["permBlack"], "15-1974": colors["permBlack"], "15-1959": colors["permBlack"], "15-1945": colors["chrome"], "10-0821": colors["chrome"], "10-0419": colors["blackHardware"], "10-0418": colors["silverHardware"],
                "10-0773": colors["silverHardware"], "15-1960": colors["permBlack"], "15-2075": colors["permBlack"], "15-1961": colors["permBlack"], "15-1946": colors["permBlack"], "15-1944": colors["permBlack"], "20-0320": colors["plastic"], "15-1798": colors["permBlack"],
                "15-1943": colors["permBlack"], "10-0928": colors["silverHardware"], "15-1423": colors["chrome"], "15-2072": colors["permBlack"], "15-2070": colors["permBlack"], "15-2073": colors["permBlack"], "15-2069": colors["permBlack"], "15-2066": colors["permBlack"],
                "10-0328": colors["rubber"], "1_am": colors["permBlack"], "10-0485_TB": colors["blackHardware"], "15-1950": colors["permBlack"], "P15-1782": colors["chrome"], "15-2187": colors["permBlack"], "15-2186": colors["permBlack"], "15-2211": colors["chrome"],
                "10-0950": colors["chrome"], "15-2201": colors["chrome"], "15-1965": colors["permBlack"], "15-1966": colors["permMat"], "15-1951": colors["permMat"], "10-0815": colors["blackHardware"], "10-0818": colors["blackHardware"], "10-0813": colors["blackHardware"],
                "bolt_2am": colors["blackHardware"], "10-0423": colors["silverHardware"], "15-2079": colors["silverHardware"], "10-0622": colors["pulleys"], "15-1949": colors["silverHardware"], "20-0132": colors["plastic"], "10-0435": colors["silverHardware"],
                "15-1590": colors["permBlack"], "15-1573": colors["permBlack"], "20-0336": colors["plastic"], "10-0762": colors["silverHardware"], "15-1800": colors["chrome"], "20-0322": colors["plastic"], "10-0507": colors["silverHardware"], "10-0763": colors["blackHardware"],
                "15-1964": colors["chrome"], "10-0951": colors["chrome"], "10-0376": colors["silverHardware"], "nut_1_am": colors["blackHardware"], "10-0811": colors["blackHardware"], "regular_1_2_am": colors["blackHardware"], "15-1957": colors["chrome"], "10-0037": colors["silverHardware"],
                "15-1789": colors["permBlack"], "15-1790": colors["permBlack"], "15-1821": colors["permBlack"], "15-1820": colors["permBlack"], "10-0765": colors["rubber"], "15-1791": colors["permBlack"], "15-1705": colors["chrome"], "15-1793": colors["permBlack"],
                "15-1706": colors["chrome"], "10-0768": colors["permBlack"], "10-0360": colors["plastic"], "P20-0307": colors["rubber"], "10-0487": colors["blackHardware"], "15-1804": colors["chrome"], "10-0424": colors["blackHardware"], "15-0317": colors["UC"][str(color)],
                "15-2042": colors["permBlack"], "15-2078": colors["silverHardware"], "20-0357": colors["plastic"], "10-0906": colors["silverHardware"], "15-2043": colors["permBlack"], "RIGHT-1": colors["permBlack"], "LEFT-1": colors["permBlack"], "15-2090": colors["chrome"],
                "nut": colors["silverHardware"], "bolt": colors["silverHardware"], "regular": colors["silverHardware"], "10-0485": colors["blackHardware"], "15-2198": colors["UC"]["white"], "15-1842": colors["UC"]["clear coat"], "15-1852": colors["UC"]["white"],
                "15-1838": colors["permBlack"], "15-1837": colors["permBlack"], "15-1828": colors["permBlack"], "15-1614": colors["permBlack"], "15-2212": colors["permBlack"], "15-2213": colors["permBlack"], "15-2200": colors["permBlack"], "15-1889": colors["permBlack"],
                "15-1841": colors["permBlack"], "15-1835": colors["permBlack"], "15-2001": colors["permBlack"], "15-1827": colors["permBlack"], "15-1885": colors["permBlack"], "15-1853": colors["UC"]["white"], "15-1829": colors["permBlack"], "15-1830": colors["permBlack"],
                "15-1999": colors["chrome"], "15-1893": colors["permBlack"], "15-1900": colors["permBlack"], "15-1901": colors["permBlack"], "15-1832": colors["permBlack"], "10-0771": colors["permBlack"], "20-0313": colors["permMat"], "20-0312": colors["permMat"],
                "20-0314": colors["permMat"], "15-1846": colors["permBlack"], "15-1847": colors["permBlack"], "15-1848": colors["permBlack"], "15-1719": colors["permBlack"], "15-1851": colors["permBlack"], "15-1849": colors["permBlack"], "15-1850": colors["permBlack"],
                "10-0793": colors["silverHardware"], "15-1620": colors["permBlack"], "15-1646": colors["permBlack"], "10-0758": colors["silverHardware"], "15-1836": colors["chrome"], "15-1633": colors["permBlack"], "15-1833": colors["permBlack"], "15-1886": colors["permBlack"],
                "10-0907": colors["blackHardware"], "10-0776": colors["blackHardware"], "15-1844": colors["permBlack"], "10-0431": colors["blackHardware"], "10-0725": colors["blackHardware"], "10-0695": colors["blackHardware"], "10-0760": colors["silverHardware"],
                "20-0321": colors["plastic"], "15-0387": colors["permBlack"], "15-1834": colors["chrome"], "15-1854": colors["permBlack"], "15-1882": colors["permBlack"], "15-1615": colors["permBlack"], "10-0490": colors["blackHardware"], "15-2199": colors["permBlack"],
                "15-1803": colors["rubber"], "15-1754": colors["permBlack"], "10-0780": colors["blackHardware"], "15-1895": colors["permBlack"], "10-0781": colors["blackHardware"], "10-0782": colors["plastic"], "15-1776": colors["permBlack"], "15-1908": colors["permBlack"], "10-0777": colors["silverHardware"],
                "15-1902": colors["chrome"], "15-1905": colors["permBlack"], "15-1907": colors["permBlack"], "15-1904": colors["permBlack"], "15-1906": colors["permBlack"], "15-1903": colors["permBlack"], "10-0723": colors["blackHardware"], "10-0724": colors["blackHardware"],
                "15-1877": colors["permBlack"], "10-0757": colors["silverHardware"], "20-0346": colors["rubber"], "15-2000": colors["chrome"], "20-0235": colors["cloth"], "20-0250": colors["cloth"], "20-0188": colors["cloth"], "20-0251": colors["cloth"], "15-1601": colors["UC"][str(color)], 
                "15-1591": colors["UC"][str(color)], "15-1596": colors["UC"][str(color)], "15-1091": colors["UC"][str(color)], "15-1600": colors["UC"][str(color)], "15-1090": colors["UC"][str(color)], "15-1592": colors["UC"][str(color)], "15-1595": colors["UC"][str(color)],
                "15-1595": colors["UC"][str(color)], "15-1594": colors["UC"][str(color)], "15-0952": colors["UC"][str(color)], "15-0951": colors["UC"][str(color)], "10-0090": colors["rubber"], "15-1546": colors["UC"][str(color)], "15-1599": colors["UC"][str(color)],
                "15-1099": colors["UC"][str(color)], "15-1598": colors["UC"][str(color)], "15-1597": colors["UC"][str(color)], "15-1098": colors["chrome"], "10-0087": colors["plastic"], "10-0706": colors["permBlack"], "10-0437": colors["permBlack"], "15-0964": colors["chrome"], 
                "15-1005": colors["permBlack"], "20-0272": colors["plastic"], "15-1093": colors["chrome"], "15-1386": colors["permBlack"], "20-0165": colors["rubber"], "15-1100": colors["permBlack"], "15-1115": colors["permBlack"], "15-1098": colors["chrome"], "15-1173": colors["permBlack"],
                "15-1363": colors["chrome"], "15-1113": colors["chrome"], "15-1364": colors["chrome"], "10-0707": colors["blackHardware"], "10-0439": colors["blackHardware"], "10-0438": colors["blackHardware"], "10-0449": colors["blackHardware"], "10-0443": colors["blackHardware"], "10-0478": colors["blackHardware"],
                "10-0441": colors["blackHardware"], "10-0429": colors["blackHardware"], "10-0444": colors["blackHardware"], "10-0674": colors["blackHardware"], "10-0428": colors["blackHardware"], "10-0449": colors["blackHardware"], "10-0436": colors["blackHardware"], 
                "10-0449": colors["blackHardware"], "10-0673": colors["blackHardware"], "10-0461": colors["blackHardware"], "10-0449": colors["blackHardware"], "15-1172": colors["blackHardware"], "10-0404": colors["blackHardware"], "10-0615": colors["blackHardware"], 
                "15-1593": colors["permBlack"], "10-0280": colors["blackHardware"], "10-0209": colors["rubber"], "15-1166": colors["rubber"], "10-0067": colors["blackHardware"], "10-0391": colors["blackHardware"], "15-0367": colors["permBlack"], "15-0355": colors["permBlack"],
                "15-0357": colors["permBlack"], "15-0358": colors["permBlack"], "15-0367": colors["permBlack"], "LOWER-1": colors["permBlack"], "UPPER-1": colors["permBlack"], "15-0339": colors["permBlack"], "15-0386": colors["permBlack"], "15-0825": colors["permBlack"], "15-0352": colors["permBlack"],
                "15-0378": colors["permBlack"], "15-0380": colors["permBlack"], "15-0377": colors["permBlack"], "15-0379": colors["permBlack"], "15-0367": colors["permBlack"], "15-0340": colors["permBlack"], "15-0353": colors["permBlack"], "15-0342": colors["permBlack"],
                "15-1127": colors["permBlack"], "15-1060": colors["permBlack"], "20-0130": colors["plastic"], "15-0354": colors["permBlack"], "15-0368": colors["permBlack"], "15-0375": colors["permBlack"], "15-0374": colors["permBlack"], "15-0376": colors["permBlack"],
                "15-0383": colors["chrome"], "15-0809": colors["permBlack"], "10-0410": colors["plastic"], "15-0934": colors["permBlack"], "15-0979": colors["permBlack"], "15-0351": colors["permBlack"], "15-0333": colors["permBlack"], "15-0335": colors["permBlack"],
                "15-0337": colors["permBlack"], "15-0338": colors["permBlack"], "15-0370": colors["permBlack"], "15-1012": colors["permBlack"], "15-1227": colors["permBlack"], "20-0150": colors["plastic"], "(Hangin": colors["cloth"], "15-0336": colors["permBlack"],
                "10-0325": colors["rubber"], "15-0371": colors["permBlack"], "15-0372": colors["permBlack"], "15-0369": colors["permBlack"], "15-0373": colors["permBlack"], "15-0807": colors["permBlack"], "15-1059": colors["permBlack"], "15-0388": colors["chrome"],
                "15-0819": colors["permBlack"], "10-0174": colors["permBlack"], "15-0382": colors["permBlack"], "15-0834": colors["permBlack"], "15-0359": colors["permBlack"], "15-0824": colors["permBlack"], "15-0366": colors["permBlack"], "15-0836": colors["permBlack"],
                "15-1122": colors["permBlack"], "15-0835": colors["permBlack"], "15-0360": colors["permBlack"], "15-03363": colors["permBlack"], "15-0808": colors["permBlack"], "15-0362": colors["permBlack"], "15-0364": colors["permBlack"], "15-0361": colors["permBlack"],
                "15-0365": colors["permBlack"], "15-0363": colors["permBlack"], "15-0823": colors["permBlack"], "15-0816": colors["permBlack"], "15-0815": colors["chrome"], "lanyard": colors["chrome"], "15-0381": colors["permBlack"], "10-0525": colors["blackHardware"],
                "10-0523": colors["blackHardware"], "10-0524": colors["blackHardware"], "15-1228": colors["permBlack"], "10-0377": colors["silverHardware"], "10-0086": colors["silverHardware"], "20-0131": colors["plastic"], "10-0024": colors["silverHardware"],
                "10-0023": colors["silverHardware"], "10-0146": colors["silverHardware"], "15-0397": colors["chrome"], "10-0286": colors["plastic"], "10-0156": colors["silverHardware"], "10-0326": colors["silverHardware"], "15-1275": colors["permBlack"], "15-1276": colors["permBlack"],
                "4-1": colors["permBlack"], "15-0391": colors["permBlack"], "15-1206": colors["permBlack"], "15-1069": colors["chrome"], "15-0968": colors["chrome"], "P15-178": colors["chrome"], "LEFT-2": colors["chrome"], "--54C-1": colors["silverHardware"],
                "15-1678": colors["permMat"], "15-1674": colors["permMat"], "15-1671": colors["permMat"], "15-1672": colors["permMat"], "15-1491": colors["permMat"], "15-1669": colors["permMat"], "--D-C-3": colors["silverHardware"], "--D-C-1": colors["silverHardware"],
                "P15-128": colors["UC"][str(color)], "15-1681": colors["permBlack"], "15-1609": colors["permBlack"], "15-1610": colors["permBlack"], "15-1284": colors["permBlack"], "15-1282": colors["permBlack"], "15-1285": colors["permBlack"], "10-0114": colors["blackHardware"],
                "15-1248": colors["UC"][str(color)], "15-1249": colors["UC"][str(color)], "15-0224": colors["UC"][str(color)], "15-1253": colors["UC"][str(color)], "15-1252": colors["UC"][str(color)], "15-1250": colors["UC"][str(color)], "15-1286": colors["permBlack"],
                "15-1611": colors["permBlack"], "CABLE-1": colors["permBlack"], "LINK-1": colors["silverHardware"], "LINK-2": colors["silverHardware"], "LINK-3": colors["silverHardware"], "LINK-4": colors["silverHardware"], "LINK-5": colors["silverHardware"],
                "15-1454": colors["permBlack"], "15-1453": colors["permBlack"], "20-0171": colors["plastic"], "15-1035": colors["permBlack"], "15-1036": colors["permBlack"], "15-1421": colors["permBlack"], "10-0612": colors["blackHardware"], "15-1455": colors["permBlack"],
                "15-0416": colors["permBlack"], "15-0418": colors["permBlack"], "15-0401": colors["permBlack"], "15-0415": colors["permBlack"], "15-0400": colors["permBlack"], "15-0413": colors["permBlack"], "20-0051": colors["plastic"], "15-1035": colors["permBlack"],
                "20-0054": colors["plastic"], "15-0298": colors["permBlack"], "20-0041": colors["plastic"], "10-0053": colors["blackHardware"], "20-0164": colors["plastic"], "20-0129": colors["plastic"], "15-1050": colors["permBlack"], "20-0214": colors["plastic"],
                "15-1051": colors["permBlack"], "15-0407": colors["permBlack"], "15-0409": colors["permBlack"], "15-0410": colors["permBlack"], "15-0411": colors["permBlack"], "15-0408": colors["permBlack"], "10-0230": colors["permBlack"], "10-0553": colors["silverHardware"],
                "10-0229": colors["permBlack"], "15-1216": colors["permBlack"], "15-1141": colors["permBlack"], "10-0235": colors["permBlack"], "10-0234": colors["permBlack"], "15-0583": colors["chrome"], "RF-0013": colors["silverHardware"], "10-0057": colors["silverHardware"],
                "15-0408": colors["permBlack"], "REVISED": colors["cloth"], "20-0155": colors["plastic"], "20-0156": colors["permBlack"], "15-0408": colors["permBlack"], "15-1031": colors["plastic"], "15-1032": colors["plastic"], "15-1030": colors["chrome"], "15-0245": colors["permBlack"],
                "15-0246": colors["permBlack"], "15-0244": colors["permBlack"], "15-0243": colors["permBlack"], "15-003088": colors["UC"][str(color)], '15-1053': colors['permBlack'], '15-1052': colors['permBlack'], '15-0450': colors['permBlack'], '15-0447': colors['permBlack'], 
                '15-0451': colors['permBlack'], '15-0452': colors['permBlack'], '15-0449': colors['permBlack'], '10-0189': colors['chrome'], '20-0065': colors['permBlack'], '20-0215': colors['plastic'], '20-0063': colors['plastic'], '20-0062': colors['plastic'], "20-003035": colors["plastic"],
                "15-003040": colors["permBlack"], "10-0662": colors["blackHardware"], "-54C": colors["silverHardware"], "10-003269": colors["chrome"], "10-0420": colors["blackHardware"], "15-003106": colors["permBlack"], "15-003110": colors["permBlack"], "15-003112": colors["permBlack"],
                "15-003113": colors["permBlack"], "15-003107": colors["permBlack"], "15-003111": colors["permBlack"], "15-1344": colors["permBlack"], "15-1323": colors["permBlack"], "15-1341": colors["permBlack"], "15-1335": colors["permBlack"], "15-1348": colors["permBlack"],
                "15-1316": colors["permBlack"], "15-1336": colors["permBlack"], "15-1313": colors["permBlack"], "15-1696": colors["permBlack"], "15-1737": colors["permBlack"], "15-1780": colors["chrome"],"15-2013": colors["permBlack"], "15-1357": colors["permBlack"], "15-1356": colors["permBlack"],
                "10-0590": colors["rubber"], "15-1782": colors["chrome"], "10-003320": colors["blackHardware"], "10-0662": colors["blackHardware"], "15-1781": colors["permBlack"], "15-1342": colors["permBlack"], "15-1326": colors["permBlack"], "15-1338": colors["chrome"],
                "15-1751": colors["permBlack"], "15-1796": colors["permBlack"], "15-1333": colors["permBlack"], "20-0206": colors["plastic"], "15-1362": colors["permBlack"], "10-0794": colors["blackHardware"], "15-1561": colors["permBlack"], "20-0276": colors["plastic"],
                "10-0580": colors["blackHardware"], "15-1899": colors["chrome"], "15-2022": colors["permBlack"], "10-0430": colors["blackHardware"], "10-0660": colors["rubber"], "10-0735": colors["blackHardware"], "15-1896": colors["permBlack"], "15-1695": colors["permBlack"],
                "15-1354": colors["permBlack"], "15-1760": colors["permBlack"], "10-0797": colors["silverHardware"], "15-1749": colors["permBlack"], "10-0810": colors["blackHardware"], "15-1347": colors["permBlack"], "15-1550": colors["permBlack"], "15-1794": colors["permBlack"], 
                "15-1750": colors["permBlack"], "15-1334": colors["chrome"], "15-1795": colors["permBlack"], "15-1898": colors["permBlack"], "15-1352": colors["chrome"], "15-1349": colors["chrome"], "15-1350": colors["permBlack"], "15-1346": colors["permBlack"],
                "20-0259": colors["plastic"], "15-1697": colors["permBlack"], "10-0124": colors["silverHardware"], "10-0788": colors["blackHardware"], "15-1355": colors["permBlack"], "15-1856": colors["permBlack"], "15-1761": colors["permBlack"], "15-1332": colors["permBlack"],
                "15-1331": colors["permBlack"], "15-1312": colors["permBlack"], "15-1319": colors["permBlack"], "10-0736": colors["blackHardware"], "10-0082": colors["blackHardware"], "20-003033": colors["plastic"], "10-0551": colors["blackHardware"], "15-1361": colors["permBlack"],
                "15-1317": colors["permBlack"], "15-1345": colors["permBlack"], "10-0546": colors["blackHardware"], "15-1343": colors["permBlack"], "10-0809": colors["blackHardware"], "15-1872": colors["chrome"], "20-0324": colors["plastic"], "15-1318": colors["permBlack"], 
                "10-0598": colors["silverHardware"], "10-0599": colors["silverHardware"], "15-003148": colors["chrome"], "15-003149": colors["chrome"], "10-003154": colors["silverHardware"], "10-003152": colors["silverHardware"], "15-003150": colors["chrome"],
                "20-0307": colors["rubber"], "15-2002": colors["permBlack"], "15-2006": colors["permBlack"], "20-0343": colors["rubber"], "20-0342": colors["rubber"], "15-003071": colors["permBlack"], "15-003072": colors["permBlack"], "15-003073": colors["permBlack"],
                "15-2003": colors["permBlack"], "15-2005": colors["permBlack"], "10-0828": colors["blackHardware"], "10-0819": colors["blackHardware"], "20-0344": colors["plastic"], "15-1917": colors["permBlack"], "10-003083": colors["permBlack"], "10-0890": colors["blackHardware"],
                "15-1925": colors["permBlack"], "15-1924": colors["permBlack"], "15-1916": colors["chrome"], "15-1927": colors["permBlack"], "10-0804": colors["blackHardware"], "15-1926": colors["permBlack"], "15-1920": colors["chrome"], "15-1918": colors["permBlack"], 
                "15-1994": colors["plastic"], "10-003156": colors["blackHardware"], "10-0801": colors["blackHardware"], "15-1919": colors["permBlack"], "15-1995": colors["permBlack"], "10-0945": colors["silverHardware"], "15-1922": colors["blackHardware"], "20-0372": colors["plastic"], 
                "15-1928": colors["chrome"], "20-0334": colors["plastic"], "20-0335": colors["plastic"], "10-0800": colors["blackHardware"], "10-003064": colors["blackHardware"], "20-0228": colors["plastic"], "20-0227": colors["plastic"], "20-0230": colors["rubber"], "15-1413": colors["plastic"],
                "15-1398": colors["permBlack"], "20-0223": colors["plastic"], "15-1404": colors["permBlack"], "20-0231": colors["rubber"], "20-0229": colors["plastic"], "15-1399": colors["permBlack"], "20-0297": colors["plastic"], "15-1403": colors["chrome"], "20-0224": colors["plastic"],
                "15-1397": colors["permBlack"], "15-1405": colors["chrome"], "10-0656": colors["blackHardware"], "15-1400": colors["permBlack"], "20-0225": colors["permBlack"], "20-0232": colors["UC"]["red"], "20-0222": colors["UC"]["red"], "20-0218": colors["plastic"],
                "10-0651": colors["blackHardware"], "10-0657": colors["blackHardware"], "20-0219": colors["plastic"], "15-1411": colors["plastic"], "10-0609": colors["blackHardware"], "20-0221": colors["plastic"], "20-0220": colors["plastic"], "15-1410": colors["plastic"],
                "15-1392": colors["permBlack"], "15-1409": colors["permBlack"], "15-003108": colors["permBlack"], "15-003109": colors["permBlack"], "15-1315": colors["permBlack"], "15-1360": colors["permBlack"], "15-1314": colors["permBlack"], "15-2014": colors["permBlack"],
                "10-0593": colors["blackHardware"], "10-0737": colors["rubber"], "10-0486": colors["silverHardware"], "10-0581": colors["blackHardware"], "15-1843": colors["permBlack"], "15-1358": colors["permBlack"], "15-1330": colors["permBlack"], "15-003067": colors["chrome"],
                "15-1921": colors["permBlack"], "15-1923": colors["permBlack"], "10-0902": colors["silverHardware"], "15-1752": colors["permBlack"], "20-0301": colors["permBlack"], "10-0597": colors["silverHardware"], "20-0302": colors["permBlack"], "10-0595": colors["permBlack"],
                "10-0596": colors["permBlack"], "20-0347": colors["plastic"], "15-1642": colors["permBlack"], "15-1652": colors["chrome"], "15-1627": colors["permBlack"], "15-1629": colors["permBlack"], "15-1740": colors["permMat"], "15-1745": colors["permMat"], "15-1744": colors["permMat"],
                "15-1742": colors["permMat"], "15-1741": colors["permMat"], "15-1636": colors["permBlack"], "15-1634": colors["permBlack"], "15-1651": colors["permBlack"], "15-1617": colors["permBlack"], "15-1625": colors["chrome"], "15-1709": colors["permBlack"], "15-1644": colors["permBlack"],
                "10-0759": colors["silverHardware"], "10-0694": colors["permBlack"], "15-1640": colors["permBlack"], "15-1641": colors["permBlack"], "15-1639": colors["permBlack"], "15-1818": colors["chrome"], "15-1637": colors["permBlack"], "15-1649": colors["permBlack"],
                "10-0746": colors["blackHardware"], "10-0696": colors["blackHardware"], "10-0766": colors["plastic"], "15-1635": colors["chrome"], "20-0289": colors["plastic"], "15-1628": colors["permBlack"], "15-1638": colors["permBlack"], "15-1616": colors["permBlack"],
                "15-1650": colors["permBlack"], "15-1743": colors["permBlack"], "10-0718": colors["blackHardware"], "15-1771": colors["chrome"], "15-1792": colors["permBlack"], "40-0117": colors["permBlack"], "ASSEMBLED-1": colors["permBlack"], "WALL-BACKER": colors["permBlack"],
                "10-0654": colors["blackHardware"], "15-1288": colors["permBlack"], "15-1284": colors["permBlack"], "15-1282": colors["permBlack"], "15-1287": colors["UC"][str(color)], "15-1289": colors["permBlack"], "15-1702": colors["permBlack"], "15-1496": colors["permBlack"], 
                "15-1554": colors["permBlack"], "15-1497": colors["permBlack"], "15-1767": colors["permBlack"], "15-1556": colors["permBlack"], "10-0566": colors["rubber"], "15-1290": colors["permBlack"], "15-1293": colors["permBlack"], "15-1562": colors["permBlack"], 
                "10-003069": colors["rubber"], "15-0088": colors["chrome"], "15-0086": colors["permBlack"], "15-0085": colors["permBlack"], "15-0081": colors["permBlack"], "15-0080": colors["permBlack"], "15-0083": colors["permBlack"], "15-0082": colors["permBlack"],
                "15-0084": colors["permBlack"], "10-0048": colors["permBlack"], "10-0066": colors["permBlack"], "15-0155": colors["chrome"], "10-0077": colors["silverHardware"], "10-0069": colors["silverHardware"], "10-0079": colors["silverHardware"], "10-0081": colors["silverHardware"],
                "15-1647": colors["chrome"], "10-0775": colors["blackHardware"], "15-1648": colors["UC"][str(color)], "10-0601": colors['permBlack'], "10-0600": colors['silverHardware'], "15-1897": colors['permBlack'], "10-0767": colors['silverHardware'], "10-0824": colors['blackHardware'],
                "15-1353": colors['permBlack'], "10-0717": colors['silverHardware'], "10-0786": colors['blackHardware'], "10-0787": colors['silverHardware'], "10-0425": colors['blackHardware'], "10-0186": colors['blackHardware'], "20-0076": colors["plastic"], "15-0300": colors["permBlack"],
                "15-0501": colors["permBlack"], "15-0299": colors["permBlack"], "15-0302": colors["permBlack"], "10-0162": colors["blackHardware"], "20-0077": colors["permBlack"], "15-0396": colors["permBlack"],"20-0186": colors["cloth"], "20-0187": colors["cloth"], "20-0045": colors["plastic"],
                "15-0491": colors["permBlack"], "20-0075": colors["plastic"], "15-0109": colors["permBlack"], "15-0059": colors["permBlack"], "15-0019": colors["permBlack"], "15-0054": colors["permBlack"], "15-0022": colors["permBlack"], "15-0167": colors["permBlack"], "20-0025": colors["plastic"],
                "15-0067": colors["chrome"], "15-0021": colors["permBlack"], "15-0057": colors["permBlack"], "10-0094": colors["permBlack"], "10-0050": colors["permBlack"], "10-0022": colors["silverHardware"], "10-0010": colors["silverHardware"], "10-0045": colors["silverHardware"],
                "10-0188": colors["silverHardware"], "20-0026": colors["plastic"], "10-0018": colors["silverHardware"], "10-0032": colors["silverHardware"], "15-1280": colors["UC"][str(color)], "15-1292": colors["UC"][str(color)], "P15-1287": colors["UC"][str(color)], 
                "15-1668": colors["UC"][str(color)], "15-1679": colors["permBlack"], "15-1676": colors["permBlack"], "15-1693": colors["permBlack"], "10-0578": colors["silverHardware"], "10-0630": colors["silverHardware"], "10-0661": colors["silverHardware"], "10-0381": colors["silverHardware"],
                "15-1675": colors["UC"][str(color)], "15-1677": colors["UC"][str(color)], "15-1049": colors["permBlack"], "15-1048": colors["permBlack"], "20-0213": colors["plastic"], "15-1420": colors["permBlack"], "15-0225": colors["permBlack"], "15-0226": colors["permBlack"],
                "15-0229": colors["permBlack"], "15-0230": colors["chrome"], "10-0144": colors["silverHardware"], "15-0453": colors["chrome"], "15-0454": colors["permBlack"], "10-0187": colors["chrome"], "15-0462": colors["permBlack"], "15-0460": colors["permBlack"], "15-0469": colors["permBlack"],
                "15-0459": colors["permBlack"], "15-0488": colors["permBlack"], "20-0066": colors["plastic"], "15-1049": colors["permBlack"], "20-0067": colors["plastic"], "20-0001": colors["plastic"], "15-0461": colors["permBlack"], "15-1391": colors["permBlack"], "15-1011": colors["permBlack"],
                "15-1049": colors["permBlack"], "20-0185": colors["plastic"], "15-2194": colors["permBlack"], "15-2193": colors["permBlack"], "15-003384": colors["rubber"], "20-003509": colors["rubber"], "10-0460": colors["blackHardware"], "15-0903": colors["permMat"],
                "15-0905": colors["permMat"], "10-0417": colors["silverHardware"], "15-0900": colors["permMat"], "15-0901": colors["chrome"], "15-2193": colors["permMat"], "15-0492": colors["permBlack"], "10-0192": colors["silverHardware"], "15-0494": colors["permBlack"],
                "15-0493": colors["permBlack"], "15-1058": colors["permBlack"], "20-0049": colors["plastic"], "10-0252": colors["chrome"], "20-0333": colors["plastic"], "15-1407": colors["permBlack"], "20-0226": colors["plastic"], "10-0658": colors["plastic"], "15-1395": colors["plastic"],
                "15-1393": colors["plastic"], "15-1229": colors["permBlack"], "15-1109": colors["permBlack"], "15-1104": colors["permBlack"], "10-0330": colors["permBlack"], "15-0569": colors["permBlack"], "15-0026": colors["permBlack"], "10-0224": colors["permBlack"],
                "15-1108": colors["permBlack"], "10-0382": colors["silverHardware"], "10-0451": colors["plastic"], "15-1557": colors["permBlack"], "15-1758": colors["permBlack"], "15-0660": colors["permBlack"], "15-1563": colors["permBlack"], "15-0748": colors["permBlack"],
                "20-0304": colors["plastic"], "20-0303": colors["plastic"], "15-1558": colors["permBlack"], "15-1759": colors["permBlack"], "20-0306": colors["permBlack"], "10-0742": colors["permBlack"], "15-1718": colors["chrome"], "15-1509": colors["permBlack"], "20-0159": colors["plastic"],
                "20-0160": colors["plastic"], "10-0514": colors["silverHardware"], "10-0517": colors["permBlack"], "15-1582": colors["chrome"], "15-1580": colors["permBlack"], "15-1575": colors["permBlack"], "15-1579": colors["permBlack"], "15-1574": colors["permBlack"],
                "10-0715": colors["permBlack"], "15-1692": colors["permBlack"], "15-1691": colors["permBlack"], "15-1568": colors["permBlack"], "15-1565": colors["permBlack"], "RF-0013B": colors["chrome"], "15-1566": colors["permBlack"], "15-1577": colors["permBlack"],
                "15-1581": colors["chrome"], "15-1713": colors["permBlack"], "15-1714": colors["permBlack"], "15-1570": colors["permBlack"], "10-0047": colors["permBlack"], "15-1576": colors["permBlack"], "15-1701": colors["permBlack"], "10-0683": colors["permBlack"],
                "15-1774": colors["permBlack"], "15-1567": colors["permBlack"], "15-1785": colors["permBlack"], "15-1587": colors["permBlack"], "15-1585": colors["permBlack"], "15-1584": colors["permBlack"], "15-1583": colors["permBlack"], "15-0201": colors["permBlack"],
                "15-0190": colors["permBlack"], "15-0092": colors["permBlack"], "10-0682": colors["permBlack"], "15-1773": colors["permBlack"], "15-1586": colors["permBlack"], "10-0680": colors["permBlack"], "15-1588": colors["permBlack"], "15-1700": colors["permBlack"],
                "20-0277": colors["permBlack"], "10-0714": colors["permBlack"], "10-0160": colors["permBlack"], "10-0112": colors["permMat"], "15-0205": colors["chrome"], "15-0189": colors["permBlack"], "15-1715": colors["permBlack"], "20-0310": colors["permBlack"],
                "15-0090": colors["permBlack"], "15-0091": colors["permBlack"], "15-0093": colors["permBlack"], "15-0094": colors["permBlack"], "15-0099": colors["permBlack"], "15-0098": colors["permBlack"], "15-0100": colors["permBlack"], "15-0095": colors["permBlack"],
                "15-0096": colors["permBlack"], "10-0113": colors["silverHardware"], "15-0097": colors["permBlack"], "10-0049": colors["permBlack"], "15-0103": colors["permBlack"], "15-0611": colors["permBlack"], "15-0102": colors["chrome"], "15-0101": colors["chrome"],
                "15-0105": colors["permBlack"], "15-0104": colors["permBlack"], "15-0108": colors["permBlack"], "15-0106": colors["permBlack"], "15-0107": colors["permBlack"], "20-0015": colors["plastic"], "20-0138": colors["permBlack"], "10-0084": colors["silverHardware"],
                "20-0080": colors["plastic"], "15-0517": colors["permBlack"], "15-0512": colors["UC"][str(color)], "15-0514": colors["UC"][str(color)], "15-0513": colors["UC"][str(color)], "15-0518": colors["UC"][str(color)], "15-0515": colors["UC"][str(color)],
                "15-0511": colors["UC"][str(color)], "15-0519": colors["UC"][str(color)], "10-0200": colors["UC"][str(color)], "15-0516": colors["UC"][str(color)], "15-0509": colors['chrome'], "10-0201": colors['rubber'], "10-0311": colors["silverHardware"],
                "10-0207": colors["silverHardware"], "10-0080": colors["silverHardware"], "15-0510": colors["UC"][str(color)], "20-0078": colors["permMat"], "15-0503": colors["UC"][str(color)], "15-0506": colors["UC"][str(color)], "15-0508": colors["UC"][str(color)], 
                "15-0504": colors["UC"][str(color)], "15-0502": colors["UC"][str(color)], "15-0505": colors["UC"][str(color)], "15-0507": colors["UC"][str(color)], "20-0233": colors["permMat"], "20-0212": colors["permMat"], "20-0211": colors["permMat"],
                "15-0506": colors["UC"][str(color)], "15-1263": colors["UC"][str(color)], "15-1083": colors["UC"][str(color)], "15-1088": colors["UC"][str(color)], "15-1080": colors["UC"][str(color)], "15-1086": colors["UC"][str(color)], "15-1085": colors["UC"][str(color)], 
                "15-1270": colors["UC"][str(color)], "15-1226": colors["UC"][str(color)], "15-1082": colors["UC"][str(color)], "15-1377": colors["UC"][str(color)], "15-1268": colors["UC"][str(color)], "10-0543": colors["UC"][str(color)], "15-1274": colors["UC"][str(color)], 
                "15-1378": colors["UC"][str(color)], "10-0212": colors["UC"][str(color)], "10-0542": colors["UC"][str(color)], "15-1376": colors["UC"][str(color)], "15-1271": colors["UC"][str(color)], "15-0858": colors["UC"][str(color)], "15-1299": colors["UC"][str(color)], 
                "15-1272": colors["UC"][str(color)], "15-1225": colors["UC"][str(color)], "10-0268": colors["UC"][str(color)], "15-0548": colors["silverHardware"], "15-1087": colors["UC"][str(color)], "15-1084": colors["UC"][str(color)], "15-1273": colors["UC"][str(color)], 
                "15-1089": colors["UC"][str(color)], "20-0167": colors["plastic"], "10-0547": colors["plastic"], "10-0434": colors["silverHardware"], "10-0324": colors["silverHardware"], "10-0548": colors["silverHardware"], "15-003101": colors["plastic"],
                "15-0117": colors["chrome"], "15-0111": colors["permBlack"], "15-0110": colors["permBlack"], "15-0118": colors["permBlack"], "10-0074": colors["rubber"], "15-0115": colors["permBlack"], "15-0116": colors["permBlack"], "15-0112": colors["permBlack"], 
                "15-0114": colors["permBlack"], "15-0113": colors["permBlack"], "10-0115": colors["silverHardware"], "10-0011": colors["silverHardware"], "10-0465": colors["silverHardware"], "15-1447": colors["chrome"], "15-1448": colors["chrome"], "15-0987": colors["chrome"],
                "15-1178": colors["permBlack"], "15-0077": colors["permBlack"], "10-0626": colors["silverHardware"], "10-0228": colors["silverHardware"], "15-1177": colors["silverHardware"], "10-0643": colors["silverHardware"], "15-1723": colors["permBlack"],
                "15-1722": colors["rubber"], "15-0850": colors["permBlack"], "15-0849": colors["silverHardware"], "15-0744": colors["chrome"], "15-0855": colors["permBlack"], "15-0853": colors["permBlack"], "10-003555": colors["silverHardware"],
                "15-0810": colors["permBlack"], "15-1390": colors["permBlack"], "15-1784": colors["chrome"], "20-0257": colors["permBlack"], "20-0265": colors["permBlack"], "20-0249": colors["permBlack"], "15-1932": colors["permBlack"], "15-1806": colors["permBlack"],
                "15-1503": colors["permBlack"], "15-1516": colors["permBlack"], "15-1505": colors["permBlack"], "15-1506": colors["permBlack"], "15-1512": colors["permBlack"], "15-1521": colors["chrome"], "10-0663": colors["chrome"], "15-1514": colors["permBlack"],
                "20-0354": colors["permBlack"], "15-1734": colors["permBlack"],} 

    collection = bpy.data.collections.get("Model")
    for obj in collection.objects:
        # Clear all existing materials. Blender gets weird when you start stacking a bunch of colors on top of each other
        obj.data.materials.clear()
        print("Materials cleared from", obj.name, "successfully!")

    # This is the list of materials in the file
    material = bpy.data.materials[0]

    # Iterate through all models in the "Model" collection 
    for obj in collection.objects:
        # Assign the material to the model, different functions depending on if the model is in the dictionary
        if obj.data.materials and obj.name.split(" ")[0] in materials:
            obj.data.materials[0] = bpy.data.materials[materials[obj.name.split(" ")[0]]]
        elif obj.name.split(" ")[0] in materials:
            obj.data.materials.append(bpy.data.materials[materials[obj.name.split(" ")[0]]])
        else:
            obj.data.materials.append(material)
        print("Material assigned to ", obj.name, " successfully!")

    collection = bpy.data.collections.get("Model")
    for subcollection in collection.children:
        for obj in subcollection.objects:
            # Clear all existing materials
            obj.data.materials.clear()
            print("Materials cleared from", obj.name, "successfully!")

            # Material List again
            material = bpy.data.materials[0]

            # Assign the material to the model
            if obj.data.materials and obj.name.split(" ")[0] in materials:
                obj.data.materials[0] = bpy.data.materials[materials[obj.name.split(" ")[0]]]
            elif obj.name.split(" ")[0] in materials:
                obj.data.materials.append(bpy.data.materials[materials[obj.name.split(" ")[0]]])
            else:
                obj.data.materials.append(material)
            print("Material assigned to ", obj.name, " successfully!")

if __name__ == "__main__":
    register()
