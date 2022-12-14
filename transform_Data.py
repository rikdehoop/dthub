import arcpy
import pathlib
from get_Data import CollectData
import os
dir = pathlib.Path().absolute()
gdb = f'{dir}\\dashboard_kaartelement\dashboard_kaartelement.gdb'
output = f'{dir}\\ouput'

def trfLoad():

    attr = "{0} = 'retail' or {0} = 'residential' or {0} = 'railway' or {0} = 'industrial' or {0} = 'education' or {0} = 'construction' or {0} = 'brownfield' or {0} = 'commercial' or {0} = 'static_caravan'".format(arcpy.AddFieldDelimiters(f'{dir}\\input\\landuse.shp', 'landuse'))
    selection = arcpy.SelectLayerByAttribute_management(f'{dir}\\input\\landuse.shp', "NEW_SELECTION", attr)
    arcpy.CopyFeatures_management(selection, f'{dir}\\input\\osm_grijs.shp')      
    arcpy.management.DeleteRows(selection)

    attr = "{0} = 'reedbed' or {0} = 'marsh' or {0} = 'swamp' or {0} = 'wet_meadow'".format(arcpy.AddFieldDelimiters(f'{dir}\\input\\water.shp', 'wetland'))
    selection = arcpy.SelectLayerByAttribute_management(f'{dir}\\input\\water.shp', "NEW_SELECTION", attr)  
    arcpy.CopyFeatures_management(selection, f'{dir}\\input\\wetland.shp')  
    arcpy.management.DeleteRows(selection)

def deletefields(input,fld_to_keep):
        exclude = [fld_to_keep]
        fields = arcpy.ListFields(input)
        fieldremover = []
        for field in fields:
            if not field.required:
                if not field.name in exclude:
                    fieldremover.append(field.name)
        if fieldremover == '':
            return(0)
        x=(';'.join(fieldremover))
        print(x)
        arcpy.management.DeleteField(input, 
        "{0}".format(x), "DELETE_FIELDS")
        return(1)

def delete_rename_merge(directory):

    groen = []
    grijs = []
    blauw = []

    for i in os.listdir(directory):
            file = os.fsdecode(i)
            if file.endswith(".shp"):
                if file == 'wetland.shp' or file == 'landuse.shp' or file == 'bgt_begroeidterreindeel.shp':
                    groen.append(f'{dir}\\input\\{file}')
                    
                    fld = arcpy.ListFields(f'{dir}\\input\\{file}')
                    print(f'{str(fld[2].name)}')
                    print(f'{str(fld[2].type)}')

                    arcpy.management.CalculateField(f'{dir}\\input\\{file}', '!type!', "'groen'", 'PYTHON3')
                    deletefields(f'{dir}\\input\\{file}', 'F_type_')
                elif file == 'osm_grijs.shp' or file == 'bgt_wegdeel.shp' or file == 'bgt_onbegroeidterreindeel.shp':
                    grijs.append(f'{dir}\\input\\{file}')
                    
                    fld = arcpy.ListFields(f'{dir}\\input\\{file}')
                    print(f'{str(fld[2].name)}')
                    print(f'{str(fld[2].type)}')

                    arcpy.management.CalculateField(f'{dir}\\input\\{file}', '!type!', "'grijs'", 'PYTHON3')
                    deletefields(f'{dir}\\input\\{file}', 'F_type_')
                elif file == 'bgt_waterdeel.shp' or file == 'water.shp':
                    blauw.append(f'{dir}\\input\\{file}')
                    
                    fld = arcpy.ListFields(f'{dir}\\input\\{file}')
                    print(f'{str(fld[2].name)}')
                    print(f'{str(fld[2].type)}')

                    arcpy.management.CalculateField(f'{dir}\\input\\{file}', '!type!', "'blauw'", 'PYTHON3')
                    deletefields(f'{dir}\\input\\{file}', 'F_type_')
    print(groen)
    print(grijs)
    print(blauw)

    arcpy.Merge_management(groen, r"output\groen.shp")
    arcpy.Merge_management(grijs, r"output\grijs.shp")
    arcpy.Merge_management(blauw, r"output\blauw.shp")



def TransformData():
    trfLoad()
    delete_rename_merge(f'{dir}\\input')
