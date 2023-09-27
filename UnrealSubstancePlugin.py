import os

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

        UnrealSubstanceLibrary().ImportAndBuildFromPath(path)

#where we have real code other than UI
class UnrealSubstanceLibrary:
    def __init__(self):
        self.rootDir = '/game/Substance/'
        self.baseMaterialName = 'Mtl_Substance_Base'

        #this is a temp folder for textures
        self.tempFolder = '/game/SubstancePluginTemp/'

    def ImportAndBuildFromPath(self, path):
        meshes = []
        textures = []
        for file in os.listdir(path):
            if '.fbx' in file:
                meshes.append(self.LoadMeshFromPath(path + "/" + file))
            else:
                textures.append(self.LoadTextureFromPath(path + "/" + file))





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

    def LoadMeshFromPath(self, path: str):
        #path = C:/Users/jili1/Downloads/assets/assets/Tiffa.fbx
        #path.split('/') -> [C:, Users, jili1, Downloads, assets, assets, Tiffa.fbx]
        # path.split('/')[-1] -> Tiffa.fbx [Tiffa, fbx]
        meshName = path.split('/')[-1].split('.')[0]
        print(f"importing: {path}")
        importTask = unreal.AssetImportTask()
        importTask.replace_existing = True
        importTask.filename = path #what we import.
        importTask.destination_path = '/game/' + meshName #the folder we import the mesh into
        importTask.save = True
        importTask.automated = True #we do not want to see the import option pop up.

        fbxImportOptions=unreal.FbxImportUI()
        fbxImportOptions.import_mesh=True
        fbxImportOptions.import_as_skeletal=False
        fbxImportOptions.static_mesh_import_data.combine_meshes=True
        fbxImportOptions.import_materials=False

        importTask.options = fbxImportOptions #set up the fbx import options to the task

        #ask unreal to do the import task
        unreal.AssetToolsHelpers().get_asset_tools().import_asset_tasks([importTask])

        return importTask.get_objects()[0]

    def LoadTextureFromPath(self, path: str):
        # add code here so all the textures should be imported as well:
        print(f"importing: {path}")
        importTask = unreal.AssetImportTask()
        importTask.replace_existing = True
        importTask.filename = path  # what we import.
        importTask.destination_path = self.tempFolder  # the folder we import the mesh into
        importTask.save = True
        importTask.automated = True  # we do not want to see the import option pop up.

        #ask unreal to do the import task
        unreal.AssetToolsHelpers().get_asset_tools().import_asset_tasks([importTask])

        return importTask.get_objects()[0]


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
        self.AddUICommandScript("ImportFromFolder", "Import From Folder", ImportFromPathScript())

        #needed to show newly added submenu
        toolMenus.refresh_all_widgets()


unrealSubstancePluginUI = UnrealSubstancePluginUI()
unrealSubstancePluginUI.InitUI()