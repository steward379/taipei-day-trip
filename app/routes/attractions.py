from flask import Blueprint, jsonify, request, Response
from app import app, db
from app.models import Attraction, AttractionImage
import json
from collections import OrderedDict
from sqlalchemy import func

attractions_bp = Blueprint('attractions', __name__)

def fetch_images_for_attraction(attraction_id):
    images = AttractionImage.query.filter_by(attraction_id=attraction_id).all()
    return [image.image_url for image in images]

def fetch_attraction_data(attraction):
    images = fetch_images_for_attraction(attraction.id)
    return {
        "id": attraction.id,
        "name": attraction.name,
        "category": attraction.CAT,
        "description": attraction.description,
        "address": attraction.address,
        "mrt": attraction.MRT,
        "transport": attraction.direction,
        "lat": attraction.latitude,
        "lng": attraction.longitude,
        "images": images
    }

@attractions_bp.route('/api/attractions', methods=['GET'])
def get_attractions():
    try:
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", None)
        mrt_only = request.args.get("mrtOnly", "false").lower() == "true"

        query = Attraction.query

        if keyword:
            if mrt_only:
                query = query.filter(Attraction.MRT == keyword)
            else:
                query = query.filter((Attraction.name.like(f"%{keyword}%")) | (Attraction.MRT == keyword))

        attractions = query.offset(page * 12).limit(12).all()
        total_count = query.count()

        is_last_page = (page * 12 + len(attractions)) >= total_count
        next_page = None if is_last_page else page + 1

        response = {
            "nextPage": next_page,
            "data": [fetch_attraction_data(attraction) for attraction in attractions]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

# 路由來獲取特定 ID 的景點
@attractions_bp.route('/api/attraction/<int:attraction_id>', methods=['GET'])
def get_attraction_by_id(attraction_id):
    try:
        attraction = Attraction.query.get(attraction_id)
        if attraction is None:
            return jsonify({"error": True, "message": "找不到該編號的景點"}), 400
        return jsonify({"data":fetch_attraction_data(attraction)}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

# 路由來獲取 MRT 清單
@attractions_bp.route('/api/mrts', methods=['GET'])
def get_mrts():
    try:
        # 使用 SQLAlchemy 的 aggregation 函數來計算每個 MRT 的景點數量
        # mrts = Attraction.query.with_entities(Attraction.MRT, func.count(Attraction.id)).group_by(Attraction.MRT).all()
        mrts = db.session.query(Attraction.MRT, func.count(Attraction.id)).group_by(Attraction.MRT).all()
        mrts = [mrt[0] for mrt in mrts if mrt[0] is not None]
        return jsonify({"data": mrts}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500