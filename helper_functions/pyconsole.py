from qgis.core import QgsSpatialIndex

proj = QgsProject.instance()
line_layer = proj.mapLayersByName("flowPath")[0]
junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]

# Initialize junction layer for QgsSpatialIndex-ing
index = QgsSpatialIndex(junction_layer.getFeatures())

def assign_node_name(vlayer,fid,field_idx, new_value):
    vlayer.changeAttributeValue(
        fid,
        field_idx,
        new_value,
        # old_value,
    )
    return


junction_field = line_layer.fields()
# Index of FromNode
idx_from_node = junction_field.indexOf("FromNode")
# Index of ToNode
idx_to_node = junction_field.indexOf("ToNode")

line_layer.startEditing()
# Loop for every feature of the conduit layed
for feat in line_layer.getFeatures():
    geom = feat.geometry().asPolyline()
    start_point = geom[0]
    end_point = geom[-1]

    # Get FID then Name of nearest junction point
    # at the START VERTEX
    start_point_fid = index.nearestNeighbor(
                            start_point,
                            neighbors=1,)[0]
    start_point_name = junction_layer.getFeature(start_point_fid)["Name"]
    # Get FID then Name of nearest junction point
    # at the END VERTEX
    end_point_fid = index.nearestNeighbor(
                            end_point,
                            neighbors=1,)[0]
    end_point_name = junction_layer.getFeature(end_point_fid)["Name"]


    # --------- Update Attribute ---------------------
    # Assign the name of the intersected junction point
    # on the FromNode and ToNode of the conduit layer
    
    # Get old value of FromNode
    old_value = feat["FromNode"]
    # Update FromNode
    assign_node_name(line_layer, 
                     feat.id(),
                     idx_from_node,
                     new_value=start_point_name,
                        )
    
    # # Get old value of ToNode
    old_value = feat["ToNode"]
    # Update ToNode
    assign_node_name(line_layer, 
                     
                        feat.id(),
                        idx_to_node,
                        new_value=end_point_name,
                        )
line_layer.commitChanges()