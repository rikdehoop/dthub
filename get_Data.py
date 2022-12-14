
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

pd.set_option('display.max_columns',None)


# rules:
#       crs epsg:28992

# Polygoon extractie (OSM):
#       landuse.shp     

# Polygoon extractie (pdok):
#       waterdeel.shp
#       bgt_onbegroeidterreindeel.shp


def osmreq(AREA):
    tag1 = {'landuse': True}
    tag2 = {'natural': True}
    AREA1 = ox.geometries_from_place(AREA, tag1)
    AREA2 = ox.geometries_from_place(AREA, tag2)
    projection = CRS.from_epsg(28992)
    AREA1 = AREA1.to_crs(projection)
    AREA2 = AREA2.to_crs(projection)
    AREA1 = AREA1.loc[:,AREA1.columns.str.contains('landuse|geometry')]
    AREA2 = AREA2.loc[:,AREA2.columns.str.contains('wetland|water|beach|geometry')]
    AREA1 = AREA1.loc[AREA1.geometry.type=='Polygon']
    AREA2 = AREA2.loc[AREA2.geometry.type=='Polygon']
    AREA1.to_file('input\\landuse.shp')
    AREA2.to_file('input\\water.shp')

def gmltoshp():
    directory = 'input'
    for i in os.listdir(directory):
        file = os.fsdecode(i)
        if file.endswith(".xml") and "shp" not in str(file): 
            basename = file.split('.')[0]
            esri_shp = basename + '.shp'
            dir = os.path.join(pathlib.Path().absolute(),"input")
            cmd = 'ogr2ogr -f "ESRI Shapefile" "{2}\{0}" "{2}\{1}"'.format(esri_shp, file, dir)
            print(cmd)
            import subprocess
            subprocess.run(cmd,shell=True)
def pdokreq(geom):
    data = {
    "featuretypes": [
        "begroeidterreindeel",
        "onbegroeidterreindeel",
        "openbareruimte",
        "wegdeel",
        "waterdeel",
    ],
    "format": "citygml",
    "geofilter": "{}".format(geom)
    }

    url = 'https://api.pdok.nl/lv/bgt/download/v1_0/delta/custom'
    headers = {'Content-Type':'application/json','Accept': 'application/json'}

    u = requests.post(url, data=json.dumps(data), headers=headers)

    if u.status_code != 202:
        print("error occured creating custom download")
        print("response status: " + str(u.status_code))
        print("response body: " + u.text)
        exit(1)

    response_object = json.loads(u.text)
    status_path = response_object["_links"]["status"]["href"]
    download_request_id = response_object["downloadRequestId"]
    status_url = "https://api.pdok.nl" + status_path
    while True:
        u = requests.get(status_url)
        status_object = u.json()
        custom_status = status_object["status"]
        print("status generating download: " + custom_status)
        if custom_status == "COMPLETED":
            download_path = status_object["_links"]["download"]["href"]
            download_url = "https://api.pdok.nl" + download_path
            break
        elif custom_status == "RUNNING":
            progress = status_object["progress"]
            print("progress generating download:  " + str(progress))
        else:
            break
        time.sleep(5)

    if download_url:
        filename = download_request_id + '_' + os.path.basename(download_url) 
        filepath = os.path.join(pathlib.Path().absolute(), filename)
        print("downloading file " + download_url + " to " + filepath)
        u = requests.get(download_url)
        with open(filepath, 'wb') as f:
            f.write(u.content)
            
        with ZipFile(filepath, 'r') as zipObj:
            zipObj.extractall('input')
        gmltoshp()
        createSHX()

        
    else:
        print("error occured generating download")

def CollectData(AREA):
    string = AREA
    AREA = ox.geocode_to_gdf(AREA)
    projection = CRS.from_epsg(28992)
    AREA = AREA.to_crs(projection)
    AREA=gdp.GeoDataFrame(data=AREA, geometry=AREA['geometry'])
    geom = AREA['geometry'].iloc[0]

    osmreq(string); 
    pdokreq(geom); 

def createSHX():
    dir = os.path.join(pathlib.Path().absolute(),"input")
    for i in os.listdir(dir):
        f = os.fsdecode(i)
        
        if f.endswith(".shp"):
            basename = f.split('.')[0]
            shx = basename + '.shx'
            if os.path.isfile(f"{dir}/{shx}"):
                reproj = gdp.read_file(f"{dir}/{f}")
                reproj = reproj.set_crs(epsg=28992, allow_override=True)
                reproj.to_crs(epsg=28992)
                reproj.to_file(f'{dir}/{f}', driver='ESRI Shapefile', crs=28992)
            else:
                import shapefile
                # Explicitly name the shp and dbf file objects
                # so pyshp ignores the missing/corrupt shx
                shp = open(f"{basename}.shp", "rb")
                dbf = open(f"{basename}.dbf", "rb")
                r = shapefile.Reader(shp=shp, shx=None, dbf=dbf)
                w = shapefile.Writer(r.shapeType)
                # Copy everything from reader object to writer object
                w._shapes = r.shapes()
                w.records = r.records()
                w.fields = list(r.fields)
                # saving will generate the shx
                w.save(f"{basename}")


