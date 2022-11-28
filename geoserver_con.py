from geo.Geoserver import Geoserver
import os
import pathlib
def raster_to_geoserver():
    geo = Geoserver('http://localhost:8085/geoserver', username='admin', password='geoserver')

    dir = pathlib.Path().absolute()

    geo.create_workspace(workspace='greenman')
    geo.create_coveragestore(layer_name='random_raster', path=rf'{dir}\output\random_scenario.tif', workspace='greenman')
    # geo.create_coveragestore(layer_name='no_scenario', path=rf'{dir}\hittekaart\hittekaart gevoelstemperatuur huidig.tif', workspace='greenman')
