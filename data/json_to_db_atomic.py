from dotenv import load_dotenv
import os
import re
import json
# import pymysql
import mysql.connector
from mysql.connector import Error


# os.chdir('../') # 會改變工作目錄，不合適
# load_dotenv(dotenv_path="絕對路徑/.env")
load_dotenv(dotenv_path="../.env")
password = os.environ.get("DB_PASSWORD")

db_settings = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": password,
    "charset": "utf8mb4" # 除 utf8 還支援 emoji 和特殊符號
    # "charset": "utf8"
    # "db": "my_db", # pymysql
    # "database": "my_db", # mysql.connector
}

connection = None
cursor = None

try:
    with open('taipei-attractions.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        meta_data = json_data['result']
        results = json_data['result']['results']
    # connection = pymysql.connect(**db_settings)
    connection = mysql.connector.connect(**db_settings)
    if connection.is_connected():
        cursor = connection.cursor()

        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS taipei_day_trip_atomic")
            cursor.execute("USE taipei_day_trip_atomic")

            create_meta_table_query = '''
            CREATE TABLE IF NOT EXISTS metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `data_limit` INT,
                `data_offset` INT,
                `data_count` INT,
                `data_sort` VARCHAR(30)
            );
            '''
            cursor.execute(create_meta_table_query)

            cursor.execute("INSERT INTO metadata (data_limit, data_offset, data_count, data_sort) VALUES (%s, %s, %s, %s)", 
                (meta_data['limit'], meta_data['offset'], meta_data['count'], meta_data['sort']))

            create_main_table_query = '''
            CREATE TABLE IF NOT EXISTS attractions(
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                langinfo INT NULL,
                old_id INT
            );
            '''
            cursor.execute(create_main_table_query)

            create_location_table_query = '''
            CREATE TABLE IF NOT EXISTS attractions_location(
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                attraction_name VARCHAR(100),
                MRT VARCHAR(30) NULL,
                direction VARCHAR(2000) NULL,
                address VARCHAR(200) NULL,
                longitude FLOAT NULL,
                latitude FLOAT NULL,
                location POINT,
                FOREIGN KEY(attraction_id) REFERENCES attractions(id)
            );
            '''
            cursor.execute(create_location_table_query)

            create_description_table_query = '''
            CREATE TABLE IF NOT EXISTS attractions_description(
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                attraction_name VARCHAR(100),
                rate INT NULL,
                description VARCHAR(2000) NULL,     
                MEMO_TIME VARCHAR(1000) NULL,
                CAT VARCHAR(30) NULL,
                idpt VARCHAR(30) NULL,
                FOREIGN KEY(attraction_id) REFERENCES attractions(id)
            );
            '''
            cursor.execute(create_description_table_query)
                
            create_date_table_query = '''
            CREATE TABLE IF NOT EXISTS attractions_date(
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                attraction_name VARCHAR(100),
                date DATE NULL,
                avBegin DATE,
                avEnd DATE,  
                FOREIGN KEY(attraction_id) REFERENCES attractions(id)
            );
            '''
            cursor.execute(create_date_table_query)

            create_others_table_query = '''
            CREATE TABLE IF NOT EXISTS attractions_others(
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                attraction_name VARCHAR(100),
                POI VARCHAR(10),
                REF_WP INT,
                SERIAL_NO VARCHAR(16),     
                RowNumber INT,
                FOREIGN KEY(attraction_id) REFERENCES attractions(id)
            );
            '''
            cursor.execute(create_others_table_query)

            create_file_images_table_query = ('''
            CREATE TABLE IF NOT EXISTS attraction_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                attraction_name VARCHAR(100),
                image_url TEXT NULL,
                FOREIGN KEY(attraction_id) REFERENCES attractions(id)
            );
            ''')
            cursor.execute(create_file_images_table_query)
            
            for item in results: 
                # images_urls = [url for url in item["file"].split(';') if re.search(r'\.(jpg|png)$', url, re.IGNORECASE)]
                
                splitted = item["file"].split('https://')
                image_urls = ['https://' + s for s in splitted[1:] if s.endswith('.jpg') or s.endswith('.png')]
                del item["file"]

                if '_id' in item:
                    item['old_id'] = item.pop('_id')

                longitude = float(item.get("longitude")) if item.get("longitude") else None
                latitude = float(item.get("latitude")) if item.get("latitude") else None

                if longitude is not None and latitude is not None:
                    point_str = f"ST_PointFromText('POINT({longitude} {latitude})')"
                else:
                    point_str = "NULL"

                columns = ', '.join(item.keys())
                placeholders = ', '.join(['%s'] * len(item.keys())) 
                sql_attractions = f"INSERT INTO attractions ({columns}) VALUES ({placeholders})"

                cursor.execute(sql_attractions, list(item.values()))
                
                cursor.execute("SELECT LAST_INSERT_ID();")
                last_id = cursor.fetchone()[0]

                sql_location = """
                    INSERT INTO attractions_location (attraction_id, attraction_name, MRT, direction, address, longitude, latitude, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                location_data = (
                    last_id, item['name'], item['MRT'], item['direction'], item['address'], longitude, latitude, point_str
                )
                cursor.execute(sql_location, location_data)

                sql_description = """
                    INSERT INTO attractions_description (attraction_id, attraction_name, rate, description, MEMO_TIME, CAT, idpt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                description_data = (
                    last_id, item['name'],item['rate'], item['description'], item['MEMO_TIME'], item['CAT'], item['idpt']
                )
                cursor.execute(sql_description, description_data)

                sql_date = """
                    INSERT INTO attractions_date (attraction_id, attraction_name, date, avBegin, avEnd)
                    VALUES (%s, %s, %s, %s, %s)
                """
                date_data = (last_id, item['name'], item['date'], item['avBegin'], item['avEnd'])
                cursor.execute(sql_date, date_data)

                sql_others = """
                    INSERT INTO attractions_others (attraction_id, attraction_name, POI, REF_WP, SERIAL_NO, RowNumber)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                others_data = (last_id, item['name'], item['POI'], item['REF_WP'], item['SERIAL_NO'], item['RowNumber'])
                cursor.execute(sql_others, others_data)

                for url in image_urls:
                    sql_image = """
                        INSERT INTO attraction_images (attraction_id, attraction_name, image_url)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_image, (last_id, item['name'], url))
                    # if url.endswith(('.jpg', '.png')):
                        # image_data.append((last_id, url))
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
            connection.rollback()
            print("交易失敗，回滾")
#Exception is also ok
except Error as e:
    print(f"Error: {e}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()