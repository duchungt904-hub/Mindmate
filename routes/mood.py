from flask import Blueprint, request, jsonify, session
from models import Mood, Chat
from database import Database
from utils import GPTService
from datetime import datetime

mood_bp = Blueprint('mood', __name__, url_prefix='/api/mood')
db = Database()
mood_model = Mood(db)
chat_model = Chat(db)
gpt_service = GPTService()

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "未登录"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@mood_bp.route('/set', methods=['POST'])
@login_required
def set_mood():
    """手动设置心情"""
    user_id = session['user_id']
    data = request.get_json()
    
    date = data.get('date')
    mood_emoji = data.get('mood_emoji')
    
    if not all([date, mood_emoji]):
        return jsonify({"success": False, "error": "缺少必填字段"}), 400
    
    result = mood_model.set_mood(user_id, date, mood_emoji, source='manual')
    return jsonify(result), 200

@mood_bp.route('/auto-analyze', methods=['POST'])
@login_required
def auto_analyze_mood():
    """自动分析聊天内容并设置心情"""
    user_id = session['user_id']
    data = request.get_json()
    
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # 获取当天的聊天消息
    messages = chat_model.get_recent_messages_for_mood(user_id, date)
    
    if not messages:
        return jsonify({"success": False, "error": "当天没有聊天记录"}), 400
    
    # 合并所有消息
    combined_text = " ".join(messages)
    
    # 使用 GPT 分析心情
    mood_emoji = gpt_service.analyze_mood_from_text(combined_text)
    
    # 保存心情
    result = mood_model.set_mood(user_id, date, mood_emoji, source='auto')
    
    if result['success']:
        return jsonify({
            "success": True,
            "date": date,
            "mood_emoji": mood_emoji
        }), 200
    else:
        return jsonify(result), 500

@mood_bp.route('/get', methods=['GET'])
@login_required
def get_mood():
    """获取某天的心情"""
    user_id = session['user_id']
    date = request.args.get('date')
    
    if not date:
        return jsonify({"success": False, "error": "缺少日期参数"}), 400
    
    mood = mood_model.get_mood(user_id, date)
    
    if mood:
        return jsonify({"success": True, "mood": mood}), 200
    else:
        return jsonify({"success": False, "error": "当天没有心情记录"}), 404

@mood_bp.route('/month', methods=['GET'])
@login_required
def get_month_moods():
    """获取某个月的所有心情，并自动分析今天的心情"""
    user_id = session['user_id']
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    if not year or not month:
        # 默认使用当前月份
        now = datetime.now()
        year = now.year
        month = now.month
    
    moods = mood_model.get_month_moods(user_id, year, month)
    
    # 自动分析今天的心情（如果今天还没有记录）
    today = datetime.now().strftime('%Y-%m-%d')
    today_has_mood = any(m['date'] == today for m in moods)
    
    if not today_has_mood:
        # 尝试自动分析今天的心情
        messages = chat_model.get_recent_messages_for_mood(user_id, today)
        
        if messages and len(messages) > 0:
            # 有聊天记录，分析心情
            combined_text = " ".join(messages)
            mood_emoji = gpt_service.analyze_mood_from_text(combined_text)
            
            # 保存心情
            mood_model.set_mood(user_id, today, mood_emoji, source='auto')
            
            # 重新加载心情数据
            moods = mood_model.get_month_moods(user_id, year, month)
    
    return jsonify({
        "success": True,
        "year": year,
        "month": month,
        "moods": moods
    }), 200
