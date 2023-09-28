from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

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

from app.routes import main, user, attractions
app.register_blueprint(main.main_bp)
app.register_blueprint(user.user_bp)
app.register_blueprint(attractions.attractions_bp)
