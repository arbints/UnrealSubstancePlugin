import os
import unreal
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

        for mesh in meshes:
            self.BuildMaterialForMesh(mesh, textures)

    def BuildMaterialForMesh(self, mesh: unreal.StaticMesh, textures: list[unreal.Texture2D]):
        meshName = mesh.get_name()
        meshDir = unreal.Paths.get_path(mesh.get_path_name())
        materialFolder = meshDir + '/materials'

        if unreal.EditorAssetLibrary.does_directory_exist(materialFolder):
            unreal.EditorAssetLibrary.delete_directory(materialFolder)

        for index, materialElement in enumerate(mesh.static_materials):
            elemmentName = unreal.StringLibrary.conv_name_to_string(materialElement.material_slot_name)
            baseColor = None
            normal = None
            occlustionRoughnessMetalic = None
            for texture in textures:
                if meshName in texture.get_name() and elemmentName in texture.get_name():
                    if "BaseColor" in texture.get_name():
                        baseColor = texture
                    if "Normal" in texture.get_name():
                        normal = texture
                    if "OcclusionRoughnessMetallic" in texture.get_name():
                        occlustionRoughnessMetalic = texture

            print(f"find material element: {elemmentName} "
                  f"with base color: {baseColor.get_name()},"
                  f" normal: {normal.get_name()},"
                  f" occlusionRoughnessMetallic:{occlustionRoughnessMetalic.get_name()}")


            #1, create a material instance, with the name "MInst_" + elementName, and path: '/game/'+meshName + '/' + elementName
            matInst = unreal.AssetToolsHelpers().get_asset_tools().create_asset(
                asset_name="MInst_" + elemmentName,
                package_path=materialFolder + "/" + elemmentName,
                asset_class= unreal.MaterialInstanceConstant,
                factory=unreal.MaterialInstanceConstantFactoryNew()
            )

            #2 retrieve the base material
            baseMat = self.BuildBaseMaterial()

            #3, set up the parent of the material instance to the base material
            matInst.set_editor_property("parent", baseMat)

            #4, attach the 3 textures to the material instance
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(matInst, "BaseColor", baseColor)
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(matInst, "Normal", normal)
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(matInst, "OcclusionRoughnessMetallic", occlustionRoughnessMetalic)

            #5, assign the material
            mesh.set_material(index, matInst)

            unreal.EditorAssetLibrary.rename_asset(baseColor.get_path_name(),
                                                   materialFolder + "/" + elemmentName + '/' + baseColor.get_name())

            unreal.EditorAssetLibrary.rename_asset(normal.get_path_name(),
                                                   materialFolder + "/" + elemmentName + '/' + normal.get_name())

            unreal.EditorAssetLibrary.rename_asset(occlustionRoughnessMetalic.get_path_name(),
                                                   materialFolder + "/" + elemmentName + '/' + occlustionRoughnessMetalic.get_name())

            unreal.EditorAssetLibrary.save_asset(matInst.get_path_name())

        unreal.EditorAssetLibrary.save_asset(mesh.get_path_name())

    def BuildBaseMaterial(self):
        #asset tools is the object we can use to create assets.
        assetTools = unreal.AssetToolsHelpers.get_asset_tools()

        #checks if base material is alreay built, if so, just return it.
        if unreal.EditorAssetLibrary.does_asset_exist(self.rootDir+self.baseMaterialName):
            return unreal.EditorAssetLibrary.load_asset(self.rootDir+self.baseMaterialName)

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

        occulutionRoughnessMetailicParam.set_editor_property("parameter_name", "OcclusionRoughnessMetallic")

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "R",
                                                                unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "G",
                                                                unreal.MaterialProperty.MP_ROUGHNESS)

        unreal.MaterialEditingLibrary.connect_material_property(occulutionRoughnessMetailicParam, "B",
                                                                unreal.MaterialProperty.MP_METALLIC)

        unreal.EditorAssetLibrary.save_asset(baseMat.get_path_name())
        return baseMat

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
