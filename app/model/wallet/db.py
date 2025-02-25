import pymysql
from app_config.config import ConfigClass as cfgserv
from flask import (
    current_app as app
)

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=cfgserv.db_host,
            port=cfgserv.db_port,
            user=cfgserv.db_user,
            password=cfgserv.db_password,
            database=cfgserv.db_name
        )
        return connection
    except pymysql.Error as e:
        app.logger.error(f"Error connecting to MariaDB: {e}")
        return None

def add_to_signer_document_table(request_id, request_object):
    # save to database a request associated to client_id
    connection = get_db_connection()
    if connection is None:
        app.logger.error("impossible to use database.")
        raise ValueError("Impossible to use database.")
    cursor = connection.cursor()
    cursor.execute(''' INSERT INTO sd VALUES(%s,%s)''',(request_id, request_object))
    connection.commit()
    cursor.close()
    
def get_request_object_from_db(request_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(''' SELECT request_object FROM sd WHERE request_id = %s''',(request_id, ))
    data = cursor.fetchone()

    if data is not None:
        print("deleting data...")
        cursor.execute(''' DELETE FROM sd WHERE request_id = %s''',(request_id, ))
        cursor.close()
        return data[0]
    
    else:
        cursor.close()
        return None
   
def add_to_signed_data_object_table(request_id, signed_data_object, error):
    connection = get_db_connection()
    cursor = connection.cursor()    
    cursor.execute(''' INSERT INTO sdo (request_id, signed_data_object, error) VALUES(%s,%s,%s)''',(request_id, signed_data_object, error))
    connection.commit()
    cursor.close()
        
def get_signed_data_object_from_db(request_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(''' SELECT signed_data_object FROM sdo WHERE request_id = %s''', (request_id,))
    data = cursor.fetchall()
    
    if data:
        print("deleting data from database...")
        cursor.execute(''' DELETE FROM sdo WHERE request_id = %s''',(request_id,))
        connection.commit()
        cursor.close()
        print(data)
        return data
    else:
        cursor.close()
        return None