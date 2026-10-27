from qgis.core import QgsProject, QgsFeatureRequest
from qgis.core import (
    Qgis, QgsFeatureSink, QgsProcessing, QgsProcessingAlgorithm,
    QgsProcessingContext, QgsProcessingException, QgsProcessingFeedback,
    QgsProcessingParameterFeatureSink, QgsProcessingParameterFeatureSource, QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber, QgsFeature, QgsFields,
    QgsField, QgsWkbTypes
)

from qgis.PyQt.QtCore import QMetaType, QVariant

from qgis import processing

class ModelChecker(QgsProcessingAlgorithm):
    OUTPUT = "OUTPUT"
    def name(self):
        return "modelchecker"
    def displayName(self):
        return "Model Checker"
    def group(self):
        return "SWMM Tools"
    def groupId(self):
        return
    def shortHelpString(self):
        return "SWMM Tools"
    
    def initAlgorithm(self, node_layers=None, sub_layer=None, link_layers=None, slope_req=None):
        self.proj = QgsProject.instance()   
        self.slope_req = slope_req
        self.node_layers = node_layers or [] 
        self.link_layers = link_layers or [] 
        self.sub_layer = sub_layer # DONE
        self.point_dict = {}
        self.line_dict = {}
        self.polygon_dict = {}
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.sub_layer,
                "Subcatchment Layer",
                [QgsProcessing.SourceType.TypeVectorPolygon],optional=True
            ))

        self.addParameter(QgsProcessingParameterMultipleLayers(
            "node_layers",
            "Input Node Layers",
            QgsProcessing.TypeVectorPoint, optional=True))

        self.addParameter(QgsProcessingParameterMultipleLayers(
                    "link_layers",
                    "Input Link Layers",
                    QgsProcessing.TypeVectorLine, optional=True))
        
        self.addParameter(QgsProcessingParameterNumber(
                    'slope_req', 
                    'Input Link Slope Requirement in decimal form.', 
                    type=QgsProcessingParameterNumber.Double, 
                    minValue=0, 
                    defaultValue=0.005, optional=True))
        
        # OUTPUTS
        self.addParameter(QgsProcessingParameterFeatureSink(
                    'sub_errors',
                    "Polygon Model Error Output",
                    type=QgsProcessing.TypeVectorPolygon,))
        self.addParameter(QgsProcessingParameterFeatureSink(
                            'link_errors',
                            "Link Model Error Output",
                            type=QgsProcessing.TypeVectorLine,))
        self.addParameter(QgsProcessingParameterFeatureSink(
                                    'point_errors',
                                    "Point Model Error Output",
                                    type=QgsProcessing.TypeVectorPoint,))

    def get_layer_names(self, layer_list):
        def iterate_layers(layer_list):
            layer_names = set()
            for layer in layer_list:
                names = set([f["Name"] for f in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry))])
                layer_names = layer_names.union(names)
            return layer_names

        self.node_names = iterate_layers(layer_list)
        self.link_names = iterate_layers(layer_list)
        self.sub_names = [f["Name"] for f in self.sub_layer.getFeatures()]

    def model_dict(self, dict_type, feat, layer, error):
        # Check if the name doesn't exists
        if not feat["Name"] in dict_type:
            dict_type[feat["Name"]] = {
                                    "id": feat.id(),
                                    "name": feat["Name"],
                                    "layer": layer.name(),
                                    "errors": [error],
                                    "geometry": feat.geometry(),
                                    "feature": feat,
                                }
        else:
            dict_type[feat["Name"]]["errors"].append(error)

    def error_builder(self, mem_layer, feature, error, layer_source):
        # Configure fields attribute values
        feature_name = feature["Name"]
        error = error

        # Assign attribute to feature
        feat = QgsFeature()
        feat.setAttributes([feature_name, layer_source, error])
        feat.setGeometry(feature.geometry())
        mem_layer.addFeature(feat)

    # ========== ERROR 108: AMBIGUOUS SUBCATCHMENT'S OUTLET ==========
    def check_ambiguous_sub_outlet(self):
        error = "error_108"
        set_node_names = set(self.node_names)
        set_sub_names = set(self.sub_names)
        self.intersection = set_node_names & set_sub_names

        for sub in self.sub_layer.getFeatures():
            if sub["Name"] in self.intersection:
                # Update the dictionary
                self.model_dict(self.polygon_dict,
                                sub, self.sub_layer, error)

    # ========== Error 209: Check Missing Subcatchment Outlet ==========
    def missing_outlet(self):
        error = "error_209"
        set_names = set(self.sub_names).union(set(self.node_names))
        for sub in self.sub_layer.getFeatures():
            # Check for missing value
            if not sub["Outlet"]:
                self.model_dict(self.polygon_dict,
                                sub, self.sub_layer, error)

            # Check if input exist in any junction/subcatchment layer value
            elif not sub["Outlet"] in set_names:
                self.model_dict(self.polygon_dict,
                                sub, self.sub_layer, error)

    # ========== CHECK FOR NULL WIDTH/SLOPE ==========
    def missing_width_slope(self):
        error_width = "missing_width"
        error_slope = "missing_slope"
        for sub in self.sub_layer.getFeatures():
            # Check for missing Width
            if not sub["Width"]:
                self.model_dict(self.polygon_dict,
                                sub, self.sub_layer, error_width)
            if not sub["Slope"]:
                self.model_dict(self.polygon_dict, 
                                sub, self.sub_layer, error_slope)

    # ========== ERROR 111: BAD CONDUIT ========== 
    # Check conduit for missing From/To Node value
    # Check for From == To Node
    # Check if Length <= 0

    def bad_conduit(self):
        for link_layer in self.link_layers:
            for conduit in link_layer.getFeatures():
                # Check missing FromNode
                if not conduit["FromNode"]:
                    error = "error_111_miss_fromNode"
                    self.model_dict(self.line_dict,
                                    conduit, link_layer, error)
                # Check missing ToNode
                if not conduit["ToNode"]:
                    error = "error_111_miss_toNode"
                    self.model_dict(self.line_dict,
                                    conduit, link_layer, error)
                # Check if FromNode == ToNode
                if conduit["FromNode"] == conduit["ToNode"]:
                    error = "error_111_equal_toFromNode"
                    self.model_dict(self.line_dict,
                                    conduit, link_layer, error)
                # Check if Length <= 0
                try:
                    if conduit["Length"] <= 0:
                        error = "error_111_neg_len"
                        self.model_dict(self.line_dict,
                                        conduit, link_layer, error)
                except:
                    continue

    # ========== ERROR 112: INVALiD CONDUIT ROUGHNESS ========== 
    def invalid_roughness(self):
        error = "error_112"
        for link_layer in self.link_layers:
            for conduit in link_layer.getFeatures():
                try:
                    # Check if ROUGHNESS is NULL
                    if not conduit["Roughness"]:
                        self.model_dict(self.line_dict,
                                        conduit, link_layer, error)
                    # Check if ROUGHNESS <= 0
                    elif conduit["Roughness"] <= 0:
                        self.model_dict(self.line_dict,
                                        conduit, link_layer, error)
                except:
                    continue
                
    # ========== ERROR: LOW CONDUIT SLOPE ========== 
    # Check whether a conduit is below the 
    # user-input required slope

    def check_slope(self):
        def get_node_elevation(node_name):
            expression = f'"Name" = \'{node_name}\''
            request = QgsFeatureRequest().setFilterExpression(expression)
            request.setFlags(QgsFeatureRequest.NoGeometry)
            for node_layer in self.node_layers:
                feats = list(node_layer.getFeatures(request))
                if feats:
                    return feats[0]["Elevation"]
            return None

        error = "low_slope"
        for link_layer in self.link_layers:
            for conduit in link_layer.getFeatures():
                from_node = conduit["FromNode"]
                to_node = conduit["ToNode"]
                if not from_node or not to_node:
                    continue

                from_elev = get_node_elevation(from_node)
                to_elev = get_node_elevation(to_node)
                if from_elev is None or to_elev is None:
                    continue

                try:
                    # Length
                    length = conduit["Length"]
                    if not length or length <= 0:
                        geom = conduit.geometry()
                        length = geom.length() if geom else 0
                    if not length or length <= 0:
                        continue
                except:
                    continue

                slope = (from_elev - to_elev) / length

                if slope < self.slope_req:
                    self.model_dict(self.line_dict, conduit, link_layer, error)

    def run_model_checker(self):
        self.check_ambiguous_sub_outlet()
        self.missing_outlet()
        self.missing_width_slope()
        self.bad_conduit()
        self.invalid_roughness()
        self.check_slope()

        # Add eveything to the sinks
        # Polygon sink:
        for name, record in self.polygon_dict.items():
            feature = record["feature"]
            error = ", ".join(record["errors"])
            self.error_builder(
                self.polygon_error,
                feature=feature,
                error=error,
                layer_source=record["layer"],
            )
        # LineString Sink
        for name, record in self.line_dict.items():
                    feature = record["feature"]
                    error = ", ".join(record["errors"])
                    self.error_builder(
                        self.link_error,
                        feature=feature,
                        error=error,
                        layer_source=record["layer"],
                    )
        # Point Sink
        for name, record in self.point_dict.items():
                    feature = record["feature"]
                    error = ", ".join(record["errors"])
                    self.error_builder(
                        self.point_error,
                        feature=feature,
                        error=error,
                        layer_source=record["layer"],
                    )


    def processAlgorithm(
            self,parameters,
            context: QgsProcessingContext,
            feedback: QgsProcessingFeedback,
        ):
        # self.get_layer_names()
        self.sub_layer = self.parameterAsLayer(parameters, self.sub_layer, context)
        if self.sub_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )
        # Define Inputs
        self.node_layers = self.parameterAsLayerList(parameters, "node_layers", context)
        self.link_layers = self.parameterAsLayerList(parameters, "link_layers", context)
        self.slope_req = self.parameterAsDouble(parameters, "slope_req", context)

        # Processing
        self.get_layer_names(self.node_layers)
        self.get_layer_names(self.link_layers)

        # Define fields of Polygon output
        fields = QgsFields()
        fields.append(QgsField("name", QVariant.String))
        fields.append(QgsField("layer_source", QVariant.String))
        fields.append(QgsField("error", QVariant.String))
        
        # Define Outputs
        (self.polygon_error, dest_id) = self.parameterAsSink(parameters, 
                                                             "sub_errors",
                                                             context,
                                                             fields,
                                                             Qgis.WkbType.Polygon,
                                                             self.sub_layer.crs(),
                                                             )

        (self.link_error, dest_id) = self.parameterAsSink(parameters, 
                                                            "link_errors",
                                                            context,
                                                            fields,
                                                            Qgis.WkbType.LineString,
                                                            self.link_layers[0].crs(),
                                                            )

        (self.point_error, dest_id) = self.parameterAsSink(parameters, 
                                                            "point_errors",
                                                            context,
                                                            fields,
                                                            Qgis.WkbType.Point,
                                                            self.node_layers[0].crs(),
                                                            )


        self.run_model_checker()
        return {self.OUTPUT: self.sub_layer}

    def createInstance(self):
        return self.__class__()