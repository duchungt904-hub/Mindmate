import sqlite3
from database.db_manager import Database
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, db: Database):
        self.db = db
    
    def create_user(self, email, username, password):
        """创建新用户"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO Users (email, username, hashed_password) VALUES (?, ?, ?)",
                (email, username, hashed_password)
            )
            user_id = cursor.lastrowid
            
            # 创建对应的用户资料记录
            cursor.execute(
                "INSERT INTO UserProfiles (user_id) VALUES (?)",
                (user_id,)
            )
            
            conn.commit()
            return {"success": True, "user_id": user_id}
        except sqlite3.IntegrityError as e:
            return {"success": False, "error": "用户名或邮箱已存在"}
        finally:
            conn.close()
    
    def verify_user(self, login_id, password):
        """验证用户登录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 查找用户（支持邮箱或用户名登录）
        cursor.execute(
            "SELECT * FROM Users WHERE email = ? OR username = ?",
            (login_id, login_id)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['hashed_password'], password):
            return {
                "success": True,
                "user_id": user['id'],
                "email": user['email'],
                "username": user['username']
            }
        return {"success": False, "error": "用户名或密码错误"}
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, username FROM Users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
