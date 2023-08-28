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

        cursor.execute("CREATE DATABASE IF NOT EXISTS taipei_day_trip")
        cursor.execute("USE taipei_day_trip")

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
            name VARCHAR(100) UNIQUE,
            CAT VARCHAR(30) NULL,
            MRT VARCHAR(30) NULL,
            idpt VARCHAR(30) NULL,
            address VARCHAR(200) NULL,
            longitude FLOAT NULL,
            latitude FLOAT NULL,
            location POINT,
            direction VARCHAR(2000) NULL,
            rate INT NULL,
            description VARCHAR(2000) NULL,
            MEMO_TIME VARCHAR(1000) NULL,
            date DATE NULL,
            langinfo INT NULL,
            REF_WP INT,
            RowNumber INT,
            POI VARCHAR(10),
            avBegin DATE,
            avEnd DATE,
            SERIAL_NO VARCHAR(16),
            old_id INT
        );
        '''
        cursor.execute(create_main_table_query)

        create_file_images_table_query = ('''
        CREATE TABLE IF NOT EXISTS attraction_images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            attraction_id INT,
            attraction_name VARCHAR(30), 
            image_url TEXT NULL,
            FOREIGN KEY(attraction_id) REFERENCES attractions(id),
            FOREIGN KEY(attraction_name) REFERENCES attractions(name) 
        );
        ''')

        cursor.execute(create_file_images_table_query)

        # 批次處理
        attractions_data = []
        image_data = []
  # The number of fields in your table
        for item in results: 
            # images_urls = [url for url in item["file"].split(';') if re.search(r'\.(jpg|png)$', url, re.IGNORECASE)]
            
            splitted = item["file"].split('https://')
            image_urls = ['https://' + s for s in splitted[1:] if s.endswith('.jpg') or s.endswith('.png')]
            del item["file"]

            if '_id' in item:
                item['old_id'] = item.pop('_id')

            longitude = float(item.get("longitude")) if item.get("longitude") else None
            latitude = float(item.get("latitude")) if item.get("latitude") else None
            # longitude = float(longitude) if longitude and longitude.replace('.', '', 1).isdigit() else None
            # latitude = float(latitude) if latitude and latitude.replace('.', '', 1).isdigit() else None

            if longitude is not None and latitude is not None:
                point_str = f"ST_PointFromText('POINT({longitude} {latitude})')"
            else:
                point_str = "NULL"

            # if point_str:
            #     columns.append('location')
            #     item_data = list(item.values())
            #     item_data.append(point_str)
            # else:
            #     item_data = list(item.values())

            columns = ', '.join(item.keys()) + ', location'
            placeholders = ', '.join(['%s'] * len(item.keys())) + f', {point_str}'
            sql_attractions = f"INSERT INTO attractions ({columns}) VALUES ({placeholders})"

            cursor.execute(sql_attractions, list(item.values()))
            
            cursor.execute("SELECT LAST_INSERT_ID();")
            last_id = cursor.fetchone()[0]

            for url in image_urls:
                # cursor.execute("INSERT INTO attraction_images (attraction_id, image_url) VALUES (%s, %s)", (last_id, url))
                cursor.execute("INSERT INTO attraction_images (attraction_id, attraction_name, image_url) VALUES (%s, %s, %s)", (last_id, item['name'], url))
                # if url.endswith(('.jpg', '.png')):
                    # image_data.append((last_id, url))
            connection.commit()
        print('success!')

        # if image_data:
        #     for attraction_id, image_url in image_data:
        #         cursor.execute("INSERT INTO attraction_images (attraction_id, image_url) VALUES (%s, %s)", (attraction_id, image_url))
        #         connection.commit()
        #         print(f'Successfully inserted image URL: {image_url} for attraction ID: {attraction_id}')
            # print('success!')
            # attractions_data.append(item_data)

        # for i, item in enumerate(results):
        #     image_urls = [url for url in item["file"].split(';') if re.search(r'\.(jpg|png)$', url, re.IGNORECASE)]
        #     for url in image_urls:
        #         image_data[i].append((last_id, url))
        #     last_id += 1
        # if longitude and latitude:
        #     point_str = f"POINT({longitude} {latitude})"
        #     cursor.execute(f"UPDATE attractions SET location = ST_PointFromText('{point_str}') WHERE id = {last_id}")
        # else:
        #     cursor.execute(f"UPDATE attractions SET location = NULL WHERE id = {last_id}")

        # if point_str:
        #     cursor.execute(f"UPDATE attractions SET location = ST_PointFromText('{point_str}') WHERE id = {last_id}")

        # item = {key: item[key] for key in ['name', 'description', 'address', 'longitude', 'latitude', 'date']}

        # sql = f"INSERT INTO attractions ({columns}) VALUES ({placeholders})"
        # 前綴 f = .format(columns=columns, placeholders=placeholders)
        # cursor.executemany(sql, list(filtered_item.values()))
            
#Exception is also ok
except Error as e:
    print(f"Error: {e}")

finally:

    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print('bye!')