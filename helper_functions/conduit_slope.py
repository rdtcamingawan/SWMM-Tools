from qgis.core import QgsProject, QgsSpatialIndex

from ..config import load_layer

def get_elevation(index, point, junction_layer):
    vertex_fid = index.nearestNeighbor(
        point,
        neighbors=1,)[0]
    junction_feat = junction_layer.getFeature(vertex_fid)
    junction_elevation = junction_feat["Elevation"]
    return junction_elevation

def get_conduit_slope(junction_layer, start_vertex, end_vertex, length, index):
    start_elevation = get_elevation(index, start_vertex, junction_layer)
    end_elevation = get_elevation(index, end_vertex, junction_layer)

    # Slope = Δ elevation / length
    conduit_slope = abs(start_elevation - end_elevation) / length
    return conduit_slope

def conduit_slope():
    proj = QgsProject.instance()

    # Get map layers
    conduit_layer = load_layer("conduit_layer_id", "conduit_layer")
    junction_layer = load_layer("junction_layer_id", "junction)layer")

    # Initialize junction layer as QgsSpatialIndex
    index = QgsSpatialIndex(junction_layer.getFeatures())     

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
            junction_layer=junction_layer,
            start_vertex=start_vertex,
            end_vertex=end_vertex,
            length=conduit_length,
            index=index,
        )

        print(feat.id(), slope)