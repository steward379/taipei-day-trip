from flask import Flask, jsonify, request, render_template, Response
import os
import json
import MySQLdb
from dotenv import load_dotenv
from datetime import date
from collections import OrderedDict

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

load_dotenv()
password = os.environ.get("DB_PASSWORD")

def connect_to_db():
    if password is None:
        raise ValueError("Database password is not set!")
    return MySQLdb.connect(user='root', passwd=password, host='localhost', db='taipei_day_trip', charset='utf8mb4')

def bytes_to_str(data):
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if isinstance(data, date):
        return data.strftime('%Y-%m-%d')
    if isinstance(data, dict):
        return {key: bytes_to_str(value) for key, value in data.items()}
    if isinstance(data, list) or isinstance(data, tuple):
        return [bytes_to_str(element) for element in data]
    return data

# Pages
@app.route("/")
def index():
	return render_template("index.html")

@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")

@app.route("/booking")
def booking():
	return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

def fetch_images_for_attraction(attraction_id, cursor):
    query = "SELECT image_url FROM attraction_images WHERE attraction_id = %s"
    cursor.execute(query, (attraction_id,))
    images = [row['image_url'] for row in cursor.fetchall()]
    return images

def fetch_attraction_data(attraction_raw, cursor):
    images = fetch_images_for_attraction(attraction_raw['id'], cursor)
    return {
        'id': attraction_raw['id'],
        'name': attraction_raw['name'],
        'category': attraction_raw['Category'],
        'description': attraction_raw['description'],
        'address': attraction_raw['address'],
        'mrt': attraction_raw['MRT'],
        'lat': attraction_raw['lat'],
        'lng': attraction_raw['lng'],
        'images': images
    }

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    try:
        page = int(request.args.get('page', 0))
        keyword = request.args.get('keyword', None)

        # mrtOnly       
        mrtOnly = request.args.get('mrtOnly', 'false') == 'true'
        
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # 先計算總數
        query_count = "SELECT COUNT(*) FROM attractions "
        
        # mrtOnly
        params_count= None

        if keyword:
            if mrtOnly:
                query_count += "WHERE mrt = %s "
                # mrtOnly
                params_count= (keyword,)
            else:
                query_count += "WHERE name LIKE %s OR mrt = %s "
                # mrtOnly
                params_count= (f"%{keyword}%", keyword)

        cursor.execute(query_count, params_count)

        total_count = cursor.fetchone()['COUNT(*)']
        print(total_count)

        query = "SELECT id, name, CAT as Category, description, address, mrt as MRT, ST_X(location) as lng, ST_Y(location) as lat FROM attractions "
        
        params_query = None

        if keyword:
            if mrtOnly:
                query += "WHERE mrt = %s "
                params_query = (keyword, page * 12)
            else:
                query += "WHERE name LIKE %s OR mrt = %s "
                params_query = (f"%{keyword}%", keyword, page * 12)
                
        query += "LIMIT %s, 12"

        if params_query:
            cursor.execute(query, params_query )
        else:
            cursor.execute(query, (page * 12,))

        # query = "SELECT *, ST_AsText(location) as location_text FROM attractions "
        # query = "SELECT *, ST_X(location) as longitude, ST_Y(location) as latitude FROM attractions "

        attractions_raw = cursor.fetchall()
        
        # attractions = []
        
        # for attraction in attractions_raw:
		# 	...
        attractions = [fetch_attraction_data(attraction, cursor) for attraction in attractions_raw]


        connection.close()
		
        # attractions = bytes_to_str(attractions)
        
        
        # for attraction in attractions:
        #     for key, value in attraction.items():
        #         if isinstance(value, bytes):
        #             print(f"Key: {key}, Value: {value}")
        #     longitude = attraction.get("longitude", None)
        #     latitude = attraction.get("latitude", None)
        #     if longitude is not None and latitude is not None:
        #     #    x, y = map(float, location_text[6:-1].split())
        #        attraction["location"] = {"longitude": longitude, "latitude": latitude}


        # next_page = page + 1 if len(attractions) == 12 else None

        is_last_page = (page * 12 + len(attractions)) >= total_count
        next_page = page + 1 if not is_last_page else None

        response = OrderedDict([
            ("nextPage", next_page),
            ("data", attractions)
        ])
        
        response_json = json.dumps(response, ensure_ascii=False)
        return Response(response_json, content_type="application/json; charset=utf-8"), 200
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": str(e)}), 500
    

@app.route('/api/attraction/<attraction_id>', methods=['GET'])
def get_attraction_by_id(attraction_id):
    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT id, name, CAT as Category, description, address, mrt as MRT, ST_X(location) as lng, ST_Y(location) as lat FROM attractions WHERE id = %s"
        cursor.execute(query, (attraction_id,))

        attraction_raw = cursor.fetchone()
        
        if attraction_raw is None:
            return jsonify({"error": True, "message": "找不到該編號的景點"}), 400
        
        attraction = fetch_attraction_data(attraction_raw, cursor)

        connection.close()
        
        response = OrderedDict([
            ("data", attraction)
        ])
        
        response_json = json.dumps(response, ensure_ascii=False)
        return Response(response_json, content_type="application/json; charset=utf-8"), 200
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
    

@app.route('/api/mrts', methods=['GET'])
def get_mrts():
    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
        SELECT mrt, COUNT(*) as count
        FROM attractions
        WHERE mrt IS NOT NULL
        GROUP BY mrt
        ORDER BY count DESC
        LIMIT 40
        """
        
        cursor.execute(query)

        result_raw = cursor.fetchall()
        
        mrts = [row['mrt'] for row in result_raw]
        
        connection.close()

        response = {
            "data": mrts
        }
        
        response_json = json.dumps(response, ensure_ascii=False)
        return Response(response_json, content_type="application/json; charset=utf-8"), 200
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

app.run(host="0.0.0.0", port=3000)