# Author: Richmond Dave T. Camingawan
# GitHub: https://github.com/rdtcamingawan/SWMM-Tools
# License: GNU General Public License v3.0

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsWkbTypes, QgsGeometry, QgsFeatureRequest)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolIdentify

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

        self.identify_tool = QgsMapToolIdentify(self.canvas)

        self.rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber.setColor(QColor(0, 120, 255, 80))
        self.rubber.setWidth(3)

        self.reset()

    def reset(self):
        self.selected_sub_fid = None
        self.rubber.reset(QgsWkbTypes.PolygonGeometry)

    def load_layers(self):
        bar = self.plugin.iface.messageBar()
        self.sub_layer = load_layer("subcatchment_layer_id", "subcatchment_layer")
        junction = load_layer("junction_layer_id", "junction_layer")
        outfall = load_layer("outfall_layer_id", "outfall_layer")

        if self.sub_layer is None:
            bar.pushCritical("Assign Outlet", "Configure a subcatchment layer first!")
            return False

        # Should one of the input nodes is missing
        self.node_layers = [layer for layer in (junction, outfall) if layer is not None]
        
        if not self.node_layers:
            bar.pushCritical("Assign Outlet", "Configure a node layer first!")
            return False

        if self.sub_layer.fields().indexOf(OUTLET_FIELD) == -1:
            bar.pushCritical(
                "Assign Outlet",
                f"Layer '{self.sub_layer.name()}' needs a field named "
                f"'{OUTLET_FIELD}'"
                )
            return False

        for layer in self.node_layers:
            if layer.fields().indexOf(NODE_ID_FIELD) == -1:
                bar.pushCritical(
                    "Assign Outlet",
                    f"Layer '{layer.name()}' needs a field named "
                    f"'{NODE_ID_FIELD}'"
                )
                return False

        return True

    def activate(self):
        super().activate()
        self.reset()

        if not self.load_layers():
            if self.plugin.action_outlet:
                self.plugin.action_outlet.setChecked(False)
            self.canvas.unsetMapTool(self)

    def deactivate(self):
        self.reset()

        if self.plugin.action_outlet:
                self.plugin.action_outlet.blockSignals(True)
                self.plugin.action_outlet.setChecked(False)
                self.plugin.action_outlet.blockSignals(False)
        super().deactivate()
    

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.reset()
        if event.button()  != Qt.LeftButton:
            return
        if self.selected_sub_fid is None:
            self._pick_subcatchment(event)
        else:
            self._pick_node(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset()

    def _identify(self, event, layers):
        results = self.identify_tool.identify(
            event.x(),
            event.y(),
            layerList=layers,
        )
        return results[0] if results else None

    def _pick_subcatchment(self, event):
        bar = self.plugin.iface.messageBar()
        result = self.identify_tool(event, [self.sub_layer])

        if result is None:
            bar.pushWarning("Assign Outlet: ",
                            "No Subcatchment selected.")
            return

        feature = result.mFeature
        self.selected_sub_fid = feature.id()
        self.rubber.setToGeometry(feature.geometry(), self.sub_layer)

        bar.pushInfo("Assign Outlet: ",
                     "Subcatchment selected. Click a junction or outfall.")
        
    def _pick_node(self, event):
        bar = self.plugin.iface.messageBar()
        result = self._identify(event, self.node_layers)

        if result is None:
            bar.pushWarning(
                "Assign Outlet",
                "No junction or outfall selected.",
            )
            return

        feature = result.mFeature
        node_layer = result.mLayer
        node_id = feature[NODE_ID_FIELD]

        if node_id is None or str(node_id).strip() == "":
            bar.pushWarning(
                "Assign Outlet",
                f"Selected feature has an empty '{NODE_ID_FIELD}' field.",
            )
            return

        self._write_outlet(str(node_id), node_layer)

    def _write_outlet(self, node_id, node_layer):
        bar = self.plugin.iface.messageBar()
        field_idx = self.sub_layer.fields().indexOf(OUTLET_FIELD)
        
        started_editing = False
        if not self.sub_layer.isEditable():
            started_editing = self.sub_layer.startEditing()
            if not started_editing:
                bar.pushCritical(
                    "Assign Outlet",
                    f"Could not start editing '{self.sub_layer.name()}'.",
                )
                return

        ok = self.sub_layer.changeAttributeValue(
            self.selected_sub_fid,
            field_idx,
            node_id,
        )

        if not ok:
            if started_editing:
                self.sub_layer.rollBack()
            bar.pushCritical(
                "Assign Outlet",
                "Could not write outlet node.",
            )
            return
        
        if started_editing:
            if not self.sub_layer.commitChanges():
                errors = "; ".join(self.sub_layer.commitErrors())
                bar.pushCritical(
                    "Assign Outlet",
                    f"Could not save outlet assignment. {errors}",
                )
                return

        self.sub_layer.triggerRepaint()
        bar.pushSuccess(
            "Assign Outlet",
            f"Outlet -> {node_id} ({node_layer.name()})",
        )
        self.reset()









    


