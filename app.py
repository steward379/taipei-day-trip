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
import requests
import uuid

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
app_key=os.environ.get("APP_KEY")
app_id=os.environ.get("APP_ID")
partner_key=os.environ.get("PARTNER_KEY")

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

def get_user_id_from_jwt():

    token = request.headers.get("Authorization")

    if not token:
        print(f"no token: {token}")  
        return None
    try:
        data = decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return data
    except Exception as e:
        print(f"An error occurred: {e}")  # 考慮使用更進階的日誌記錄方式
        return None

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
    return render_template("booking.html",  app_id = app_id, app_key = app_key)

@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/member/<member_id>")
def member(member_id):
	return render_template("member.html")

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
# check login status
@app.route("/api/user/auth", methods=["GET"])
def get_user():
    userData = get_user_id_from_jwt()
    if userData is not None:
        userData.pop("exp")
    return jsonify({"data": userData}), 200

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

    user_data = get_user_id_from_jwt()
    
    if user_data is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    
    user_id = user_data["id"]

    connection = connect_to_db()
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    # cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
    sql_query = """
    SELECT 
        b.*, 
        a.name as attraction_name, 
        a.address as attraction_address, 
        ai.image_url as attraction_image 
    FROM 
        bookings b
    LEFT JOIN 
        attractions a ON b.attraction_id = a.id
    LEFT JOIN (
        SELECT attraction_id, MIN(id) as min_id
        FROM attraction_images
        GROUP BY attraction_id
    ) subq ON b.attraction_id = subq.attraction_id
    LEFT JOIN 
        attraction_images ai ON ai.id = subq.min_id
    WHERE 
        b.user_id = %s  AND b.order_id IS NULL
    """
    cursor.execute(sql_query, (user_id,))
    # booking_data = cursor.fetchone()
    booking_data_list = cursor.fetchall()

    connection.close()

    response_data_list = []

    for booking_data in booking_data_list:
    # if booking_data:
        if booking_data["attraction_id"] is None or booking_data["attraction_name"] is None:
            # response_data = None
            continue
        else:
            response_data = {
                "id": booking_data["id"],
                "attraction": {
                    "id": booking_data["attraction_id"],
                    "name": booking_data["attraction_name"],
                    "address": booking_data["attraction_address"],
                    "image": booking_data["attraction_image"]
                },
                "date": booking_data["date"],
                "time": booking_data["time"],
                "price": booking_data["price"]
            }
            response_data_list.append(response_data)

    connection.close()

    if response_data_list:
        # return jsonify({"data": response_data}), 200
        return jsonify({"data": response_data_list}), 200
    else:
        return jsonify({"data": None}), 200

@app.route("/api/booking", methods=["POST"])
def post_booking():
    user_data = get_user_id_from_jwt()
    
    if user_data is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    
    user_id = user_data["id"]

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

    # 單筆訂單

    # cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
    # existing_booking = cursor.fetchone()

    # if existing_booking:
    #     cursor.execute("UPDATE bookings SET attraction_id = %s, date = %s, time = %s, price = %s WHERE user_id = %s",
    #                    (attraction_id, data["date"], data["time"], data["price"], user_id))
    # else:
    cursor.execute("INSERT INTO bookings (user_id, attraction_id, date, time, price) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, attraction_id, data["date"], data["time"], data["price"]))
        
    connection.commit()
    connection.close()

    return jsonify({"ok": True}), 200

@app.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def delete_looking(booking_id):
    try:
        user_data = get_user_id_from_jwt()
    
        if user_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
        
        user_id = user_data["id"]

        connection = connect_to_db()
        if connection is None:
            return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
        cursor = connection.cursor()

        # cursor.execute("DELETE FROM bookings WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM bookings WHERE id = %s AND user_id = %s  AND order_id IS NULL", (booking_id, user_id))

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


# 


# order-id factory
def generate_order_number(user_id):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S") 
    user_id_short = str(user_id)[:5]
    current_time_short = str(current_time)
    unique_id = uuid.uuid4().hex[:10]
    return f"{user_id_short }-{current_time_short}-{unique_id}"

# order-id factory
def generate_bank_id(bank_id):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S") 
    bank_id_short = str(bank_id)[:5]
    current_time_short = str(current_time)[:11]
    unique_id = uuid.uuid4().hex[:4].upper()
    return f"{bank_id_short}-{current_time_short}-{unique_id}".upper()

@app.route("/api/order/<order_number>", methods=["GET"])
def get_order(order_number):
    user_data = get_user_id_from_jwt()

    if user_data is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    
    user_id = user_data["id"]

    try:
        connection = connect_to_db()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM orders WHERE order_number = %s", (order_number,))
        order = cursor.fetchone()
        
        if order is None:
            return jsonify({"error": True, "message": "找不到該訂單"}), 400

        # order["trip"] = json.loads(order["trip"])
        # order["contact"] = json.loads(order["contact"])
                # 查詢相關的 booking 資訊
        sql_query_booking = """
        SELECT 
            b.*, 
            a.name as attraction_name, 
            a.address as attraction_address, 
            (SELECT MIN(ai.image_url) FROM attraction_images ai WHERE ai.attraction_id = a.id) as attraction_image 
        FROM 
            bookings b
        LEFT JOIN 
            attractions a ON b.attraction_id = a.id
        WHERE 
            b.order_id = %s
        """
        cursor.execute(sql_query_booking, (order['id'],))
        booking_data_list = cursor.fetchall()

        # 組裝最終的回應資料
        response_data = OrderedDict([
            ("number", order['order_number']),
            ("price", float(order['total_price'])),  # 轉換為 float
            ("trips", []),
            ("contact", OrderedDict([
                ("name", order['contact_name']),
                ("email", order['contact_email']),
                ("phone", order['contact_phone'])
            ])),
            ("status", order['payment_status'])
        ])

        seen_attraction_ids = set()

        for booking_data in booking_data_list:
            if booking_data["attraction_id"] is not None and booking_data["attraction_name"] is not None:
                trip_info = OrderedDict([
                    ("attraction", OrderedDict([
                        ("id", booking_data["attraction_id"]),
                        ("name", booking_data["attraction_name"]),
                        ("address", booking_data["attraction_address"]),
                        ("image", booking_data["attraction_image"])
                    ])),
                    ("date", str(booking_data["date"])),  # 轉換為正確的日期格式
                    ("time", booking_data["time"])
                ])
                response_data["trips"].append(trip_info)

        connection.close()

        return jsonify({"data": response_data }), 200
    except Exception as e:
        print(e)
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
    

@app.route("/api/orders", methods=["POST"])
def orders():
    user_data = get_user_id_from_jwt()

    if user_data is None:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    
    user_id = user_data["id"]

    data = request.json

    prime = data.get("prime", "")
    order = data.get("order", {})
    price = order.get("price", 0)
    trips = order.get("trips", [])
    contact = order.get("contact", {})

    if not prime or not order or price == 0:
        return jsonify({
            "error": True,
            "message": "請求資料不完整"
        }), 400
    
    # order ID
    # 由小於五十位的英數位元所自行定義的訂單編號，用於 TapPay 做訂單識別，可重複帶入。若有帶入此欄位，則不可為空

    order_number = generate_order_number(user_id)
    # order_number = order_number.replace("-", "")

    merchant_id_token = "ESUN"
    bank_transaction_id_primitive = generate_bank_id(merchant_id_token)
    bank_transaction_id = bank_transaction_id_primitive.replace("-", "")


    total_trips = len(trips)   
    # num_to_print = 1 if total_trips == 1 else 2
    num_to_print = 1 
    trip_details = []
    for i, trip in enumerate(trips[:num_to_print]):
        name = trip['attraction'].get('name', '')
        date = trip.get('date', '')
        time = trip.get('time', '')
        trip_details.append(f"{name} ({date}, {time})")
    details_info = f"共 {total_trips} 個一日遊：{'、'.join(trip_details)}"

    # 設置 TapPay 的 API 參數
    tappay_data = {
        # direct pay
        # "prime": "test_3a2fb2b7e892b914a03c95dd4dd5dc7970c908df67a49527c0a648b2bc9",
        "prime" : prime ,
        "partner_key": partner_key,
        "merchant_id": "murmurline_ESUN",
        "amount": 100,
        "currency": "TWD", # 預設值
        "bank_transaction_id" : bank_transaction_id,
        "details": details_info,
        "cardholder": {
            "phone_number": contact.get("phone"),
            "name": contact.get("name"),
            "email": contact.get("email"),
            "zip_code": "",
            "address": "",
            "national_id": "",
            "member_id" : user_id,
        },
        "remember": True,
        "order_number": order_number,
    }

    headers = {
        "x-api-key": partner_key
    }   
    
    # 調用 TapPay API
    response = requests.post(
        "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
        headers=headers,
        json=tappay_data
    )

    result = response.json()
    
    # rec_trace_id 退款時使用
    # 處理付款結果
    if result["status"] == 0:
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            sql_insert_order = """
            INSERT INTO orders (user_id, order_number, payment_status, contact_name, contact_email, contact_phone, total_price) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert_order, (user_id, order_number, 0, contact.get("name"), contact.get("email"), contact.get("phone"), price))  # 0 表示付款成功

            # 獲取剛剛插入的訂單ID
            order_id = cursor.lastrowid

            for trip in trips:
                booking_id = trip.get("bookingId")
            
                sql_insert_or_update_booking = """
                UPDATE bookings 
                SET order_id = %s 
                WHERE id = %s
                """
                cursor.execute(sql_insert_or_update_booking, (order_id, booking_id))

            # # 更新 `bookings` 資料表的 `order_id`
            # sql_update_booking = """
            # UPDATE bookings SET order_id = %s WHERE user_id = %s
            # """
            # cursor.execute(sql_update_booking, (order_id, user_id))

            connection.commit()
            connection.close()

            print('database completed!')

        except Exception as e:
            print(e)
            return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
        return jsonify({
            "data": {
                "number": order_number,  # 請換成你的訂單編號
                "payment": {
                    "status": 0,
                    "message": "付款成功"
                }
            }
        })
    else:
        return jsonify({
            "error": True,
            "message": str(result["status"]) + result["msg"]
        }), 500

app.run(host="0.0.0.0", port=3000)