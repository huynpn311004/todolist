from math import e
from re import template
from flask import Blueprint,render_template, request, flash, session, url_for, current_app
from sqlalchemy.sql.expression import false
from .models import User, PasswordResetToken
from werkzeug.security import generate_password_hash, check_password_hash
from .import db, mail
from flask_login import login_user, logout_user, login_required, current_user
from flask import redirect, url_for
from flask_mail import Message


user = Blueprint("user",__name__)

@user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        
        # Yêu cầu phải nhập đầy đủ cả email, username và password
        if not email or not user_name or not password:
            flash("Vui lòng nhập đầy đủ email, tên đăng nhập và mật khẩu!", category="error")
            return render_template("login.html", user=current_user)
        
        # Tìm user theo email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Kiểm tra username có khớp với user tìm được không
            if user.user_name != user_name:
                flash("Email và tên đăng nhập không khớp với cùng một tài khoản!", category="error")
                return render_template("login.html", user=current_user)
            
            # Kiểm tra password
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
            flash("Email không tồn tại trong hệ thống!", category="error")
    return render_template("login.html", user=current_user)
    
@user.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_name = request.form.get("user_name") 
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

@user.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("Vui lòng nhập email.", category="error")
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                # Xóa các token cũ của user này
                PasswordResetToken.query.filter_by(user_id=user.id, used=False).delete()
                
                # Tạo token mới
                reset_token = PasswordResetToken(user.id)
                db.session.add(reset_token)
                db.session.commit()
                
                # Gửi email
                try:
                    reset_url = url_for('user.reset_password', token=reset_token.token, _external=True)
                    sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@todolist.com')
                    msg = Message(
                        subject='Reset Password - TodoList App',
                        sender=sender_email,
                        recipients=[user.email]
                    )
                    msg.html = f"""
                    <h2>Reset Password</h2>
                    <p>Xin chào {user.user_name},</p>
                    <p>Bạn đã yêu cầu reset mật khẩu cho tài khoản TodoList của mình.</p>
                    <p>Nhấn vào link bên dưới để reset mật khẩu:</p>
                    <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
                    <p>Link này sẽ hết hạn sau 1 giờ.</p>
                    <p>Nếu bạn không yêu cầu reset mật khẩu, vui lòng bỏ qua email này.</p>
                    <p>Trân trọng và cảm ơn bạn đã sử dụng TodoList.Chúc bạn có một ngày tốt lành,<br>TodoList Team</p>
                    """
                    mail.send(msg)
                    flash("Email reset mật khẩu đã được gửi! Vui lòng kiểm tra hộp thư.", category="success")
                except Exception as e:
                    print("Lỗi gửi email:", e)
                    flash("Có lỗi khi gửi email. Vui lòng thử lại sau.", category="error")
            else:
                flash("Email không tồn tại trong hệ thống.", category="error")
    return render_template("forgot_password.html", user=current_user)

@user.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token:
        flash("Token không hợp lệ hoặc đã hết hạn.", category="error")
        return redirect(url_for('user.forgot_password'))
    
    if not reset_token.is_valid():
        flash("Token đã hết hạn hoặc đã được sử dụng.", category="error")
        return redirect(url_for('user.forgot_password'))
    
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        if not new_password or not confirm_password:
            flash("Vui lòng nhập đầy đủ mật khẩu mới và xác nhận.", category="error")
        elif len(new_password) != 8:
            flash("Mật khẩu phải đúng 8 ký tự.", category="error")
        elif new_password != confirm_password:
            flash("Xác nhận mật khẩu không trùng khớp.", category="error")
        else:
            try:
                user = User.query.get(reset_token.user_id)
                user.password = generate_password_hash(new_password)
                reset_token.used = True
                db.session.commit()
                flash("Reset mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.", category="success")
                return redirect(url_for('user.login'))
            except Exception as e:
                db.session.rollback()
                print("Lỗi reset mật khẩu:", e)
                flash("Có lỗi khi reset mật khẩu.", category="error")
    
    return render_template("reset_password.html", user=current_user, token=token)