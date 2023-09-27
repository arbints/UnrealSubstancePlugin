import unreal
import tkinter
from tkinter import filedialog

@unreal.uclass()
class BuildSubstanceMaterialScript(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None: #execute when click.
        UnrealSubstanceLibrary().BuildBaseMaterial()

@unreal.uclass()
class ImportFromPathScript(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context):
        window = tkinter.Tk()
        window.withdraw()
        path = filedialog.askdirectory()
        window.destroy()

        print(f"importing from path: {path}")


class UnrealSubstanceLibrary:
    def __init__(self):
        self.rootDir = '/game/Substance/'
        self.baseMaterialName = 'Mtl_Substance_Base'

    def BuildBaseMaterial(self):
        #asset tools is the object we can use to create assets.
        assetTools = unreal.AssetToolsHelpers.get_asset_tools()
        baseMat = assetTools.create_asset(self.baseMaterialName, self.rootDir, unreal.Material, unreal.MaterialFactoryNew())

        baseColorParam = unreal.MaterialEditingLibrary.create_material_expression(material=baseMat,
                                                                                  expression_class=unreal.MaterialExpressionTextureSampleParameter2D,
                                                                                  node_pos_x=-800,
                                                                                  node_pos_y=0
                                                                                  )
        baseColorParam.set_editor_property("parameter_name", "BaseColor")

        unreal.MaterialEditingLibrary.connect_material_property(baseColorParam,
                                                "RGB",
                                                                unreal.MaterialProperty.MP_BASE_COLOR)


        normalParam = unreal.MaterialEditingLibrary.create_material_expression(material=baseMat,
                                                                               expression_class=unreal.MaterialExpressionTextureSampleParameter2D,
                                                                               node_pos_x=-800,
                                                                               node_pos_y=400,
                                                                               )
        normalParam.set_editor_property("parameter_name", "Normal")
        defaultNormalMap = unreal.EditorAssetLibrary.load_asset('/Engine/EngineMaterials/DefaultNormal')
        normalParam.set_editor_property("texture", defaultNormalMap)
        unreal.MaterialEditingLibrary.connect_material_property(normalParam, "RGB", unreal.MaterialProperty.MP_NORMAL)


        occulutionRoughnessMetailicParam = unreal.MaterialEditingLibrary.create_material_expression(baseMat,
                                                                                                    unreal.MaterialExpressionTextureSampleParameter2D,
                                                                                                    -800,
                                                                                                    800
                                                                                                    )

        occulutionRoughnessMetailicParam.set_editor_property("parameter_name", "OcclusionRoughnessMetalic")

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "R",
                                                                unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "G",
                                                                unreal.MaterialProperty.MP_ROUGHNESS)

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "B",
                                                                unreal.MaterialProperty.MP_METALLIC)

        unreal.EditorAssetLibrary.save_asset(baseMat.get_path_name())

class UnrealSubstancePluginUI:
    def __init__(self):
        self.submenuName = "SubstancePlugins"
        self.submenuLabel = "Substance Plugins"
        self.subMenu = None

    def AddUICommandScript(self, name:str, label:str, script: unreal.ToolMenuEntryScript):
        script.init_entry(
            owner_name=self.subMenu.menu_name,
            menu=self.subMenu.menu_name,
            section="",
            name=name,
            label=label
        )
        #registering so the system will update and show it. without it will not apear.
        script.register_menu_entry()

    def InitUI(self):
        #tool menus is the object that handles meun stuff.
        toolMenus = unreal.ToolMenus().get()

        #this give us the main menu that we can do something about it.
        mainMenu = toolMenus.find_menu("LevelEditor.MainMenu")

        self.subMenu = mainMenu.add_sub_menu(owner=mainMenu.get_name(),#the name of the ower
                                        section_name="", #which section it belongs to, main menu has no section
                                        name=self.submenuName, #the name of the submenu
                                        label=self.submenuLabel #the label of the submeun
                                        )
        #this adds the button
        self.AddUICommandScript("CreateSubstanceMaterial", "Create Base Substance Material", BuildSubstanceMaterialScript())

        #needed to show newly added submenu
        toolMenus.refresh_all_widgets()


unrealSubstancePluginUI = UnrealSubstancePluginUI()
unrealSubstancePluginUI.InitUI()