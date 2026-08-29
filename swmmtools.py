from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os.path

from .config_dialog import ConfigDialog
from .assign_outlet import AssignOutletMapTool

class SWMMTools:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action_config = None
        self.canvas = self.iface.mapCanvas()
        self.action_outlet = None
        self.outlet_tool = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        # Create an action
        self.action_config = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            "Configure Layers", 
            self.iface.mainWindow()
        )
        self.action_config.setToolTip("Configure SWMM layers")
        # Connect the action to a method
        self.action_config.triggered.connect(self.run_config)
        # Add to the Plugins menu
        self.iface.addPluginToMenu("&SWMM Tools", self.action_config)
        self.iface.addToolBarIcon(self.action_config)

        # Assign Outlet
        self.action_outlet = QAction("Assign Outlet", self.iface.mainWindow())
        self.action_outlet.setToolTip("Click a subcatchment, then a node")
        self.action_outlet.setCheckable(True)
        self.action_outlet.triggered.connect(self.toggle_outlet_tool)
        self.iface.addPluginToMenu("&SWMM Tools", self.action_outlet)
        self.iface.addToolBarIcon(self.action_outlet)
        self.outlet_tool = AssignOutletMapTool(self.canvas, self)

    def toggle_outlet_tool(self, checked):
        if checked:
            self.canvas.setMapTool(self.outlet_tool)
        else:
            if self.canvas.mapTool() == self.outlet_tool:
                self.canvas.unsetMapTool(self.outlet_tool)
            self.outlet_tool.reset()
            
    def unload(self):
        # Remove the menu item when pllugin is disabled
        if self.action_config:
            self.iface.removePluginMenu("&SWMM Tools", self.action_config)
            self.iface.removeToolBarIcon(self.action_config)

        if self.action_outlet:
            self.iface.removePluginMenu("&SWMM Tools", self.action_outlet)
            self.iface.removeToolBarIcon(self.action_outlet)
        if self.canvas.mapTool() == self.outlet_tool:
            self.canvas.unsetMapTool(self.outlet_tool)
            
    def run_config(self):
        
        dialog = ConfigDialog(self.iface.mainWindow())
        result = dialog.exec() if hasattr(dialog, "exec") else dialog.exec()

        if not result: # user cancelled
            return

        # User clicked OK. Read layers
        layers = dialog.get_selected_layers()

        # Save the layers
        from .config import save_layers
        save_layers(
            subcatchment=layers["subcatchment"],
            junction=layers["junction"],
            outfall=layers["outfall"]
        )

        # Code block for push message (debugging)
        subcatchment = layers["subcatchment"]
        junction = layers["junction"]
        outfall = layers["outfall"]

        # sample result
        msg = []
        msg.append(f"Subcatchment: {subcatchment.name() if subcatchment else None}")
        msg.append(f"Junction: {junction.name() if junction else None}")
        msg.append(f"Outfall: {outfall.name() if outfall else None}")


        self.iface.messageBar().pushSuccess(
            "SWMM Tools",
            " | ".join(msg)
        )

        self.iface.messageBar().pushMessage(
            "SWMM Tools",
            "Layer configuration saved for this project."
        )