from flask import Blueprint, request, jsonify, session
from models import User
from database import Database
import secrets
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
db = Database()
user_model = User(db)

# Token 存储（简单的内存存储，生产环境应使用 Redis）
active_tokens = {}  # {token: {user_id, expires_at}}

def generate_token():
    """生成随机 token"""
    return secrets.token_urlsafe(32)

def verify_token(token):
    """验证 token 并返回 user_id"""
    if not token or token not in active_tokens:
        return None
    
    token_data = active_tokens[token]
    
    # 检查是否过期
    if token_data['expires_at'] < time.time():
        del active_tokens[token]
        return None
    
    return token_data['user_id']

def get_token_from_request():
    """从请求中获取 token（支持多种方式）"""
    # 1. 从 Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.replace('Bearer ', '')
    
    # 2. 从请求体
    if request.is_json:
        token = request.get_json().get('token')
        if token:
            return token
    
    # 3. 从 URL 参数
    token = request.args.get('token')
    if token:
        return token
    
    # 4. 向后兼容：从 session
    user_id = session.get('user_id')
    if user_id:
        return f"session_{user_id}"
    
    return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({"success": False, "error": "缺少必填字段"}), 400
    
    # 使用用户名作为邮箱（为了兼容数据库结构）
    email = f"{username}@mindmate.local"
    
    result = user_model.create_user(email, username, password)
    
    if result['success']:
        user_id = result['user_id']
        
        # 生成 token
        token = generate_token()
        active_tokens[token] = {
            'user_id': user_id,
            'expires_at': time.time() + 86400  # 24小时
        }
        
        # 同时设置 session（向后兼容）
        session['user_id'] = user_id
        session.permanent = True  # 设置为永久 session
        
        result['token'] = token
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    login_id = data.get('login_id')  # email 或 username
    password = data.get('password')
    
    if not all([login_id, password]):
        return jsonify({"success": False, "error": "缺少必填字段"}), 400
    
    result = user_model.verify_user(login_id, password)
    
    if result['success']:
        user_id = result['user_id']
        
        # 生成 token
        token = generate_token()
        active_tokens[token] = {
            'user_id': user_id,
            'expires_at': time.time() + 86400  # 24小时
        }
        
        # 同时设置 session（向后兼容）
        session['user_id'] = user_id
        session.permanent = True  # 设置为永久 session
        
        result['token'] = token
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    # 获取并删除 token
    token = get_token_from_request()
    if token and token in active_tokens:
        del active_tokens[token]
    
    # 清除 session
    session.pop('user_id', None)
    
    return jsonify({"success": True}), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查用户是否已登录"""
    # 优先从 token 获取 user_id
    token = get_token_from_request()
    user_id = None
    
    if token:
        user_id = verify_token(token)
    
    # 向后兼容：从 session 获取
    if not user_id:
        user_id = session.get('user_id')
    
    if user_id:
        user = user_model.get_user_by_id(user_id)
        if user:
            return jsonify({"authenticated": True, "user": user}), 200
    
    return jsonify({"authenticated": False}), 200

@auth_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """获取用户统计信息（仅管理员或测试使用）"""
    from database import db_manager
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # 获取总用户数
        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        
        # 获取最近注册的用户（最多10个）
        cursor.execute("""
            SELECT id, username, created_at 
            FROM Users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = []
        for row in cursor.fetchall():
            recent_users.append({
                'id': row[0],
                'username': row[1],
                'created_at': row[2]
            })
        
        conn.close()
        
        return jsonify({
            "success": True,
            "total_users": total_users,
            "recent_users": recent_users
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取用户统计失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
