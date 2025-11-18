import os
import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import Database
from routes import auth_bp, profile_bp, avatar_bp, chat_bp, mood_bp

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大上传大小

# Session 配置（支持移动端和跨设备访问）
app.config['SESSION_COOKIE_NAME'] = 'mindmate_session'  # 自定义 Cookie 名称
app.config['SESSION_COOKIE_SAMESITE'] = None  # 完全允许跨站
app.config['SESSION_COOKIE_SECURE'] = False  # HTTP 环境
app.config['SESSION_COOKIE_HTTPONLY'] = False  # 允许 JavaScript 访问（方便调试）
app.config['SESSION_COOKIE_DOMAIN'] = None  # 不限制域名（关键！）
app.config['SESSION_COOKIE_PATH'] = '/'  # 所有路径
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # 每次请求刷新

# 启用 CORS（完全开放配置）
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Set-Cookie"])

# 初始化数据库
db = Database(os.getenv('DATABASE_PATH', 'mindmate.db'))

# 注册蓝图（API 路由）
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(avatar_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(mood_bp)

# Token 认证中间件
@app.before_request
def check_token_auth():
    """在每个请求前检查 token 认证"""
    from routes.auth import get_token_from_request, verify_token
    
    # 跳过公开路由
    public_routes = ['/login', '/register', '/api/auth/login', '/api/auth/register', '/static', '/test-login', '/test']
    if any(request.path.startswith(route) for route in public_routes):
        return
    
    # 检查 token
    token = get_token_from_request()
    if token:
        user_id = verify_token(token)
        if user_id:
            # 将 user_id 设置到 session 中（向后兼容）
            session['user_id'] = user_id
            return
    
    # 检查 session（向后兼容）
    if 'user_id' in session:
        return
    
    # 对于 API 请求，返回 401
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "未授权"}), 401
    
    # 对于页面请求，重定向到登录页
    if request.path not in ['/', '/login', '/register']:
        return redirect(url_for('login'))

# 页面路由
@app.route('/')
def index():
    """首页 - 重定向到登录或主页"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """登录页面"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html', show_nav=False)

@app.route('/register')
def register():
    """注册页面"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('register.html', show_nav=False)

@app.route('/home')
def home():
    """主页"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', show_nav=True, active_page='home')

@app.route('/profile')
def profile():
    """个人资料页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from models import UserProfile
    profile_model = UserProfile(db)
    user_profile = profile_model.get_profile(session['user_id'])
    
    return render_template('profile.html', 
                         show_nav=True, 
                         active_page='profile',
                         profile=user_profile or {})

@app.route('/avatar')
def avatar():
    """Avatar 列表页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('avatars.html', show_nav=True, active_page='avatar')

@app.route('/chat')
def chat():
    """聊天页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', show_nav=True, active_page='chat')

@app.route('/calendar')
def calendar():
    """日历页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('calendar.html', show_nav=True, active_page='calendar')

@app.route('/test-login')
def test_login():
    """测试登录页面（用于调试）"""
    return render_template('test_login.html')

@app.route('/test')
def test():
    """简单测试页面（无需登录）"""
    return render_template('test.html')

# 错误处理
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs('static/uploads/avatars', exist_ok=True)
    os.makedirs('static/uploads/avatar_images', exist_ok=True)
    
    # 运行应用
    port = int(os.getenv('PORT', 5001))  # Render 会提供 PORT 环境变量
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'True') == 'True'
    )
