from qgis.core import QgsProject

proj = QgsProject.instance()

junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]
sub_layer = proj.mapLayersByName("5_2_SWMM_subcatchments")[0]
conduit_layer = proj.mapLayersByName("5_2_SWMM_conduits")[0]

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

# ========== Error 209: Check Missing Subcatchment Outlet ==========
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

# missing_outlet(sub_layer, junction_layer)

# ========== CHECK FOR NULL WIDTH/SLOPE ==========
def missing_width_slope(sub_layer):
    for sub in sub_layer.getFeatures():
        # Check for missing Width
        if not sub["Width"]:
            print(f"Missing Width on {sub["Name"]}")

        if not sub["Slope"]:
            print(f"Missing Slope on {sub["Name"]}")

# missing_width_slope(sub_layer)

# ========== ERROR 111: BAD CONDUIT ========== 
# Check conduit for missing From/To Node value
# Check for From == To Node
# Check if Length <= 0

def bad_conduit(conduit_layer, node_layer):
    node_names = set(collect_node_names(node_layer))
    for conduit in conduit_layer.getFeatures():
        # Check missing FromNode
        if not conduit["FromNode"]:
            print(f"Missing FromNode of conduit: {conduit["Name"]}")
        # Check missing ToNode
        if not conduit["ToNode"]:
            print(f"Missing ToNode of conduit: {conduit["Name"]}")
        # Check if FromNode == ToNode
        if conduit["FromNode"] == conduit["ToNode"]:
            print(f"Bad conduit at {conduit['Name']}")
        # Check if Length <= 0
        if conduit["Length"] <= 0:
            print(f"Bad conduit length at {conduit['Name']}")

# bad_conduit(conduit_layer, [junction_layer])

# ========== ERROR 112: INVALiD CONDUIT ROUGHNESS ========== 
def invalid_roughness(conduit_layer):
    for conduit in conduit_layer.getFeatures():
        # Check if ROUGHNESS is NULL
        if not conduit["Roughness"]:
            print(f"No roughness value assigned at {conduit['Name']}")
        # Check if ROUGHNESS <= 0
        if conduit["Roughness"] <= 0:
            print(f"Invalid roughness value at conduit: {conduit['Name']}")

# invalid_roughness(conduit_layer)

