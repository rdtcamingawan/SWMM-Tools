from qgis.PyQt.QtWidgets import QAction

class SWMMTools:
    def __init__(self, iface):
        self.iface = iface
        self.action_config = None
    def initGui(self):
        # Create an action
        self.action_config = QAction(
            "Configure Layers", 
            self.iface.mainWindow()
        )
        self.action_config.setToolTip("Configure SWMM layers")
        # Connect the action to a method
        self.action_config.triggered.connect(self.run_config)
        # Add to the Plugins menu
        self.iface.addPluginToMenu("&SWMM Tools", self.action_config)
    def unload(self):
        # Remove the menu item when pllugin is disabled
        if self.action_config:
            self.iface.removePluginMenu("&SWMM Tools", self.action_config)
    def run_config(self):
        from .config_dialog import ConfigDialog

        dialog = ConfigDialog(self.iface.mainWindow())
        result = dialog.exec()

        if not result: # user cancelled
            return

        # User clicked OK. Read layers
        layers = dialog.get_selected_layers()

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