#!/usr/bin/python

## with help from:
##  https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts

import os, sys, json
import pdb
from collections import OrderedDict
import geopandas
from qgis.core import *

# Supply path to qgis install location
QgsApplication.setPrefixPath("/usr/bin/qgis", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Write your code here to load some layers, use processing
# algorithms, etc.
sys.path.append('/usr/share/qgis/python/plugins/')
import processing
from processing.script.ScriptAlgorithmProvider import ScriptAlgorithmProvider
from processing.script import ScriptUtils
sys.path.append('/home/robertc/.local/share/QGIS/QGIS3/profiles/default/')
sfolder = ScriptUtils.scriptsFolders()[0]
from functools import partial
taskman = QgsTaskManager()


def multipoint2convexHull(multipoint_layer, output_layer, project):
    print('about to start multipoint2convexHull...')
    context = QgsProcessingContext()
    # context.setProject(project)
    parameters = {
        'Multipoint Layer': 'Multipoint Layer',
        'Market Boundary Layer': 'TEMPORARY_OUTPUT'
    }
    feedback = QgsProcessingFeedback()
    script_alg = ScriptUtils.loadAlgorithm(
        'script:Convert: Multipoint Geom -> Convex Hull',
        filePath='./ConvertMultipointGeom2Polygon.py')
    buffer_alg = script_alg
    task = QgsProcessingAlgRunnerTask(buffer_alg, parameters, context,
                                      feedback)
    print('init task...')

    def callback(context, success, results):
        print('success? ', success)
        print('done converting multipoint to convex hull!')
        print('results:', results)
        olayer = context.getMapLayer(results['OUTPUT'])
        QgsProject.instance().addMapLayer(context.takeResultLayer(olayer.id()))

    task.executed.connect(partial(callback, context))
    taskman.addTask(task)
    print('task added!')
    print('task done?', task.waitForFinished())
    return


class RBMarketAreasLoader:

    stlname, mplname = 'StartPoint', 'AccessibleArea'

    def __init__(self, json_filenames=None, **kwds):
        self.rbdatadir = os.environ.get('RB_DATA')
        self.rbsrcdir = os.environ.get('RB_SRC')
        self.templatesdir = os.path.join(self.rbdatadir,
                                         'QGIS_templates/market_area_map/')
        self.default_project_path = os.path.join(
            self.templatesdir, 'MarketAreaProjectTemplate-QGIS.qgz')
        self.projectdir, self.projectfpath = None, None
        self.json_filenames = self.init_json_filenames(json_filenames)

    def init_json_filenames(self, json_filenames):
        if not json_filenames or isinstance(json_filenames, str):
            json_inputs_filepath = os.path.join(
                self.rbsrcdir, 'scripts/qgis_scripts/list_json_inputs.txt')
            if isinstance(json_filenames, str):
                json_inputs_filepath = os.path.realpath(json_filenames)
            with open(json_inputs_filepath, 'r') as f:
                json_filenames = [r.strip() for r in f.readlines()]
        return json_filenames

    def __call__(self, **kwds):
        if not self.json_filenames:
            raise RuntimeError(
                "make sure to set json_filenames before calling this object!")
        self.setup_market_areas()

    def load_project(self, fn):
        ''' load default project template '''
        project = None
        print('...created project instance.')
        QgsProject.instance().read(self.default_project_path)
        self.projectdir = os.path.join(
            self.templatesdir, f'{fn.replace(".json","")}-MarketAreaProject')
        try:
            os.mkdir(self.projectdir)
        except FileExistsError:
            pass
        self.projectfpath = os.path.join(
            self.projectdir, f'{fn.replace(".json","")}-MarketAreaProject.qgz')
        status = QgsProject.instance().write(self.projectfpath)
        print('project write status=', status)
        sys.stdout.flush()
        project = QgsProject.instance()
        project.read(self.projectfpath)
        project.reloadAllLayers()
        return project

    def load_geojson(self, json_fpath):
        print('Loading', json_fpath, '...')
        gdf = geopandas.read_file(json_fpath)
        stfpath = os.path.join(self.projectdir, self.stlname + '.shp')
        gdf[gdf['name'] == self.stlname].to_file(stfpath)
        mpfpath = os.path.join(self.projectdir, self.mplname + '.shp')
        gdf[gdf['name'] == self.mplname].to_file(mpfpath)
        return stfpath, mpfpath

    def setup_vector_layers(self, stfpath, mpfpath, project):
        startpoint_layer, multipoint_layer = None, None
        startpoint_layer = QgsVectorLayer(stfpath, self.stlname, 'ogr')
        if not startpoint_layer.isValid():
            print('startpoint_layer is not valid!')
        project.addMapLayer(startpoint_layer)
        startpoint_layer.startEditing()
        startpoint_layer = self.set_startpoint_layer_style(
            startpoint_layer, labelname=self.stlname)
        startpoint_layer.commitChanges()
        multipoint_layer = QgsVectorLayer(mpfpath, self.mplname, 'ogr')
        afpath = mpfpath.replace(self.mplname + '.shp', 'area_bounds.shp')
        output_layer = QgsVectorLayer(afpath, 'Market Boundary Layer',
                                      'memory')
        multipoint2convexHull(multipoint_layer, output_layer, project)
        project.addMapLayer(multipoint_layer)
        project.reloadAllLayers()
        return startpoint_layer, multipoint_layer

    def setup_market_areas(self):
        for fn in self.json_filenames:
            project = self.load_project(fn)  # load, create project dir, .qgz
            print('project loaded.')
            sys.stdout.flush()
            json_fpath = os.path.join(self.rbsrcdir, f'output/{fn}')
            stfpath, mpfpath = self.load_geojson(json_fpath)
            stlayer, mplayer = self.setup_vector_layers(
                stfpath, mpfpath, project)
            project.write()
            print(f'...finished {project.fileName()}.')
            sys.stdout.flush()
            project = None
            print('starting next project...')
            sys.stdout.flush()

    def set_startpoint_layer_style(self, layer, labelname=None):
        style = QgsStyle()
        style.load(
            '/home/robertc/.local/share/QGIS/QGIS3/profiles/default/symbology-style.db'
        )
        symbol_name = style.findSymbols(style.StyleEntity(),
                                        'Market Area Start Point Styles')[0]
        print('...symbol found = ', symbol_name)
        new_renderer = QgsSingleSymbolRenderer(style.symbol(symbol_name))
        print('...set symbol.')
        layer.setRenderer(new_renderer)
        print('...set renderer.')
        return layer

    def set_area_layer_style(self, layer, labelname=None):
        status = layer.loadNamedStyle('Market Area Bounding Geometry Styles')
        print('area_style_status=', status)
        return layer


loader = RBMarketAreasLoader()
loader()

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
