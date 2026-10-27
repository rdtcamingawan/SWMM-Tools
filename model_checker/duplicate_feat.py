from qgis.PyQt.QtCore import QMetaType
from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY
from qgis.core import QgsProject

def error_points(mem_layer, layer, feature, error):
    # Configure fields attribute values
    feature_name = feature["Name"]
    layer_source = layer.name()
    error = error

    # Assign attribute to feature
    feat = QgsFeature()
    feat.setAttributes([feature_name, layer_source, error])
    feat.setGeometry(feature.geometry())
    mem_layer_data = mem_layer.dataProvider()
    mem_layer_data.addFeatures([feat])

proj = QgsProject.instance()

# Create a temporary layer
mem_layer = QgsVectorLayer("Polygon?crs=EPSG:25833", "ErrorSubcatchments", "memory")
# Initialize fields
field = [QgsField("name",QMetaType.Type.QString),
        QgsField("layer_source", QMetaType.Type.QString),
        QgsField("error", QMetaType.Type.QString)]
# Assign fields to temporary layer
mem_layer_data = mem_layer.dataProvider()
mem_layer_data.addAttributes(field)
mem_layer.updateFields()


junction_layer = proj.mapLayersByName("5_2_SWMM_junctions")[0]
outfall_layer = proj.mapLayersByName("5_2_SWMM_outfalls")[0]

Junction_feat = junction_layer.getFeature(1)
outfall_feat = outfall_layer.getFeature(1)


error_points(
    mem_layer=mem_layer,
    layer=junction_layer,
    feature=Junction_feat,
    error="Error 208"
)

error_points(
    mem_layer=mem_layer,
    layer=outfall_layer,
    feature=outfall_feat,
    error="Error 208"
)



# mem_layer.startEditing()
# mem_layer.changeAttributeValue(1,2,"Hellow!")
# mem_layer.commitChanges()

proj.addMapLayer(mem_layer)