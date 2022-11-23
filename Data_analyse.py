import arcpy
import pathlib
import conf as config
from get_Data import CollectData
from transform_Data import TransformData
from db_con import Database_migration, gdf_to_postgis, get_features_id, create_gdf  

import os

# place = f'{input()}'

dir = pathlib.Path().absolute()
output = f'{dir}\\output'
gdb = f'{dir}\\dashboard_kaartelement\dashboard_kaartelement.gdb'
workspace=gdb

CollectData('‘s-Hertogenbosch')

arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

TransformData()

def make_point_lyr():
    ext = r's_hertogenbosch_extent\gemeente s-hertogenbosch.shp'
    bbox = arcpy.Describe(ext)
    arcpy.CreateFishnet_management(r"output\reg_point_lyr.shp",str(bbox.extent.lowerLeft),str(bbox.extent.XMin) + " " + str(bbox.extent.YMax + 10),"5000","","20","20",str(bbox.extent.upperRight),"LABELS","#","POLYLINE")
    arcpy.sa.ExtractValuesToPoints(r"output\reg_point_lyr_label.shp", r"hittekaart\hittekaart gevoelstemperatuur huidig.tif", rf"{output}\valuextract1.shp", "INTERPOLATE", "VALUE_ONLY")

    attr = "{0} = -9999".format(arcpy.AddFieldDelimiters(rf"{output}\valuextract1.shp", 'RASTERVALU'))
    selection = arcpy.SelectLayerByAttribute_management(rf"{output}\valuextract1.shp", "NEW_SELECTION", attr)
    arcpy.management.DeleteRows(selection)

def make_interpolation():
    arcpy.ga.EmpiricalBayesianKriging(
    rf"{output}\valuextract1.shp", "RASTERVALU", # input
    rf"{output}\stat_intpl.shp",                # secundairy output
    rf"{output}\hittekaart_pred1.tif",          # primary output      
    42.7140140000077, "NONE", 100, 1, 100,      # parameters:
    '''NBRTYPE=StandardCircular 
        RADIUS=5501.37988985476 
        ANGLE=0 
        NBR_MAX=15 
        NBR_MIN=10 
        SECTOR_TYPE=ONE_SECTOR
    ''', "PREDICTION", 0.5, "EXCEED", None, "POWER")

    # from osgeo import gdal
    # from osgeo import ogr

    # pts = ogr.Open("output\\valuextract1.shp", 0)
    # layer = pts.GetLayer()
    

    
    # for field in layer.schema:
    #     print(field.name)
    # rlayer  = gdal.Open("hittekaart\\hittekaart gevoelstemperatuur huidig.tif")
    # gt = rlayer.GetGeoTransform()

    # ulx = gt[0]
    # uly = gt[3]
    # res = gt[2]
    # xsize = rlayer.RasterXSize
    # ysize = rlayer.RasterYSize
    # lrx = ulx + xsize * res
    # lry = uly - ysize * res

    # rlayer = None
    # pts = layer = None
    # idw =  gdal.Grid("rasterp.tif", "output\\valuextract1.shp", zfield="RASTERVALU",
    # algorithm="nearest", outputBounds=[ulx, uly, lrx, lry], width=xsize, height=ysize)  
    # idw = None


def create_uniques():
    for i in os.listdir(output):
        file = os.fsdecode(i)
        if file.endswith(".shp"):
            arcpy.management.CalculateField(rf"output\{file}", "Id", "!FID!", "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")

    
    
make_point_lyr()
make_interpolation()
create_uniques()
Database_migration(config.cad_files_list)




