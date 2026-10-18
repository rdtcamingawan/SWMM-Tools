from qgis.core import QgsSpatialIndex, QgsProject

from ..config import load_layer

def assign_node_name(vlayer,fid,field_idx, new_value):
    vlayer.changeAttributeValue(
        fid,
        field_idx,
        new_value,
        # old_value,
    )
    return

def assign_node():
    proj = QgsProject.instance()
    conduit_layer = load_layer("conduit_layer_id", "conduit_layer")
    node_layer = load_layer("junction_layer_id", "junction_layer")

    # Initialize node layer as QgsSpatialIndex
    index = QgsSpatialIndex(node_layer.getFeatures())

    conduit_fields = conduit_layer.fields()
    # Index of FromNode
    idx_from_node = conduit_fields.indexOf("FromNode")
    # Index of ToNode
    idx_to_node = conduit_fields.indexOf("ToNode")

    conduit_layer.startEditing() # Conduit layer Start Editing
    # Loop for every feature of the conduit layed
    for feat in conduit_layer.getFeatures():
        geom = feat.geometry().asPolyline()
        start_point = geom[0]
        end_point = geom[-1]

        # Get FID then Name of nearest junction point
        # at the START VERTEX
        start_point_fid = index.nearestNeighbor(
                                start_point,
                                neighbors=1,)[0]
        start_point_name = node_layer.getFeature(start_point_fid)["Name"]
        # Get FID then Name of nearest junction point
        # at the END VERTEX
        end_point_fid = index.nearestNeighbor(
                                end_point,
                                neighbors=1,)[0]
        end_point_name = node_layer.getFeature(end_point_fid)["Name"]


        # --------- Update Conduit Layer Attribute Value ---------------------       
        
        # Update FromNode
        assign_node_name(conduit_layer, 
                        feat.id(),
                        idx_from_node,
                        new_value=start_point_name,
                            )
        # Update ToNode
        assign_node_name(conduit_layer, 
                            feat.id(),
                            idx_to_node,
                            new_value=end_point_name,
                            )
        
    # conduit_layer.commitChanges() # Commit Edits