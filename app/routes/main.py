from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")

@main_bp.route("/booking")
def booking():
    return render_template("booking.html")

@main_bp.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")
