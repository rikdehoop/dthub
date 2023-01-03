import arcpy
import pathlib
import conf as config
from get_Data import CollectData
from transform_Data import TransformData
from arcpy import env
from arcpy.sa import *
from alwayslookin import retrieve
import os
from datetime import *
from pysolar.solar import *
import shapely.wkt
from shapely.geometry import Point, mapping
from geoserver_con import raster_to_geoserver  
from db_con import Database_migration
import fiona
from fiona.crs import from_epsg


dir = pathlib.Path().absolute()
output = f'{dir}\\output'
gdb = f'{dir}\\dashboard_kaartelement\dashboard_kaartelement.gdb'
workspace=gdb

# CollectData('‘s-Hertogenbosch') #downloaden data

arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# TransformData() #clip, filter op attri, verwijderd alle onnodige rijen, en merged als grijs, blauw en groen
while True:
    dt_data = retrieve()
    def make_point_lyr():

        schema = {
            'geometry': 'Point',
            'properties': {'id': 'int','temp': 'int',}}
        with fiona.open('output' + '\\trees.shp', 'w', driver='ESRI Shapefile', schema=schema) as c:
            for i in dt_data:
                point = shapely.wkt.loads(i['geom'])
                geom = Point(point)

                p = shapely.wkt.loads(i['rdnew'])
                rdnew = Point(p)
                c.write({
                    'geometry': mapping(rdnew),
                    'properties': {'id': i['id'], 'temp': 6},
                })
        return point    

    


    def make_interpolation(dt_data=dt_data, point=make_point_lyr()):
        #input gebruiker, kroonhoogte, boomhoote etc..

    
        datetzinfo=dt_data[0]['tijdstip']
        power = 1
        tree_dia = dt_data[0]['kroondia']
        tree_height = dt_data[0]['boomh']
        altitude = get_altitude(point.y, point.x, datetzinfo)
        azimuth = get_azimuth(point.y, point.x, datetzinfo)
        print(azimuth)
        azi = azimuth - 180 + 90 # graden stand zon ten opzichte van de absolute noordpijl - 180 om de kant schaduw te krijgen + 90, zodat arcgis ook begint bij de Noordpijl
        
        param = f"NBRTYPE=Standard S_MAJOR={tree_dia} S_MINOR={tree_height} ANGLE={azi} NBR_MAX=15 NBR_MIN=0 SECTOR_TYPE=ONE_SECTOR"
        print(param)

        arcpy.ga.IDW(os.path.join(output, "trees.shp"), "temp", None, "outputraster", 1, 2, param, None)
        arcpy.management.Shift("outputraster", "shifted_rast", tree_height*0.5, tree_height*0.5, None)



        outCon = Con(IsNull("shifted_rast"), 0, "shifted_rast")
        outCon.save(f"{output}\\tree_shade.tif")

        raster_list = [f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif", f"{output}\\tree_shade.tif"]

        ras0 = Raster(raster_list[0])
        ras1 = Raster(raster_list[1])


        output_raster = ras0 - ras1

        output_raster.save(rf"{output}\random_scenario.tif")

        RDNEW = f"{dir}\\hittekaart\\hittekaart gevoelstemperatuur huidig.tif"
        coord_sys = arcpy.Describe(RDNEW).spatialReference
        arcpy.management.DefineProjection(rf"{output}\random_scenario.tif", coord_sys)


    
    def create_uniques():
        for i in os.listdir(output):
            file = os.fsdecode(i)
            if file.endswith(".shp"):
                arcpy.management.CalculateField(rf"output\{file}", "Id", "!FID!", "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")

    make_interpolation(dt_data=dt_data, point=make_point_lyr())
    create_uniques()

    


    raster_to_geoserver()
# Database_migration(config.cad_files_list)


