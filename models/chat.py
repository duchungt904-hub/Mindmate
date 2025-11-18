from database.db_manager import Database
from datetime import datetime

class Chat:
    def __init__(self, db: Database):
        self.db = db
    
    def save_message(self, user_id, avatar_id, sender, message):
        """保存聊天消息"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO ChatHistory (user_id, avatar_id, sender, message) VALUES (?, ?, ?, ?)",
            (user_id, avatar_id, sender, message)
        )
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return {"success": True, "message_id": message_id}
    
    def get_chat_history(self, user_id, avatar_id=None, limit=50):
        """获取聊天历史（可按 avatar_id 过滤）"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if avatar_id:
            cursor.execute(
                """SELECT * FROM ChatHistory 
                   WHERE user_id = ? AND avatar_id = ?
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, avatar_id, limit)
            )
        else:
            cursor.execute(
                """SELECT * FROM ChatHistory 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
        
        messages = cursor.fetchall()
        conn.close()
        
        # 反转顺序，使最新的消息在最后
        return [dict(m) for m in reversed(messages)]
    
    def get_recent_messages_for_mood(self, user_id, date):
        """获取特定日期的聊天消息，用于分析心情"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT message FROM ChatHistory 
               WHERE user_id = ? 
               AND date(timestamp) = date(?) 
               AND sender = 'user'
               ORDER BY timestamp""",
            (user_id, date)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        return [m['message'] for m in messages]
