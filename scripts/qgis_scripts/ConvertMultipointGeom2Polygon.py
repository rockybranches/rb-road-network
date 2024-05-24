import sys, os
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import (QgsVectorLayer, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingOutputVectorLayer)
try:
    import processing
except ModuleNotFoundError:
    sys.path.append('/usr/share/qgis/python/plugins/')
    import processing
    print('imported processing!')
    from processing.core.Processing import Processing
    Processing.initialize()
    print('processing initialized!')


class ConvertMultipointGeomConvexHull(QgsProcessingAlgorithm):
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                'Minimumboundingpolygon',
                'MinimumBoundingPolygon',
                type=QgsProcessing.TypeVectorPolygon,
                createByDefault=True,
                defaultValue=None))
        self.addParameter(
            QgsProcessingParameterVectorLayer('Multipoint Layer',
                                              'Multipoint Layer',
                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(
            QgsProcessingParameterVectorDestination('Market Boundary Layer'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Multipart to singleparts
        multipoint_layer = parameters['Multipoint Layer']
        alg_params = {
            'INPUT': multipoint_layer,  #'Multipoint Layer'
            'OUTPUT': parameters['Market Boundary Layer']
        }
        outputs['MultipartToSingleparts'] = processing.run(
            'native:multiparttosingleparts',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Minimum bounding geometry
        alg_params = {
            'FIELD': None,
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'TYPE': 3,
            'OUTPUT': parameters['Minimumboundingpolygon']
        }
        outputs['MinimumBoundingGeometry'] = processing.run(
            'qgis:minimumboundinggeometry',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        results['Minimumboundingpolygon'] = outputs['MinimumBoundingGeometry'][
            'OUTPUT']
        return results

    def name(self):
        return 'Convert: Multipoint Geom -> Convex Hull'

    def displayName(self):
        return 'Convert: Multipoint Geom -> Convex Hull'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return ConvertMultipointGeomConvexHull()
