from database.db_manager import Database
from datetime import datetime

class Mood:
    def __init__(self, db: Database):
        self.db = db
    
    def set_mood(self, user_id, date, mood_emoji, source='manual'):
        """设置某天的心情"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 使用 REPLACE 来更新或插入
        cursor.execute(
            """INSERT OR REPLACE INTO MoodCalendar 
               (user_id, date, mood_emoji, source) 
               VALUES (?, ?, ?, ?)""",
            (user_id, date, mood_emoji, source)
        )
        
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def get_mood(self, user_id, date):
        """获取某天的心情"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM MoodCalendar WHERE user_id = ? AND date = ?",
            (user_id, date)
        )
        
        mood = cursor.fetchone()
        conn.close()
        
        if mood:
            return dict(mood)
        return None
    
    def get_month_moods(self, user_id, year, month):
        """获取某个月的所有心情记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 格式化月份为 YYYY-MM
        date_prefix = f"{year}-{month:02d}"
        
        cursor.execute(
            """SELECT * FROM MoodCalendar 
               WHERE user_id = ? 
               AND date LIKE ? 
               ORDER BY date""",
            (user_id, f"{date_prefix}%")
        )
        
        moods = cursor.fetchall()
        conn.close()
        
        return [dict(m) for m in moods]
