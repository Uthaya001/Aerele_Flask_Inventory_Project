from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'product'
    
    product_id = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    movements = db.relationship('ProductMovement', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.product_id}: {self.product_name}>'


class Location(db.Model):
    __tablename__ = 'location'
    
    location_id = db.Column(db.String(50), primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    
    movements_from = db.relationship('ProductMovement', foreign_keys='ProductMovement.from_location', backref='from_loc', lazy=True)
    movements_to = db.relationship('ProductMovement', foreign_keys='ProductMovement.to_location', backref='to_loc', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.location_id}: {self.location_name}>'


class ProductMovement(db.Model):
    __tablename__ = 'product_movement'
    
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.product_id} - {self.qty}>'
    
    def get_movement_type(self):
        if self.from_location and self.to_location:
            return 'Transfer'
        elif self.to_location:
            return 'IN'
        elif self.from_location:
            return 'OUT'
        return 'Unknown'
