from .import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Date

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
