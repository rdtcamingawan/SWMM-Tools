from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os.path

from .config_dialog import ConfigDialog
from .assign_outlet import AssignOutletMapTool
from .helper_functions.calculate_width import CalculateWidth
from .helper_functions.assign_conduit_node import assign_node

class SWMMTools:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action_config = None
        self.canvas = self.iface.mapCanvas()
        self.action_outlet = None
        self.outlet_tool = None
        self.action_width = None
        self.action_assign_node = None

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

        # Calculate Width
        self.action_width = QAction("Calculate Width", self.iface.mainWindow())
        self.action_width.setToolTip("Calculate subcatchment width from longest flowpath")
        self.action_width.triggered.connect(self.run_calculate_width)
        self.iface.addPluginToMenu("&SWMM Tools", self.action_width)
        self.iface.addToolBarIcon(self.action_width)

        # Assign Conduit Nodes
        self.action_assign_node = QAction("Assign Conduit Node", self.iface.mainWindow())
        self.action_assign_node.triggered.connect(self.run_assign_conduit_node)
        self.iface.addPluginToMenu("&SWMM Tools", self.action_assign_node)

        # Initialize list of QActions
        self.actions = [
            self.action_config,
            self.action_outlet,
            self.action_width,
            self.action_assign_node,
        ]

    def toggle_outlet_tool(self, checked):
        if checked:
            self.canvas.setMapTool(self.outlet_tool)
        else:
            if self.canvas.mapTool() == self.outlet_tool:
                self.canvas.unsetMapTool(self.outlet_tool)
            self.outlet_tool.reset()
            
    def unload(self):
        # Unset map tool
        if self.canvas.mapTool() == self.outlet_tool:
            self.canvas.unsetMapTool(self.outlet_tool)

        # Remove everything
        for action in self.actions:
            if not action:
                continue

            # Menu
            self.iface.removePluginMenu("&SWMM Tools", action)

            # Toolbar
            try:
                self.iface.removeToolBarIcon(action)
            except Exception:
                try:
                    # fallback
                    pass
                except Exception:
                    continue
            
    def run_config(self):
        
        dialog = ConfigDialog(self.iface.mainWindow())
        result = dialog.exec() if hasattr(dialog, "exec") else dialog.exec()

        if not result: # user cancelled
            return

        # User clicked OK. Read layers
        layers = dialog.get_selected_layers()
        fields = dialog.get_assign_outlet_fields()

        # Save the layers
        from .config import save_layers, save_outlet_fields
        save_layers(
            subcatchment=layers["subcatchment"],
            junction=layers["junction"],
            outfall=layers["outfall"],
            conduit=layers["conduit"],
            longest_flowpath=layers["longest_flowpath"],
        )

        save_outlet_fields(
            outlet_field=fields["outlet_field"],
            junction_id_field=fields["junction_id_field"],
            outfall_id_field=fields["outfall_id_field"],
        )   

        # Code block for push message (debugging)
        subcatchment = layers["subcatchment"]
        junction = layers["junction"]
        outfall = layers["outfall"]
        flowpath = layers["longest_flowpath"]

        # sample result
        msg = []
        msg.append(f"Subcatchment: {subcatchment.name() if subcatchment else None}")
        msg.append(f"Junction: {junction.name() if junction else None}")
        msg.append(f"Outfall: {outfall.name() if outfall else None}")
        msg.append(f"Longest Flowpath: {flowpath.name() if flowpath else None}")

        self.iface.messageBar().pushSuccess(
            "SWMM Tools",
            " | ".join(msg)
        )

        self.iface.messageBar().pushMessage(
            "SWMM Tools",
            "Layer configuration saved for this project."
        )

    def run_calculate_width(self):
        tool = CalculateWidth(self.iface)
        tool.calculate_width()

    def run_assign_conduit_node(self):
        assign_node()
        
