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
    arcpy.management.CreateRandomPoints(output, "ran_trees", None, '142520 408356 162772 419594 PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]', 16, "0 Unknown", "POINT", 0)
    arcpy.management.CalculateField(rf"{output}\ran_trees", "cool", 6, 'PYTHON3','','DOUBLE','') 


    # attr = "{0} = -9999".format(arcpy.AddFieldDelimiters(rf"{output}\valuextract1.shp", 'RASTERVALU'))
    # selection = arcpy.SelectLayerByAttribute_management(rf"{output}\valuextract1.shp", "NEW_SELECTION", attr)
    # arcpy.management.DeleteRows(selection)

def make_interpolation():
    power = 1
    tree_dia = 4
    tree_height = 10
    altitude = 60
    azimuth = 215.42 - 180 + 90
    param = f"NBRTYPE=Standard S_MAJOR={tree_dia} S_MINOR={tree_height} ANGLE={azimuth} NBR_MAX=15 NBR_MIN=0 SECTOR_TYPE=ONE_SECTOR"
    arcpy.ga.IDW(os.path.join(output, "ran_trees"), "cool", None, "outputraster", 1, 2, param, None)
    arcpy.management.Shift("outputraster", "shifted_rast", tree_height*0.5, tree_height*0.5, None)

    RDNEW = f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif"
    coord_sys = arcpy.Describe(RDNEW).spatialReference


    outCon = Con(IsNull("shifted_rast"), 0, "shifted_rast")
    outCon.save(f"{output}\\tree_shade.tif")

    raster_list = [f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif", f"{output}\\tree_shade.tif"]

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




