from app import db
from geoalchemy2 import Geometry

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Attraction(db.Model):
    __tablename__ = 'attractions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=True)
    CAT = db.Column(db.String(30), nullable=True)
    MRT = db.Column(db.String(30), nullable=True)
    idpt = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    location = db.Column(Geometry(geometry_type='POINT'), nullable=True)
    direction = db.Column(db.String(2000), nullable=True)
    rate = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(2000), nullable=True)
    # ... other fields

class AttractionImage(db.Model):
    __tablename__ = 'attraction_images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=True)
    attraction_name = db.Column(db.String(30), db.ForeignKey('attractions.name'), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    attraction = db.relationship('Attraction', foreign_keys=[attraction_id])


# CREATE TABLE users (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(50) UNIQUE NOT NULL,
#     password VARCHAR(255) NOT NULL
# );

# CREATE TABLE bookings (     
#     id INT AUTO_INCREMENT PRIMARY KEY,     
#     user_id INT,     
#     attraction_id INT,    
#     attraction_name VARCHAR(255),     
#     attraction_address VARCHAR(255),     
#     attraction_image VARCHAR(255),     
#     date DATE NOT NULL,     
#     time ENUM('morning', 'afternoon') NOT NULL,     
#     price DECIMAL(10, 2) NOT NULL,     
#     FOREIGN KEY (user_id) REFERENCES users(id),     
#     FOREIGN KEY (attraction_id) REFERENCES attractions(id) 
# );