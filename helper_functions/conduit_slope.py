from qgis.core import QgsProject, QgsSpatialIndex

# Get map layers
proj = QgsProject.instance()
conduit_layer = proj.mapLayersByName("5_2_SWMM_conduits")[0]
junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]

# Initialize junction layer as QgsSpatialIndex
index = QgsSpatialIndex(junction_layer.getFeatures())

def get_elevation(index, point, junction_layer):
    vertex_fid = index.nearestNeighbor(
        point,
        neighbors=1,)[0]
    junction_feat = junction_layer.getFeature(vertex_fid)
    junction_elevation = junction_feat["Elevation"]
    return junction_elevation
    


for feat in conduit_layer.getFeatures():
    geom = feat.geometry()
    geom_poly = geom.asPolyline()
    start_vertex = geom_poly[0]
    end_vertex = geom_poly[-1]

    # Get conduit end elevations
    start_elevation = get_elevation(
        index=index,
        point=start_vertex,
        junction_layer=junction_layer,)
    end_elevation = get_elevation(
        index=index,
        point=end_vertex,
        junction_layer=junction_layer,)

    # Get conduit length
    conduit_length = geom.length()

    # Skip the current feature if length is 0
    if conduit_length == 0:
        continue
    else:
        # Finally, get conduit slope
        # Slope = Δ elevation / length
        conduit_slope = (abs(start_elevation - end_elevation)) / conduit_length
        print(f"{feat["Name"]} Slope: {conduit_slope}, Length: {conduit_length}")