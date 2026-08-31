from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsWkbTypes, QgsGeometry, QgsFeatureRequest)
from qgis.gui import QgsMapTool, QgsRubberBand

from qgis.core import QgsMapTool

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

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.reset()
        if event.button()  != Qt.LeftButton:
            return

        click_point = self.toMapCoordinates(event.pos())
        click_geom = QgsGeometry.fromPointXY(click_point)

        if self.selected_sub_fid is None:
            self._pick_subcatchment(click_point, click_geom)
        else:
            self._pick_node(click_geom)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset()

    def deactivate(self):
        self.reset()
        if self.plugin.action_outlet:
                self.plugin.action_outlet.blockSignals(True)
                self.plugin.action_outlet.setChecked(False)
                self.plugin.action_outlet.blockSignals(False)
        super().deactivate()

    def _pick_subcatchment(self, click_point, click_geom):
        bar = self.plugin.iface.messageBar()
        request = QgsFeatureRequest().setFilterRect(click_geom.boundingBox())
        found = None
        for feat in self.sub_layer.getFeatures(request):
            geom = feat.geometry()
            if geom.contains(click_point) or geom.intersects(click_geom):
                found = feat
                break
        if found is None:
            bar.pushWarning("Assign Outlet", "No subcatchment selected!")

        self.selected_sub_fid = found.id()
        self.rubber.setToGeometry(found.geometry(), self.sub_layer)
        bar.pushInfo("Assign Outlet", "Subcatchment selected. Click on a node to assign outlet.")

    def _pick_node(self, click_geom):
        bar = self.plugin.iface.messageBar()
        nearest = None
        nearest_layer = None
        min_dist = float("inf")
        tolerance = 50.0

        for lyr in self.node_layers:
            for feat in lyr.getFeatures():
                dist = feat.geometry().distance(click_geom)
                if dist < min_dist:
                    min_dist = dist
                    nearest = feat
                    nearest_layer = lyr

        if nearest is None or min_dist > tolerance:
            bar.pushWarning("Assign Outlet", 
                            "No close nodes. Click near a node.")

        node_id = nearest[NODE_ID_FIELD]
        if node_id is None or str(node_id).strip() == "":
            bar.pushWarning("Assign Outlet",
                            "Node has an empty Name field")
            return
        self._write_outlet(str(node_id), nearest_layer)

    def _write_outlet(self, node_id, node_layer):
        bar = self.plugin.iface.messageBar()
        field_idx = self.sub_layer.fields().indexOf(OUTLET_FIELD)

        if not self.sub_layer.isEditable():
            self.sub_layer.startEditing()

        ok = self.sub_layer.changeAttributeValue(
            self.selected_sub_fid, field_idx, node_id
        )

        if ok:
            self.sub_layer.commitChanges()
            self.sub_layer.triggerRepaint()
            bar.pushSuccess("Assign Outlet",
                            f"Outlet -> {node_id} ({node_layer.name()})")
        else:
            self.sub_layer.rollBack()
            bar.pushCritical("Assign Outlet",
                             "Could not write outlet node.")

        self.reset()









    


