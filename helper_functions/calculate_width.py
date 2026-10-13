# Author: Richmond Dave T. Camingawan
# GitHub: https://github.com/rdtcamingawan/SWMM-Tools
# License: GNU General Public License v3.0

from qgis.core import QgsProject

from ..config import load_layer


class CalculateWidth:
    def __init__(self, iface):
        self.iface = iface
        self.bar = self.iface.messageBar()

    def calculate_width(self):
        sub_layer = load_layer("subcatchment_layer_id", "subcatchment_layer")
        flowpath_layer = load_layer("longest_flowpath_layer_id", "longest_flowpath_layer")

        if sub_layer is None:
            self.bar.pushCritical("Calculate Width", "Configure a subcatchment layer first!")
            return

        if flowpath_layer is None:
            self.bar.pushCritical("Calculate Width", "Configure a longest flowpath layer first!")
            return

        width_field = "Width"
        width_idx = sub_layer.fields().indexOf(width_field)
        if width_idx == -1:
            self.bar.pushCritical(
                "Calculate Width",
                f"Layer '{sub_layer.name()}' needs a field named '{width_field}'",
            )
            return

        flowpath_feats = list(flowpath_layer.getFeatures())
        sub_feats = list(sub_layer.getFeatures())

        started = False
        if not sub_layer.isEditable():
            started = sub_layer.startEditing()
            if not started:
                self.bar.pushCritical(
                    "Calculate Width",
                    f"Could not start editing '{sub_layer.name()}'.",
                )
                return

        updated = 0
        for sub_feat in sub_feats:
            sub_geom = sub_feat.geometry()
            total_length = 0.0

            for fp_feat in flowpath_feats:
                intersect = fp_feat.geometry().intersection(sub_geom)
                if not intersect.isEmpty():
                    total_length += intersect.length()

            if total_length > 0:
                area = sub_geom.area()
                width = area / total_length
                ok = sub_layer.changeAttributeValue(sub_feat.id(), width_idx, width)
                if ok:
                    updated += 1

        if started:
            if not sub_layer.commitChanges():
                errors = "; ".join(sub_layer.commitErrors())
                self.bar.pushCritical(
                    "Calculate Width",
                    f"Could not save widths. {errors}",
                )
                return

        sub_layer.triggerRepaint()
        self.bar.pushSuccess(
            "Calculate Width",
            f"Updated {updated} subcatchment(s).",
        )