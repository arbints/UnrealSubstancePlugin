
import unreal
import tkinter
from UnrealSubstanceLibrary import UnrealSubstanceLibrary
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