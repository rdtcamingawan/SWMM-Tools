from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                                 QDialogButtonBox, QLabel
                                 )
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel

from .config import load_layer

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("SWMM Tools -- Configure Layer")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)

        # Short Explanation
        info = QLabel("Select all layers that SWMM Tools should use.")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Initialize a Form Layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # --- Subcatchment (Polygon) ---
        self.cmb_sub = QgsMapLayerComboBox()
        self.cmb_sub.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.cmb_sub.setAllowEmptyLayer(True)
        form.addRow("Subcatchment: ", self.cmb_sub)

        # --- Junctions (Point) ---
        self.cmb_junction = QgsMapLayerComboBox()
        self.cmb_junction.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.cmb_junction.setAllowEmptyLayer(True)
        form.addRow("Junction: ", self.cmb_junction)

        # --- Outfalls (Point) ---
        self.cmb_outfall = QgsMapLayerComboBox()
        self.cmb_outfall.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.cmb_outfall.setAllowEmptyLayer(True)
        form.addRow("Outfall: ", self.cmb_outfall)

        # Add all the combo boxes to the main layout
        layout.addLayout(form)

        #OK/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Pre-select previously selected layers
        self.cmb_sub.setLayer(load_layer("subcatchment_layer_id", "subcatchment_layer"))
        self.cmb_junction.setLayer(load_layer("junction_layer_id", "junction_layer"))
        self.cmb_outfall.setLayer(load_layer("outfall_layer_id", "outfall_layer"))


    def get_selected_layers(self):
        """Returns the layer the user chooses"""
        return {
            "subcatchment": self.cmb_sub.currentLayer(),
            "junction": self.cmb_junction.currentLayer(),
            "outfall": self.cmb_outfall.currentLayer()
        }



