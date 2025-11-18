from flask import Blueprint, request, jsonify, session
from models import UserProfile
from database import Database
from utils import save_uploaded_file
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
db = Database()
profile_model = UserProfile(db)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "未登录"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@profile_bp.route('/', methods=['GET'])
@login_required
def get_profile():
    """获取用户资料"""
    user_id = session['user_id']
    profile = profile_model.get_profile(user_id)
    
    if profile:
        return jsonify({"success": True, "profile": profile}), 200
    else:
        return jsonify({"success": False, "error": "资料不存在"}), 404

@profile_bp.route('/', methods=['POST'])
@login_required
def update_profile():
    """更新用户资料"""
    user_id = session['user_id']
    
    # 处理表单数据
    name = request.form.get('name')
    gender = request.form.get('gender')
    date_birth = request.form.get('date_birth')
    goal = request.form.get('goal')
    self_description = request.form.get('self_description')
    
    # 更新资料（不处理头像）
    result = profile_model.update_profile(
        user_id,
        name=name,
        gender=gender,
        date_birth=date_birth,
        goal=goal,
        self_description=self_description
    )
    
    return jsonify(result), 200
