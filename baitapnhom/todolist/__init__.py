from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from datetime import timedelta
from sqlalchemy import text

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
DB_NAME = os.environ.get("DB_NAME")

db = SQLAlchemy()

def create_database(app):
    if not os.path.exists("todolist/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Created Database!")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    from .views import views
    from .user import user
    from .models import User, Task
    from .admin import admin
    
    create_database(app)
    with app.app_context():
        db.create_all()
        # Ensure new columns exist for existing SQLite DBs (simple auto-migration)
        try:
            cols = db.session.execute(text("PRAGMA table_info(user)")).fetchall()
            col_names = {c[1] for c in cols}
            if "is_admin" not in col_names:
                db.session.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                db.session.commit()
        except Exception:
            db.session.rollback()
        # Seed default admin account if not exists
        from werkzeug.security import generate_password_hash
        admin_email = "admin@gmail.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin is None:
            admin_user = User(
                email=admin_email,
                password=generate_password_hash("admin123"),
                user_name="admin",
                is_admin=True,
            )
            db.session.add(admin_user)
            db.session.commit()
    
    app.register_blueprint(user)
    app.register_blueprint(views)
    app.register_blueprint(admin)

    login_manager = LoginManager()
    login_manager.login_view = "user.login"
    login_manager.init_app(app)
    app.permanent_session_lifetime = timedelta(minutes=1)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app  