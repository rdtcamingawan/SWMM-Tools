from qgis.core import QgsProject

proj = QgsProject.instance()

junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]
sub_layer = proj.mapLayersByName("5_2_SWMM_subcatchments")[0]

def collect_node_names(node_layer_list):
    for layer in node_layer_list:
        node_names = [f["Name"] for f in layer.getFeatures()]
    return node_names

def collect_sub_names(sub_layer):
    return [f["Name"] for f in sub_layer.getFeatures()]

# ========== ERROR 108: AMBIGUOUS SUBCATCHMENT'S OUTLET ==========
def check_ambiguous_sub_outlet(sub_names, node_names, sub_layer):
    set_node_names = set(node_names)
    set_sub_names = set(sub_names)
    intersection = set_node_names & set_sub_names

    # Walk the sub layer, check for any ambiguoug outlet
    # based on the intersection result
    for sub in sub_layer.getFeatures():
        if sub["Outlet"] in intersection:
            print(f"Error 108 @ {sub["Name"]}")
    return

# node_names = collect_node_names([junction_layer])
# sub_names = collect_sub_names(sub_layer)
# intersection = check_ambiguous_sub_outlet(sub_names, node_names, sub_layer)

def missing_outlet(sub_layer, node_layers):
    sub_names = collect_sub_names(sub_layer)
    node_names = collect_node_names([node_layers])
    set_names = set(sub_names).union(set(node_names))
    for sub in sub_layer.getFeatures():
        # Check for missing value
        if not sub["Outlet"]:
            print(f"Error 208: {sub['Name']} has missing outlet!")

        # Check if input exist in any junction/subcatchment layer value
        elif not sub["Outlet"] in set_names:
            print(f"Error 208: {sub['Name']} has invalid outlet! Outlet does not exist in any node/subcatchment layers! {set_names}")

missing_outlet(sub_layer, junction_layer)