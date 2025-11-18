from database.db_manager import Database

class UserProfile:
    def __init__(self, db: Database):
        self.db = db
    
    def get_profile(self, user_id):
        """获取用户资料"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM UserProfiles WHERE user_id = ?",
            (user_id,)
        )
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            return dict(profile)
        return None
    
    def update_profile(self, user_id, name=None, gender=None, user_avatar_path=None, 
                      date_birth=None, goal=None, self_description=None):
        """更新用户资料"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if gender is not None:
            updates.append("gender = ?")
            values.append(gender)
        if user_avatar_path is not None:
            updates.append("user_avatar_path = ?")
            values.append(user_avatar_path)
        if date_birth is not None:
            updates.append("date_birth = ?")
            values.append(date_birth)
        if goal is not None:
            updates.append("goal = ?")
            values.append(goal)
        if self_description is not None:
            updates.append("self_description = ?")
            values.append(self_description)
        
        if not updates:
            return {"success": False, "error": "没有要更新的字段"}
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE UserProfiles SET {', '.join(updates)} WHERE user_id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {"success": True}
