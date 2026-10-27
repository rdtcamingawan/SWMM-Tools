from qgis.core import QgsFeatureRequest, QgsProject
def get_node_elevation(node_layers, node_name):
    expression = f"\"Name\" = \'{node_name}\'"
    request = QgsFeatureRequest().setFilterExpression(expression)
    for layer in node_layers:
        request = [f["Name"] for f in layer.getFeautures(request)]
    request = node_layers.getFeatures(request)
    return [f["Elevation"] for f in request]

proj = QgsProject.instance()
# Nodes
junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]
outfall_layer = proj.mapLayersByName("5_2_SWMM_outfalls")[0]
divider_layer = proj.mapLayersByName("5_2_SWMM_dividers")[0]
storage_layer = proj.mapLayersByName("5_2_SWMM_storages")[0]
# Links
conduit_layer = proj.mapLayersByName("5_2_SWMM_conduits")[0]
weir_layer = proj.mapLayersByName('5_2_SWMM_weirs')[0]
pump_layer = proj.mapLayersByName('5_2_SWMM_pumps')[0]
outlet_layer = proj.mapLayersByName("5_2_SWMM_outlets")[0]
orifice_layer = proj.mapLayersByName("5_2_SWMM_orifices")[0]
# Subcatchment
subcatchment_layer = proj.mapLayersByName("5_2_SWMM_subcatchments")[0]

node_layers = [junction_layer, outfall_layer, divider_layer, storage_layer]
sub_layer = subcatchment_layer
link_layers = [conduit_layer, weir_layer, pump_layer, outlet_layer, orifice_layer]
slope_req = 0.005




