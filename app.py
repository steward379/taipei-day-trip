from flask import Flask, jsonify, request, render_template, Response 
import os
import json
import MySQLdb
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from collections import OrderedDict
from dbutils.pooled_db import PooledDB
import jwt
from jwt import decode, encode
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

load_dotenv()
user=os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
db = os.environ.get("DB_NAME")
charset = os.environ.get("DB_CHARSET")
secret_key = os.environ.get("SECRET_KEY")

app.config["SECRET_KEY"]= secret_key

pool = PooledDB(
    creator=MySQLdb,  # 使用的庫
    maxconnections=6,  # 連接池允許的最大連接數，0和None表示不限制連接數
    mincached=2,  # 初始化時，連接池中至少創建的空閒的連接，0表示不創建
    maxcached=5,  # 連接池中最多閒置的連接，0和None不限制
    maxshared=3,  # 連接池中最多共享的連接數量，0和None表示全部共享
    blocking=True,  # 連接池中如果沒有可用連接後，是否阻塞等待。True，等待；False，不等待然後報錯
    setsession=[],  # 開始會話前執行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    user=user,
    passwd=password,
    host=host,
    db=db,
    charset=charset,
)

def connect_to_db():
    if password is None:
        raise ValueError("Database password is not set!")
    # return MySQLdb.connect(user=user, passwd=password, host=host, db=db , charset=charset )
    return pool.connection()

def bytes_to_str(data):
    if isinstance(data, bytes):
        return data.decode("utf-8")
    if isinstance(data, date):
        return data.strftime("%Y-%m-%d")
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
    #return render_template("attraction.html", attraction_id=id)
@app.route("/booking")
def booking():
	return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

def fetch_images_for_attraction(attraction_id, cursor):
    query = "SELECT image_url FROM attraction_images WHERE attraction_id = %s"
    cursor.execute(query, (attraction_id,))
    images = [row["image_url"] for row in cursor.fetchall()]
    return images


def fetch_attraction_data(attraction_raw, cursor):
    images = fetch_images_for_attraction(attraction_raw["id"], cursor)
    return {
        "id": attraction_raw["id"],
        "name": attraction_raw["name"],
        "category": attraction_raw["CAT"],
        "description": attraction_raw["description"],
        "address": attraction_raw["address"],
        "mrt": attraction_raw["MRT"],
        "transport": attraction_raw["direction"],
        "lat": attraction_raw["latitude"],
        "lng": attraction_raw["longitude"],
        "images": images
    }

def fetch_attraction_booking(attraction_raw, cursor):
    images = fetch_images_for_attraction(attraction_raw["id"], cursor)
    return {
        "id": attraction_raw["id"],
        "name": attraction_raw["name"],
        "address": attraction_raw["address"],
        "images": images
    }

# register
@app.route("/api/user", methods=["POST"])
def register():
    connection = None
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        data = request.json

        cursor.execute("SELECT * FROM users WHERE email = %s", (data["email"],))
        if cursor.fetchone():
            return jsonify({"error": True, "message": "Email 已被使用"}), 400
        
        cursor.execute("SELECT * FROM users WHERE name = %s", (data["name"],))
        if cursor.fetchone():
            return jsonify({"error": True, "message": "名稱已被使用"}), 400
        

        hashed_password = generate_password_hash(data["password"], method="scrypt")
        
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                       (data["name"], data["email"], hashed_password))

        connection.commit()
        # connection.close()

        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

# login
@app.route("/api/user/auth", methods=["PUT"])
def login():
    connection = None
    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        data = request.json

        cursor.execute("SELECT * FROM users WHERE email = %s", (data["email"],))
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password"], data["password"]):
            return jsonify({"error": True, "message": "帳密錯誤"}), 404

        token = jwt.encode({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(days=7)
        }, app.config["SECRET_KEY"])

        return jsonify({"token": token}), 200   
    except Exception as e:
        print(str(e))
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

def get_user_id_from_jwt():

    token = request.headers.get("Authorization")

    if not token:
        return None
    try:
        data = decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return data["id"]
    except Exception as e:
        print(f"An error occurred: {e}")  # 考慮使用更進階的日誌記錄方式
        return None


# check login status
@app.route("/api/user/auth", methods=["GET"])
def get_user():
    token = request.headers.get("Authorization")
    # authorization_header = request.headers.get("Authorization")
    # token = request.headers.get("Authorization").split(" ")[1]
    # if not authorization_header:
        # print(f"no authorization_header: {authorization_header}")
        # return jsonify({"data": None}), 200
    # try:
        # token = authorization_header.split(" ")[1]
    # except IndexError:
        # print(f"can't split: {authorization_header}") 
        # return jsonify({"data": None}), 200
    
    if not token:
        print(f"no token: {token}")  
        return jsonify({"data": None}), 200
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"]) #SHA-256
        return jsonify({
            "data": {
                "id": data["id"],
                "name": data["name"],
                "email": data["email"]
            }
        }), 200
    except Exception as e:
        # print(f"An error occurred: {e}")  # 考慮使用更進階的日誌記錄方式
        return jsonify({"data": None}), 200

@app.route("/api/attractions", methods=["GET"])
def get_attractions():
    try:
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", None)

        # mrtOnly       
        mrtOnly = request.args.get("mrtOnly", "false") == "true"
        
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # 先計算總數
        query_count = "SELECT COUNT(*) FROM attractions "
        
        # mrtOnly
        params_count= None

        if keyword:
            if mrtOnly:
                query_count += "WHERE MRT = %s "
                # mrtOnly
                params_count= (keyword,)
            else:
                query_count += "WHERE name LIKE %s OR MRT = %s "
                # mrtOnly
                params_count= (f"%{keyword}%", keyword)

        cursor.execute(query_count, params_count)

        total_count = cursor.fetchone()["COUNT(*)"]
        # print(total_count)

        # query = "SELECT id, name, CAT as Category, description, address, direction ,mrt as MRT, ST_X(location) as lng, ST_Y(location) as lat FROM attractions "
        query = "SELECT id, name, CAT, description, address, direction, MRT, longitude, latitude FROM attractions "
        
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
    

@app.route("/api/attraction/<attraction_id>", methods=["GET"])
def get_attraction_by_id(attraction_id):
    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # query = "SELECT id, name, CAT as Category, description, address, direction ,mrt as MRT, ST_X(location) as lng, ST_Y(location) as lat FROM attractions WHERE id = %s"
        query = "SELECT id, name, CAT, description, address, direction, MRT, longitude, latitude FROM attractions WHERE id = %s "
        
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
    

@app.route("/api/mrts", methods=["GET"])
def get_mrts():
    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
        SELECT MRT, COUNT(*) as count
        FROM attractions
        WHERE MRT IS NOT NULL
        GROUP BY MRT
        ORDER BY count DESC
        LIMIT 40
        """
        
        cursor.execute(query)

        result_raw = cursor.fetchall()
        
        mrts = [row["MRT"] for row in result_raw]
        
        connection.close()

        response = {
            "data": mrts
        }
        
        response_json = json.dumps(response, ensure_ascii=False)
        return Response(response_json, content_type="application/json; charset=utf-8"), 200
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
 
@app.route("/api/booking", methods=["GET"])
def get_booking():

    user_id = get_user_id_from_jwt()
    
    if user_id is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    connection = connect_to_db()
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))

    booking_data = cursor.fetchone()

    if booking_data:
        attraction_id = booking_data['attraction_id']

        cursor.execute("SELECT id, name, address FROM attractions WHERE id = %s", (attraction_id,))
        attraction_raw = cursor.fetchone()
        attraction_data = fetch_attraction_booking(attraction_raw, cursor)

        if attraction_raw is None:
            connection.close()
            return jsonify({"error": True, "message": "找不到相應的景點"}), 400

        # 將 booking_data 和attraction_data 合併
        response_data = {
            "attraction": {
                "id": attraction_data["id"],
                "name": attraction_data["name"],
                "address": attraction_data["address"],
                "image": attraction_data["images"][0] if attraction_data["images"] else None
            },
            "date": booking_data["date"],
            "time": booking_data["time"],
            "price": booking_data["price"]
        }
    else:
        response_data = None

    connection.close()

    if response_data:
        return jsonify({"data": response_data}), 200
    else:
        return jsonify({"data": None}), 200

@app.route("/api/booking", methods=["POST"])
def post_booking():
    user_id = get_user_id_from_jwt()

    if user_id is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    data = request.json

    if not all(k in data for k in ("attractionId", "date", "time", "price")):
        return jsonify({"error": True, "message": "輸入不正確"}), 400
    
    attraction_id = data["attractionId"]

    connection = connect_to_db()
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    # 先取得景點資料
    cursor.execute("SELECT * FROM attractions WHERE id = %s", (attraction_id,))
    attraction_data = cursor.fetchone()
    if not attraction_data:
        connection.close()
        return jsonify({"error": True, "message": "找不到該景點"}), 400

    images = fetch_images_for_attraction(attraction_id, cursor)
    first_image = images[0] if images else None

    cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
    existing_booking = cursor.fetchone()

    if existing_booking:
        cursor.execute("UPDATE bookings SET attraction_id = %s, attraction_name = %s, attraction_address = %s, attraction_image = %s, date = %s, time = %s, price = %s WHERE user_id = %s",
                       (attraction_id, attraction_data["name"], attraction_data["address"], first_image, data["date"], data["time"], data["price"], user_id))
    else:
        cursor.execute("INSERT INTO bookings (user_id, attraction_id, attraction_name, attraction_address, attraction_image, date, time, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (user_id, attraction_id, attraction_data["name"], attraction_data["address"], first_image, data["date"], data["time"], data["price"]))
        
    connection.commit()
    connection.close()

    return jsonify({"ok": True}), 200

@app.route("/api/booking", methods=["DELETE"])
def delete_looking():
    try:
        user_id = get_user_id_from_jwt()

        if user_id is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        connection = connect_to_db()
        if connection is None:
            return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
        cursor = connection.cursor()

        cursor.execute("DELETE FROM bookings WHERE user_id = %s", (user_id,))

        if cursor.rowcount == 0:
            return jsonify({"error": True, "message": "找不到相應的景點"}), 400
    
        connection.commit()
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
    finally:
        if connection:
            connection.close()
    return jsonify({"ok": True}), 200

app.run(host="0.0.0.0", port=3000)

# CREATE TABLE users (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(50) UNIQUE NOT NULL,
#     password VARCHAR(255) NOT NULL
# );