import substance_painter.ui
import substance_painter.export
import substance_painter.project
import  substance_painter.textureset
from PySide2 import QtWidgets

plugin_widgets = []

def export_to_unreal():
    print("exporting")

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