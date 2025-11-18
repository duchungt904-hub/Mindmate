from flask import Blueprint, request, jsonify, session
from models import Chat, UserProfile, Avatar
from database import Database
from utils import GPTService

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
db = Database()
chat_model = Chat(db)
profile_model = UserProfile(db)
avatar_model = Avatar(db)
gpt_service = GPTService()

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "未登录"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@chat_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """获取聊天历史（可按 avatar_id 过滤）"""
    user_id = session['user_id']
    limit = request.args.get('limit', 50, type=int)
    avatar_id = request.args.get('avatar_id', type=int)  # 可选的 avatar_id 参数
    
    history = chat_model.get_chat_history(user_id, avatar_id, limit)
    return jsonify({"success": True, "history": history}), 200

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """发送消息并获取 AI 回复"""
    user_id = session['user_id']
    data = request.get_json()
    
    user_message = data.get('message')
    avatar_id = data.get('avatar_id')  # 获取 avatar_id 参数
    
    if not user_message:
        return jsonify({"success": False, "error": "消息不能为空"}), 400
    
    if not avatar_id:
        return jsonify({"success": False, "error": "请指定 Avatar"}), 400
    
    # 获取 Avatar 配置
    avatar = avatar_model.get_avatar_by_id(avatar_id, user_id)
    
    if not avatar:
        return jsonify({"success": False, "error": "Avatar 不存在或无权限"}), 400
    
    # 保存用户消息
    chat_model.save_message(user_id, avatar_id, 'user', user_message)
    
    # 获取用户资料
    user_profile = profile_model.get_profile(user_id)
    
    # 确定使用的系统提示
    if avatar['persona_id'] == 5 and avatar['custom_persona']:  # User-defined
        system_prompt = avatar['custom_persona']
    else:
        system_prompt = avatar['system_prompt']
    
    # 获取聊天历史（只获取该 Avatar 的历史）
    chat_history = chat_model.get_chat_history(user_id, avatar_id, limit=10)
    
    # 生成 AI 回复
    response = gpt_service.generate_response(
        user_message,
        chat_history,
        system_prompt,
        user_profile
    )
    
    if response['success']:
        ai_message = response['message']
        
        # 保存 AI 回复
        chat_model.save_message(user_id, avatar_id, 'ai', ai_message)
        
        return jsonify({
            "success": True,
            "user_message": user_message,
            "ai_message": ai_message
        }), 200
    else:
        # API 调用失败，但还是返回一个友好的回复
        error_message = response.get('message', response.get('error', '抱歉，我现在无法回复。'))
        
        # 保存错误消息（让用户看到）
        chat_model.save_message(user_id, avatar_id, 'ai', error_message)
        
        return jsonify({
            "success": True,  # 改为 True，让前端正常显示
            "user_message": user_message,
            "ai_message": error_message
        }), 200
