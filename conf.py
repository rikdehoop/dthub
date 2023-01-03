import os
import pathlib

dir = pathlib.Path().absolute()
output = f'{dir}\\output'
gdb = f'{dir}\\dashboard_kaartelement\dashboard_kaartelement.gdb'
workspace=gdb

shapefiles_folder = output

cad_directory = output
cad_files_list = os.listdir(cad_directory)

pg_user = 'daqznt_tbcceo'
pg_password = 'de3ffb08'
pg_port = 5432
pg_host = 'db.qgiscloud.com'
pg_dbname = 'daqznt_tbcceo'

# pg_user = 'postgres'
# pg_password = 'Boerenkool14'
# pg_port = 5433
# pg_host = 'localhost'
# pg_dbname = 'postgres'


engine = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(pg_user, pg_password, pg_host, pg_port, pg_dbname)
print(engine)

if __name__ == "__main__":
    print("Executed when ran as main")
else:
    print("Executed when imported")