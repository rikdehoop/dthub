from geo.Geoserver import Geoserver
import os
import pathlib

geo = Geoserver('http://localhost:8085/geoserver', username='admin', password='geoserver')

dir = pathlib.Path().absolute()


geo.create_workspace(workspace='workspace')
geo.create_coveragestore(layer_name='praster', path=r'C:\\kaarttest.tif', workspace='workspace')



                        
# # for i in os.listdir(output):
# #     file = os.fsdecode(i)
# #     if file.endswith(".shp"):
# #         table = str(file[:-4])
# #         print(table)
# #         geo.create_featurestore(store_name='geo_data_blob', workspace='workspace', db='srxqua_poqsyl', 
# #                         host='db.qgiscloud.com', pg_user='srxqua_poqsyl', pg_password='a4e1fec9')
# #         geo.publish_featurestore(workspace='workspace', store_name='geo_data_blob', pg_table=table)





# # sql = 'SELECT name, id, geom FROM post_gis_table_name'
# # geo.publish_featurestore_sqlview(store_name='geo_data', name='view_name', sql=sql, key_column='name', workspace='demo')

# # geo.upload_style(path='file.sld', workspace='demo')
# # geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo')