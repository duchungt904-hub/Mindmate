from flask import Blueprint, jsonify, session
from database import Database
from models import User

demo_bp = Blueprint('demo', __name__, url_prefix='/api/demo')
db = Database()
user_model = User(db)

DEMO_USERNAME = 'test'
DEMO_EMAIL = 'test@mindmate.demo'
DEMO_PASSWORD = 'test'

@demo_bp.route('/clear', methods=['POST'])
def clear_demo_data():
    """清空 demo 测试账号的所有数据"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 查找 demo 用户
        cursor.execute("SELECT id FROM Users WHERE username = ? OR email = ?", 
                      (DEMO_USERNAME, DEMO_EMAIL))
        user = cursor.fetchone()
        
        if user:
            user_id = user['id']
            print(f"[DEMO] 清空用户 {DEMO_USERNAME} (ID: {user_id}) 的数据")
            
            # 1. 删除聊天记录
            cursor.execute("DELETE FROM ChatHistory WHERE user_id = ?", (user_id,))
            deleted_chats = cursor.rowcount
            
            # 2. 删除 Avatars
            cursor.execute("DELETE FROM Avatars WHERE user_id = ?", (user_id,))
            deleted_avatars = cursor.rowcount
            
            # 3. 删除心情记录
            cursor.execute("DELETE FROM MoodCalendar WHERE user_id = ?", (user_id,))
            deleted_moods = cursor.rowcount
            
            # 4. 清空用户资料（保留基本信息）
            cursor.execute("""
                UPDATE UserProfiles 
                SET name = NULL, 
                    gender = NULL, 
                    user_avatar_path = NULL, 
                    date_birth = NULL, 
                    goal = NULL, 
                    self_description = NULL
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"[DEMO] 已清空: {deleted_chats} 条聊天, {deleted_avatars} 个 Avatar, {deleted_moods} 条心情记录")
            
            return jsonify({
                "success": True,
                "message": "Demo data cleared",
                "deleted": {
                    "chats": deleted_chats,
                    "avatars": deleted_avatars,
                    "moods": deleted_moods
                }
            }), 200
        else:
            # 用户不存在，创建一个
            print(f"[DEMO] Demo 用户不存在，正在创建...")
            result = user_model.create_user(DEMO_EMAIL, DEMO_USERNAME, DEMO_PASSWORD)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": "Demo user created"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to create demo user"
                }), 500
                
    except Exception as e:
        print(f"[ERROR] 清空 demo 数据失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@demo_bp.route('/status', methods=['GET'])
def demo_status():
    """检查 demo 账号状态"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM Users WHERE username = ?", (DEMO_USERNAME,))
        user = cursor.fetchone()
        
        if user:
            user_id = user['id']
            
            # 统计数据
            cursor.execute("SELECT COUNT(*) as count FROM Avatars WHERE user_id = ?", (user_id,))
            avatar_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM ChatHistory WHERE user_id = ?", (user_id,))
            chat_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM MoodCalendar WHERE user_id = ?", (user_id,))
            mood_count = cursor.fetchone()['count']
            
            conn.close()
            
            return jsonify({
                "success": True,
                "exists": True,
                "data": {
                    "avatars": avatar_count,
                    "chats": chat_count,
                    "moods": mood_count
                }
            }), 200
        else:
            conn.close()
            return jsonify({
                "success": True,
                "exists": False
            }), 200
            
    except Exception as e:
        print(f"[ERROR] 检查 demo 状态失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
