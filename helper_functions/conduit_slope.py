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
    
def get_conduit_slope(start_vertex, end_vertex, length, index):
    start_elevation = get_elevation(index, start_vertex, junction_layer)
    end_elevation = get_elevation(index, end_vertex, junction_layer)

    # Slope = Δ elevation / length
    conduit_slope = abs(start_elevation - end_elevation) / length
    return conduit_slope

# Loop to get codnuit slope for each feature
for feat in conduit_layer.getFeatures():
    geom = feat.geometry()
    conduit_length = geom.length()

    # Skip zero-length conduits
    if conduit_length == 0:
        continue

    geom_poly = geom.asPolyline()
    start_vertex = geom_poly[0]
    end_vertex = geom_poly[-1]

    slope = get_conduit_slope(
        start_vertex=start_vertex,
        end_vertex=end_vertex,
        length=conduit_length,
        index=index,
    )

    print(feat.id(), slope)