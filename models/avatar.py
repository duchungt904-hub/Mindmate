from database.db_manager import Database

class Avatar:
    def __init__(self, db: Database):
        self.db = db
    
    def get_personas(self):
        """获取所有预设的 Persona"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Personas")
        personas = cursor.fetchall()
        conn.close()
        
        return [dict(p) for p in personas]
    
    def get_all_avatars(self, user_id):
        """获取用户的所有 Avatar"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT a.*, p.name as persona_name, p.system_prompt, p.description 
               FROM Avatars a 
               LEFT JOIN Personas p ON a.persona_id = p.id 
               WHERE a.user_id = ?
               ORDER BY a.created_at DESC""",
            (user_id,)
        )
        avatars = cursor.fetchall()
        conn.close()
        
        return [dict(a) for a in avatars]
    
    def get_avatar_by_id(self, avatar_id, user_id=None):
        """根据 ID 获取 Avatar（可选验证 user_id）"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                """SELECT a.*, p.name as persona_name, p.system_prompt, p.description 
                   FROM Avatars a 
                   LEFT JOIN Personas p ON a.persona_id = p.id 
                   WHERE a.id = ? AND a.user_id = ?""",
                (avatar_id, user_id)
            )
        else:
            cursor.execute(
                """SELECT a.*, p.name as persona_name, p.system_prompt, p.description 
                   FROM Avatars a 
                   LEFT JOIN Personas p ON a.persona_id = p.id 
                   WHERE a.id = ?""",
                (avatar_id,)
            )
        
        avatar = cursor.fetchone()
        conn.close()
        
        if avatar:
            return dict(avatar)
        return None
    
    def get_avatar(self, user_id):
        """获取用户的默认 Avatar（兼容旧 API）"""
        avatars = self.get_all_avatars(user_id)
        return avatars[0] if avatars else None
    
    def create_avatar(self, user_id, avatar_name, appearance_type, 
                     custom_image_path, persona_id, custom_persona=None):
        """创建新的 Avatar"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO Avatars 
               (user_id, avatar_name, appearance_type, custom_image_path, persona_id, custom_persona) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, avatar_name, appearance_type, custom_image_path, persona_id, custom_persona)
        )
        
        avatar_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"success": True, "avatar_id": avatar_id}
    
    def update_avatar(self, avatar_id, user_id, avatar_name=None, appearance_type=None,
                     custom_image_path=None, persona_id=None, custom_persona=None):
        """更新 Avatar"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 验证 Avatar 属于该用户
        cursor.execute("SELECT id FROM Avatars WHERE id = ? AND user_id = ?", (avatar_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return {"success": False, "error": "Avatar 不存在或无权限"}
        
        # 构建更新语句
        updates = []
        params = []
        
        if avatar_name is not None:
            updates.append("avatar_name = ?")
            params.append(avatar_name)
        if appearance_type is not None:
            updates.append("appearance_type = ?")
            params.append(appearance_type)
        if custom_image_path is not None:
            updates.append("custom_image_path = ?")
            params.append(custom_image_path)
        if persona_id is not None:
            updates.append("persona_id = ?")
            params.append(persona_id)
        if custom_persona is not None:
            updates.append("custom_persona = ?")
            params.append(custom_persona)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([avatar_id, user_id])
            
            sql = f"UPDATE Avatars SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            cursor.execute(sql, params)
            conn.commit()
        
        conn.close()
        return {"success": True}
    
    def delete_avatar(self, avatar_id, user_id):
        """删除 Avatar"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 验证 Avatar 属于该用户
        cursor.execute("SELECT id FROM Avatars WHERE id = ? AND user_id = ?", (avatar_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return {"success": False, "error": "Avatar 不存在或无权限"}
        
        # 删除 Avatar
        cursor.execute("DELETE FROM Avatars WHERE id = ? AND user_id = ?", (avatar_id, user_id))
        
        # 删除相关的聊天记录
        cursor.execute("DELETE FROM ChatHistory WHERE avatar_id = ? AND user_id = ?", (avatar_id, user_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def create_or_update_avatar(self, user_id, appearance_type, 
                                custom_image_path, persona_id, custom_persona=None):
        """创建或更新用户的 Avatar（兼容旧 API）"""
        avatars = self.get_all_avatars(user_id)
        
        if avatars:
            # 更新第一个 Avatar
            return self.update_avatar(
                avatars[0]['id'], 
                user_id,
                appearance_type=appearance_type,
                custom_image_path=custom_image_path,
                persona_id=persona_id,
                custom_persona=custom_persona
            )
        else:
            # 创建新 Avatar
            from models import Avatar as AvatarModel
            persona = None
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM Personas WHERE id = ?", (persona_id,))
            result = cursor.fetchone()
            if result:
                persona = dict(result)
            conn.close()
            
            avatar_name = persona['name'] if persona else "My Avatar"
            return self.create_avatar(
                user_id,
                avatar_name,
                appearance_type,
                custom_image_path,
                persona_id,
                custom_persona
            )
