from flask import Blueprint, request, jsonify, session
from models import Avatar
from database import Database
from utils import save_uploaded_file
import os

avatar_bp = Blueprint('avatar', __name__, url_prefix='/api/avatar')
db = Database()
avatar_model = Avatar(db)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "未登录"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@avatar_bp.route('/personas', methods=['GET'])
@login_required
def get_personas():
    """获取所有预设的 Persona"""
    personas = avatar_model.get_personas()
    return jsonify({"success": True, "personas": personas}), 200

@avatar_bp.route('/list', methods=['GET'])
@login_required
def get_all_avatars():
    """获取用户的所有 Avatar 列表"""
    user_id = session['user_id']
    avatars = avatar_model.get_all_avatars(user_id)
    return jsonify({"success": True, "avatars": avatars}), 200

@avatar_bp.route('/<int:avatar_id>', methods=['GET'])
@login_required
def get_avatar_by_id(avatar_id):
    """根据 ID 获取特定 Avatar"""
    user_id = session['user_id']
    avatar = avatar_model.get_avatar_by_id(avatar_id, user_id)
    
    if avatar:
        return jsonify({"success": True, "avatar": avatar}), 200
    else:
        return jsonify({"success": False, "error": "Avatar 不存在"}), 404

@avatar_bp.route('/', methods=['GET'])
@login_required
def get_avatar():
    """获取用户的默认 Avatar（兼容旧 API）"""
    user_id = session['user_id']
    avatar = avatar_model.get_avatar(user_id)
    
    if avatar:
        return jsonify({"success": True, "avatar": avatar}), 200
    else:
        return jsonify({"success": False, "error": "尚未配置 Avatar"}), 404

@avatar_bp.route('/create', methods=['POST'])
@login_required
def create_avatar():
    """创建新的 Avatar"""
    user_id = session['user_id']
    
    avatar_name = request.form.get('avatar_name')
    appearance_type = request.form.get('appearance_type')
    persona_id = request.form.get('persona_id')
    custom_persona = request.form.get('custom_persona')
    
    if not avatar_name or not appearance_type or not persona_id:
        return jsonify({"success": False, "error": "缺少必填字段"}), 400
    
    custom_image_path = None
    
    # 处理自定义头像上传
    if 'custom_image' in request.files:
        image_file = request.files['custom_image']
        if image_file and image_file.filename:
            upload_folder = os.path.join('static', 'uploads', 'avatar_images')
            custom_image_path = save_uploaded_file(image_file, upload_folder, f'avatar_{user_id}')
    
    result = avatar_model.create_avatar(
        user_id,
        avatar_name,
        appearance_type,
        custom_image_path,
        int(persona_id),
        custom_persona
    )
    
    return jsonify(result), 200

@avatar_bp.route('/<int:avatar_id>', methods=['PUT', 'POST'])
@login_required
def update_avatar(avatar_id):
    """更新 Avatar"""
    user_id = session['user_id']
    
    avatar_name = request.form.get('avatar_name')
    appearance_type = request.form.get('appearance_type')
    persona_id = request.form.get('persona_id')
    custom_persona = request.form.get('custom_persona')
    
    custom_image_path = None
    
    # 处理自定义头像上传
    if 'custom_image' in request.files:
        image_file = request.files['custom_image']
        if image_file and image_file.filename:
            upload_folder = os.path.join('static', 'uploads', 'avatar_images')
            custom_image_path = save_uploaded_file(image_file, upload_folder, f'avatar_{avatar_id}')
    
    result = avatar_model.update_avatar(
        avatar_id,
        user_id,
        avatar_name=avatar_name,
        appearance_type=appearance_type,
        custom_image_path=custom_image_path,
        persona_id=int(persona_id) if persona_id else None,
        custom_persona=custom_persona
    )
    
    return jsonify(result), 200

@avatar_bp.route('/<int:avatar_id>', methods=['DELETE'])
@login_required
def delete_avatar(avatar_id):
    """删除 Avatar"""
    user_id = session['user_id']
    result = avatar_model.delete_avatar(avatar_id, user_id)
    return jsonify(result), 200

@avatar_bp.route('/', methods=['POST'])
@login_required
def save_avatar():
    """保存或更新用户的 Avatar（兼容旧 API）"""
    user_id = session['user_id']
    
    appearance_type = request.form.get('appearance_type')
    persona_id = request.form.get('persona_id')
    custom_persona = request.form.get('custom_persona')
    
    if not appearance_type or not persona_id:
        return jsonify({"success": False, "error": "缺少必填字段"}), 400
    
    custom_image_path = None
    
    # 处理自定义头像上传
    if 'custom_image' in request.files:
        image_file = request.files['custom_image']
        if image_file and image_file.filename:
            upload_folder = os.path.join('static', 'uploads', 'avatar_images')
            custom_image_path = save_uploaded_file(image_file, upload_folder, f'avatar_{user_id}')
    
    result = avatar_model.create_or_update_avatar(
        user_id,
        appearance_type,
        custom_image_path,
        int(persona_id),
        custom_persona
    )
    
    return jsonify(result), 200
