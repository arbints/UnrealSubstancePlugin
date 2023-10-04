import os.path

import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
from PySide2 import QtWidgets
import pathlib
import shutil
import remote_execution

plugin_widgets = []

def export_to_unreal():
    if not substance_painter.project.is_open():
        print("please open a project")
        return

    stacks = substance_painter.textureset.all_texture_sets()
    export_preset = substance_painter.resource.ResourceID(
        context="starter_assets",
        name="Unreal Engine 4 (Packed)"
    )

    project_path = substance_painter.project.file_path()
    project_dir = pathlib.Path(project_path).parent.resolve()
    project_name = substance_painter.project.name()
    export_path = f'{project_dir}\\{project_name}'

    export_list = []
    for stack in stacks:
        export_list.append({"rootPath": str(stack)})

    config = {
        "exportShaderParams" : False,
        "exportPath" : export_path,
        "exportList" : export_list,
        "defaultExportPreset" : export_preset.url(),
        "exportParameters":
        [
            {
                "parameters":
                {
                    "fileFormat" : "tga",
                    "bitDepth" : "8",
                    "dithering" : True,
                    "paddingAlgorithm" : "infinite"
                }
            }
        ]
    }
    if os.path.exists(export_path): #if the path exists
        shutil.rmtree(export_path)
    export_result = substance_painter.export.export_project_textures(config)
    fbx_file = substance_painter.project.last_imported_mesh_path()
    shutil.copy(fbx_file, export_path)

    lib_path = f'{pathlib.Path(__file__).parent.parent.resolve()}\\modules\\UnrealSubstanceLibrary.py'

    lines = []
    with open(lib_path, 'r') as lib:
        lines = lib.readlines()
    read_path = export_path.replace('\\', '/')
    lines.append(f'\nUnrealSubstanceLibrary().ImportAndBuildFromPath(\'{read_path}\')')

    cmd = ''.join(lines)
    remote_exc = remote_execution.RemoteExecution()
    remote_exc.start()
    remote_exc.open_command_connection(remote_exc.remote_nodes)
    remote_exc.run_command(cmd)
    remote_exc.stop()

def start_plugin():
    print("plugin started")
    #this creates an action
    Action = QtWidgets.QAction("Export To Unreal", triggered=export_to_unreal)
    plugin_widgets.append(Action)
    #this add the action to the file menu
    substance_painter.ui.add_action(substance_painter.ui.ApplicationMenu.File, Action)

def close_plugin():
    print("plugin closed")
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)

    plugin_widgets.clear()