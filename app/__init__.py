from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from dbutils.pooled_db import PooledDB
import MySQLdb
import jwt

# Load environment variables
load_dotenv(".env")

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}?charset={os.environ.get('DB_CHARSET')}"

# 設置連接池的大小和超時時間
app.config['SQLALCHEMY_POOL_SIZE'] = 5  # 資料庫連接池的大小。預設是資料庫引擎的預設值 （通常是 5）。
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 10  # 指定資料庫連接池的超時時間。預設是 10。
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # 配置多久之後對連接池中的連接進行一次重新連接（重置），預設是 1800。

db = SQLAlchemy(app)

pool = PooledDB(
    creator=MySQLdb,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    setsession=[],
    user=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    db=os.environ.get("DB_NAME"),
    charset=os.environ.get("DB_CHARSET"),
)

def connect_to_db():
    return pool.connection()

def get_user_id_from_jwt():
    token = request.headers.get("Authorization")
    if not token:
        return None
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return data
    except Exception as e:
        return None

from app.routes import main, user, attractions
app.register_blueprint(main.main_bp)
app.register_blueprint(user.user_bp)
app.register_blueprint(attractions.attractions_bp)
