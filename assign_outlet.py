from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsWkbTypes
from qgis.gui import QgsMapTool, QgsRubberBand

from .config import load_layer

OUTLET_FIELD = "Outlet"
NODE_ID_FIELD = "Name"

class AssignOutletMapTool(QgsMapTool):
    def __init__(self, canvas, plugin):
        super().__init__(canvas)
        self.canvas = canvas
        self.plugin = plugin
        self.setCursor(Qt.CrossCursor)

        self.sub_layer = None
        self.node_layers = []
        self.selected_sub_fid = None

        self.rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber.setColor(QColor(0, 120, 255, 80))
        self.rubber.setWidth(3)

        self.reset()

    def reset(self):
        self.selected_sub_fid = None
        self.rubber.reset(QgsWkbTypes.PolygonGeometry)

    def load_layers(self):
        self.sub_layer = load_layer("subcatchment_layer_id", "subcatchment_layer")
        junction = load_layer("junction_layer_id", "juntion_layer")
        outfall = load_layer("outfall_layer_id", "outfall_layer")

        bar = self.plugin.iface.messageBar()

        if self.sub_layer is None:
            bar.pushCritical("Assign Outlet", "Configure a subcatchment layer first!")
            return False
        if junction is None or outfall is None:
            bar.pushCritical("Assign Outlet", "Configure a node layer first!")
            return False
        if self.sub_layer.fields().indexOf(OUTLET_FIELD) == -1:
            bar.pushCritical("Assign Outlet", "Subcatchment layer needs a text field named Outlet.")
            return False

        for lyr in (junction, outfall):
            if lyr.fields().indexOf(NODE_ID_FIELD) == -1:
                bar.pushCritical(
                    "Assign Outlet",
                    f"Layer: '{lyr.name()}' needs a field named Name",
                    )
                return False

        self.node_layers = [junction, outfall]
        return True

    def activate(self):
        super().activate()
        self.reset()
        if not self.load_layers():
            self.plugin.action_outlet.setChecked(False)
            self.canvas.unsetMapTool(self)


    


