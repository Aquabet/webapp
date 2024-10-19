from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50)) 
    last_name = db.Column(db.String(50))
    account_created = db.Column(db.DateTime, default=datetime.now)
    account_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
