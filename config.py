from qgis.core import QgsProject

_GROUP = "SWMMTools"

def save_layers(
        subcatchment:None,
        junction:None,
        outfall:None,
        longest_flowpath=None):
    # Initialize QgsProject
    proj = QgsProject.instance()

    def _write(layer, name_key, id_key):
        if layer:
            proj.writeEntry(_GROUP, name_key, layer.name())
            proj.writeEntry(_GROUP, id_key, layer.id())
        else:
            proj.writeEntry(_GROUP, name_key, "")
            proj.writeEntry(_GROUP, id_key, "")

    _write(subcatchment, "subcatchment_layer", "subcatchment_layer_id")
    _write(junction, "junction_layer", "junction_layer_id")
    _write(outfall, "outfall_layer", "outfall_layer_id")
    _write(longest_flowpath, "longest_flowpath_layer", "longest_flowpath_layer_id")

def load_layer(id_key, name_key):
    proj = QgsProject.instance()

    # Stores layer ID
    layer_id = proj.readEntry(_GROUP, id_key, "")[0]

    if layer_id:
        layer = proj.mapLayer(layer_id)
        if layer:
            return layer

    # Uses name, if layer id fails
    name = proj.readEntry(_GROUP, name_key, "")[0]
    if name:
        layers = proj.mapLayersByName(name)
        if layers:
            return layers[0]

def save_outlet_fields(outlet_field, junction_id_field, outfall_id_field):
    proj = QgsProject.instance()
    proj.writeEntry(_GROUP, "outlet_field", outlet_field or "")
    proj.writeEntry(_GROUP, "junction_id_field", junction_id_field or "")
    proj.writeEntry(_GROUP, "outfall_id_field", outfall_id_field or "")

def load_outlet_fields():
    proj = QgsProject.instance()
    return {
        "outlet_field": proj.readEntry(_GROUP, "outlet_field", "")[0],
        "junction_id_field": proj.readEntry(_GROUP, "junction_id_field", "")[0],
        "outfall_id_field": proj.readEntry(_GROUP, "outfall_id_field", "")[0],
    }
