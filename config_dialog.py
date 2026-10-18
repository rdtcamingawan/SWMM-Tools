from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                                 QDialogButtonBox, QLabel, QToolButton,
                                 QWidget
                                 )
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.core import QgsMapLayerProxyModel

from .config import load_layer, load_outlet_fields

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

        # --- Longest Flowpath (Line) ---
        self.cmb_conduit = QgsMapLayerComboBox()
        self.cmb_conduit.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.cmb_conduit.setAllowEmptyLayer(True)
        form.addRow("Conduit: ", self.cmb_conduit)
        
        # --- Longest Flowpath (Line) ---
        self.cmb_flowpath = QgsMapLayerComboBox()
        self.cmb_flowpath.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.cmb_flowpath.setAllowEmptyLayer(True)
        form.addRow("Longest Flowpath: ", self.cmb_flowpath)

        # Add all the combo boxes to the main layout
        layout.addLayout(form)

        # Assign outlet fields
        self.btn_assign_outlet_fields = QToolButton()
        self.btn_assign_outlet_fields.setText("Assign Outlet Fields")
        self.btn_assign_outlet_fields.setCheckable(True)
        self.btn_assign_outlet_fields.setChecked(False)
        self.btn_assign_outlet_fields.setArrowType(Qt.RightArrow)
        self.btn_assign_outlet_fields.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        layout.addWidget(self.btn_assign_outlet_fields)

        self.assign_outlet_fields_widget = QWidget()
        fields_form = QFormLayout(self.assign_outlet_fields_widget)
        fields_form.setLabelAlignment(Qt.AlignRight)

        # Subcatchment Outlet Field
        self.cmb_outlet_field = QgsFieldComboBox()
        fields_form.addRow("Outlet Field: ", self.cmb_outlet_field)

        # Junction node ID field
        self.cmb_junction_id_field = QgsFieldComboBox()
        fields_form.addRow("Junction ID field:", self.cmb_junction_id_field)

        # Outfall node ID field
        self.cmb_outfall_id_field = QgsFieldComboBox()
        fields_form.addRow("Outfall ID field:", self.cmb_outfall_id_field)

        self.assign_outlet_fields_widget.setVisible(False)
        layout.addWidget(self.assign_outlet_fields_widget)

        # Connect selected layers to their field selectors
        self.cmb_sub.layerChanged.connect(
            self.cmb_outlet_field.setLayer
        )
        self.cmb_junction.layerChanged.connect(
            self.cmb_junction_id_field.setLayer
        )
        self.cmb_outfall.layerChanged.connect(
            self.cmb_outfall_id_field.setLayer
        )

        # Expand / collapse
        self.btn_assign_outlet_fields.toggled.connect(
            self._toggle_assign_outlet_fields
        )

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
        self.cmb_conduit.setLayer(load_layer("conduit_layer_id", "conduit_layer"))
        self.cmb_flowpath.setLayer(load_layer("longest_flowpath_layer_id", "longest_flowpath_layer"))


        # Pre-select previously selected outlet fields
        fields = load_outlet_fields()
        
        self.cmb_outlet_field.setLayer(self.cmb_sub.currentLayer())
        self.cmb_junction_id_field.setLayer(self.cmb_junction.currentLayer())
        self.cmb_outfall_id_field.setLayer(self.cmb_outfall.currentLayer())
        
        if fields["outlet_field"]:
            self.cmb_outlet_field.setField(fields["outlet_field"])
        if fields["junction_id_field"]:
            self.cmb_junction_id_field.setField(fields["junction_id_field"])
        if fields["outfall_id_field"]:
            self.cmb_outfall_id_field.setField(fields["outfall_id_field"])

    def _toggle_assign_outlet_fields(self, checked):
        self.assign_outlet_fields_widget.setVisible(checked)
        self.btn_assign_outlet_fields.setArrowType(
            Qt.DownArrow if checked else Qt.RightArrow
        )
    
    def get_selected_layers(self):
        """Returns the layer the user chooses"""
        return {
            "subcatchment": self.cmb_sub.currentLayer(),
            "junction": self.cmb_junction.currentLayer(),
            "outfall": self.cmb_outfall.currentLayer(),
            "conduit": self.cmb_conduit.currentLayer(),
            "longest_flowpath": self.cmb_flowpath.currentLayer(),
        }

    def get_assign_outlet_fields(self):
        """Return the fields used by the Assign Outlet tool."""
        return {
            "outlet_field": self.cmb_outlet_field.currentField(),
            "junction_id_field": self.cmb_junction_id_field.currentField(),
            "outfall_id_field": self.cmb_outfall_id_field.currentField(),
        }



