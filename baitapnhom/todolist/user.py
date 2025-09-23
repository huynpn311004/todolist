from math import e
from re import template
from flask import Blueprint,render_template, request, flash, session
from sqlalchemy.sql.expression import false
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .import db
from flask_login import login_user, logout_user, login_required, current_user
from flask import redirect, url_for


user = Blueprint("user",__name__)

@user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        if user is None and user_name:
            user = User.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user, remember=True)
                flash("Đăng nhập thành công!", category="success")
                if getattr(user, "is_admin", False):
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("views.home"))
            else:
                flash("Sai mật khẩu, vui lòng thử lại!", category="error")
        else:
            flash("Không tìm thấy người dùng!", category="error")
    return render_template("login.html", user=current_user)
    
@user.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_name = request.form.get("user_name") # Assuming you have a 'user_name' field in your form
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email đã tồn tại.", category="error")
        elif len(email) < 4:
            flash("Email phải dài hơn 3 ký tự.", category="error")
        elif len(password) != 8:
            flash("Mật khẩu phải đúng 8 ký tự.", category="error")
        elif password != confirm_password:
            flash("Mật khẩu xác nhận không trùng khớp.", category="error")
        else:
            password=generate_password_hash(password)
            new_user = User(email, password,user_name)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Tạo tài khoản thành công! Vui lòng đăng nhập.", category="success")
                return redirect(url_for("user.login"))
            except Exception as e:
                print("Lỗi khi tạo tài khoản:", e)
                flash("Có lỗi khi tạo tài khoản!", category="error")
    return render_template("signup.html", user=current_user)

@user.route("/logout")
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.", category="success")
    return redirect(url_for("user.login"))

@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "info":
            new_email = request.form.get("email")
            new_username = request.form.get("user_name")
            if not new_email or not new_username:
                flash("Vui lòng nhập đầy đủ email và tên đăng nhập.", category="error")
            else:
                existing = User.query.filter(User.email == new_email, User.id != current_user.id).first()
                if existing:
                    flash("Email đã được sử dụng bởi tài khoản khác.", category="error")
                else:
                    current_user.email = new_email
                    current_user.user_name = new_username
                    try:
                        db.session.commit()
                        flash("Cập nhật thông tin thành công!", category="success")
                    except Exception as e:
                        db.session.rollback()
                        print("Lỗi cập nhật thông tin:", e)
                        flash("Có lỗi khi cập nhật thông tin.", category="error")
        elif form_type == "password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")
            if not current_password or not new_password or not confirm_password:
                flash("Vui lòng nhập đầy đủ các trường mật khẩu.", category="error")
            elif not check_password_hash(current_user.password, current_password):
                flash("Mật khẩu hiện tại không đúng.", category="error")
            elif len(new_password) != 8:
                flash("Mật khẩu mới phải đúng 8 ký tự.", category="error")
            elif new_password != confirm_password:
                flash("Xác nhận mật khẩu mới không trùng khớp.", category="error")
            else:
                try:
                    current_user.password = generate_password_hash(new_password)
                    db.session.commit()
                    flash("Đổi mật khẩu thành công!", category="success")
                except Exception as e:
                    db.session.rollback()
                    print("Lỗi đổi mật khẩu:", e)
                    flash("Có lỗi khi đổi mật khẩu.", category="error")
    return render_template("profile.html", user=current_user)
