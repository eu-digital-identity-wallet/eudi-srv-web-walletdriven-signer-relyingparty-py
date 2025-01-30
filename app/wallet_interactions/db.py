import pymysql

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='rp',
            password='rp',
            database='rp'
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def add_to_signer_document_table(client_id, request_object):
    # save to database a request associated to client_id
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(''' INSERT INTO sd VALUES(%s,%s)''',(client_id, request_object))
    connection.commit()
    cursor.close()
    
def get_request_object_from_db(client_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(''' SELECT request_object FROM sd WHERE client_id = %s''',(client_id))
    data = cursor.fetchone()

    if(data is not None):
        print("deleting data...")
        cursor.execute(''' DELETE FROM sd WHERE client_id = %s''',(client_id))
        cursor.close()
        return data[0]
    
    else:
        cursor.close()
        return None
   
def add_to_signed_data_object_table(client_id, documentWithSignature):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(''' INSERT INTO sdo VALUES(%s,%s)''',(client_id, documentWithSignature))
    connection.commit()
    cursor.close()
    
def get_signed_data_object_from_db(client_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(''' SELECT signed_data_object FROM sdo WHERE client_id = %s''',(client_id))
    data = cursor.fetchone()
    
    if(data is not None):
        print("deleting data...")
        cursor.execute(''' DELETE FROM sdo WHERE client_id = %s''',(client_id))
        cursor.close()
        return data[0]

    else:
        cursor.close()
        return None