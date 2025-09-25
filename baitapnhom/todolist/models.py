from .import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Date
import secrets
from datetime import datetime, timedelta

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Chưa xong")
    priority = db.Column(db.String(20), nullable=False, default="trung bình")
    start_date = db.Column(Date, nullable=True)
    end_date = db.Column(Date, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship("Task", cascade="all, delete-orphan", lazy=True)

    def __init__(self,email,password,user_name,is_admin=False):
        self.email = email
        self.password = password
        self.user_name = user_name
        self.is_admin = is_admin

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, user_id):
        self.token = secrets.token_urlsafe(32)
        self.user_id = user_id
        self.expires_at = datetime.utcnow() + timedelta(hours=1)  # Token hết hạn sau 1 giờ
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired()
