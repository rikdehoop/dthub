import psycopg2
import datetime as dt
from pysolar.solar import *
import conf as config
import fiona
from sqlalchemy import create_engine
point_dict = []
def retrieve():
    try:
        dt_data = {}
        while True:
            connection = psycopg2.connect(user="daqznt_tbcceo",
                                        password="de3ffb08",
                                        host="db.qgiscloud.com",
                                        port="5432",
                                        database="daqznt_tbcceo")

            print("LISTENING.......")
            cursor = connection.cursor()
            postgreSQL_select_Query = "select dt_data.id, dt_data.datumtijd, dt_data.kroonh, dt_data.kroondia, dt_data.stamh, st_astext(geom) as geometry_wkt , st_astext(ST_Transform(geom,28992)) as rdnew from dt_data"

            cursor.execute(postgreSQL_select_Query)
            records = cursor.fetchall()
            
            for row in records:
                dt_data = {
                "id": row[0],
                "boomh": row[2]+row[4],
                "kroondia": row[3],
                "tijdstip": row[1],
                "geom": row[5],
                "rdnew": row[6]
                }
                point_dict.append(dt_data)
                r = row[0]
            if bool(dt_data) == True and r == 5: 
                break
            

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

    finally:
        # closing database connection
        if connection:
            
            
            postgreSQL_delete_Query = "DELETE FROM dt_data"
            postgreSQL_alter_Query = "ALTER SEQUENCE dt_data_id_seq RESTART WITH 1"
            cursor.execute(postgreSQL_delete_Query)
            connection.commit()
            cursor.execute(postgreSQL_alter_Query)
            connection.commit()
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed \n")
            print(point_dict)
            return point_dict


 









