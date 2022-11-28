import arcpy
import pathlib
import conf as config
from get_Data import CollectData
from transform_Data import TransformData
from arcpy import env
from arcpy.sa import *

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
    # arcpy.CreateFishnet_management(r"output\reg_point_lyr.shp",str(bbox.extent.lowerLeft),str(bbox.extent.XMin) + " " + str(bbox.extent.YMax + 10),"5000","","20","20",str(bbox.extent.upperRight),"LABELS","#","POLYLINE")
    # arcpy.sa.ExtractValuesToPoints(r"output\reg_point_lyr_label.shp", r"hittekaart\hittekaart gevoelstemperatuur huidig.tif", rf"{output}\valuextract1.shp", "INTERPOLATE", "VALUE_ONLY")
    arcpy.management.CreateRandomPoints(output, "ran_points", None, '142520 408356 162772 419594 PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]', 16, "0 Unknown", "POINT", 0)
    arcpy.management.CalculateField(rf"{output}\ran_points", "cool", "random()*7", "ARCADE", '', "DOUBLE", "NO_ENFORCE_DOMAINS")



    attr = "{0} = -9999".format(arcpy.AddFieldDelimiters(rf"{output}\valuextract1.shp", 'RASTERVALU'))
    selection = arcpy.SelectLayerByAttribute_management(rf"{output}\valuextract1.shp", "NEW_SELECTION", attr)
    arcpy.management.DeleteRows(selection)

def make_interpolation():
    # arcpy.ga.EmpiricalBayesianKriging(
    # rf"{output}\valuextract1.shp", "RASTERVALU",    # input
    # rf"{output}\stat_intpl.shp",                    # secundairy output
    # rf"{output}\hittekaart_pred1.tif",              # primary output      
    # 42.7140140000077, "NONE", 100, 1, 100,          # parameters:
    # '''NBRTYPE=StandardCircular 
    #     RADIUS=5501.37988985476 
    #     ANGLE=0 
    #     NBR_MAX=15 
    #     NBR_MIN=10 
    #     SECTOR_TYPE=ONE_SECTOR
    # ''', "PREDICTION", 0.5, "EXCEED", None, "POWER")


    arcpy.ga.IDW(rf"{output}\ran_points", "cool", None, rf"{output}\randomraster.tif", 36.2841841540039, 2, 
    "NBRTYPE=StandardCircular RADIUS=460 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR", None)

    RDNEW = f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif"
    coord_sys = arcpy.Describe(RDNEW).spatialReference

    # arcpy.management.DefineProjection(rf"{output}\hittekaart_pred1.tif", coord_sys)
    # from osgeo import gdal
    # from osgeo import ogr

    # pts = ogr.Open(rf"{output}\valuextract1.shp", 0)
    # layer = pts.GetLayer()

    # for field in layer.schema:
    #     print(field.name)
    # rlayer  = gdal.Open("hittekaart\\hittekaart gevoelstemperatuur huidig.tif")
    # gt = rlayer.GetGeoTransform()

    # ulx = gt[0] 
    # uly = gt[3] 
    # res = gt[1] 
    # xsize = rlayer.RasterXSize 
    # ysize = rlayer.RasterYSize 
    # lrx = ulx + xsize * res 
    # lry = uly - ysize * res 

    # rlayer = None 
    # pts = layer = None 
    # idw =  gdal.Grid(rf"{output}\randomraster.tif", rf"{output}\valuextract1.shp", zfield="RASTERVALU", 
    # algorithm="invdist:power=3:radius1=2000:radius2:2000", outputBounds=[ulx, uly, lrx, lry], width=xsize, height=ysize)  
    # idw = None 
    raster_list = [f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif", f"{output}\\randomraster.tif"]

    ras0 = Raster(raster_list[0])
    ras1 = Raster(raster_list[1])


    output_raster = ras0 - ras1

    output_raster.save(rf"{output}\random_scenario.tif")
    arcpy.management.DefineProjection(rf"{output}\random_scenario.tif", coord_sys)


 
def create_uniques():
    for i in os.listdir(output):
        file = os.fsdecode(i)
        if file.endswith(".shp"):
            arcpy.management.CalculateField(rf"output\{file}", "Id", "!FID!", "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")


make_point_lyr()
make_interpolation()
create_uniques()

    
from geoserver_con import raster_to_geoserver  
from db_con import Database_migration

raster_to_geoserver()
Database_migration(config.cad_files_list)




