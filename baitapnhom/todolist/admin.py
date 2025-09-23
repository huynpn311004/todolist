from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from .models import User, Task
from . import db

admin = Blueprint("admin", __name__)

def _require_admin():
    if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
        abort(403)

@admin.route("/admin")
@login_required
def dashboard():
    _require_admin()
    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin/index.html", user=current_user, users=users)

@admin.route("/admin/delete-user", methods=["POST"])
@login_required
def delete_user():
    _require_admin()
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "missing user_id"}), 400
    target = User.query.get(user_id)
    if not target:
        return jsonify({"code": 404}), 404
    if target.id == current_user.id:
        return jsonify({"code": 400, "message": "cannot delete self"}), 400
    try:
        db.session.delete(target)
        db.session.commit()
        return jsonify({"code": 200})
    except Exception:
        db.session.rollback()
        return jsonify({"code": 500}), 500


