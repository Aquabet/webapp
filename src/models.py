from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    account_created = Column(DateTime, default=datetime.now())
    account_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

class Image(db.Model):
    __tablename__ = 'images'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.now(), nullable=False)
    user_id = Column(String(36), db.ForeignKey('users.id'), nullable=False)