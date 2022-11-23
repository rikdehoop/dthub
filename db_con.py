
from datetime import date
import arcpy
import conf as config
import fiona
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
import os.path
import shutil
from pathlib import Path
from pyproj import CRS
import fiona.crs


import requests
import json
import time
import os
from zipfile import ZipFile
import pathlib
import osmnx as ox
import matplotlib.pyplot as plt
import fiona
import fiona.crs
import geopandas as gdp
import pandas as pd
from pyproj import CRS
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt
from osgeo import gdal, osr
import psycopg2
import subprocess

# Workspace and files directories, fetched from config file
workspace = config.workspace
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

shapefile_directory = config.shapefiles_folder

# Gets through the ids of the existing features in the db table and puts them in a list       
def get_features_id(tablename):
    engine = create_engine(config.engine)

    connection = engine.connect()
    query = f'SELECT "Id" FROM {tablename}'
    uniqueList = []
    result = connection.execute(query)
    for elem in result:
        uniqueList.append(elem[0])
    print(uniqueList)
    return uniqueList

# Creates the pandas geodataframe from the shapefile
def create_gdf(type, tablename):
    shapefile = shapefile_directory + "\{0}".format(type)
    gdf = gpd.read_file(shapefile)      
    
    print('------------------------------{0} pandas gdf created-----------------------'.format(type))
    
    # if table exists, creates a new dataframe excluding the already existing features/rows
    engine = create_engine(config.engine)
    if engine.dialect.has_table(engine, tablename):
         gdf = gdf[~gdf['Id'].isin(get_features_id(tablename))]
    projection = CRS.from_epsg(28992)
    gdf = gdf.set_crs(projection)
    print(gdf)
    return gdf


# Connects to postgis and creates or adds the geodataframe to the table
def gdf_to_postgis(type, tablename):
    gdf = create_gdf(type, tablename)
    engine = create_engine(config.engine)
    gdf.to_postgis(name=tablename, con=engine, if_exists='append')
    print('------------------------------{0} data added to postgis -----------------------'.format(type))


def Database_migration(cad_files_list):
    for file in cad_files_list:
        if file.endswith(".shp"):
            gdf_to_postgis(file, str(file[:-4]))
        if file.endswith(".tif"):

            fileName = rf'{config.output}\{file}' #tiff_file_name and location
            raster = gdal.Open(fileName)
            proj = osr.SpatialReference(wkt=raster.GetProjection())
            projection=str(proj.GetAttrValue('AUTHORITY',1))
            gt =raster.GetGeoTransform()
            pixelSizeX =str(round(gt[1]))
            pixelSizeY =str(round(-gt[5]))
            cmd = '"C:\Program Files\PostgreSQL\\15\\bin\\raster2pgsql.exe" -F -I -C -s ' + projection + ' -t '+ pixelSizeX + 'x' + pixelSizeY + ' "' + fileName + '" public.' + 'hittekaart_pred1' + ' | psql ' + config.engine
            print(cmd)
            subprocess.run(cmd,shell=True)



Database_migration(config.cad_files_list)
