import unreal

@unreal.uclass()
class BuildSubstanceMaterialScript(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None: #execute when click.
        print("excuting command!!!!")


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