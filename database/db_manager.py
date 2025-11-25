import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

class Database:
    def __init__(self, db_path='mindmate.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        return conn
    
    def init_db(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # UserProfiles 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT,
                gender TEXT,
                user_avatar_path TEXT,
                date_birth TEXT,
                goal TEXT,
                self_description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        ''')
        
        # Personas 表（预设的 Avatar 内核）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                system_prompt TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # Avatars 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Avatars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                appearance_type TEXT NOT NULL,
                custom_image_path TEXT,
                persona_id INTEGER NOT NULL,
                custom_persona TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (persona_id) REFERENCES Personas(id)
            )
        ''')
        
        # ChatHistory 表（增加 persona_id 字段用于多个聊天对象）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ChatHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                persona_id INTEGER NOT NULL DEFAULT 1,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (persona_id) REFERENCES Personas(id)
            )
        ''')
        
        # MoodCalendar 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MoodCalendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                mood_emoji TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date),
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        ''')
        
        # 插入预设的 Personas
        self._insert_default_personas(cursor)
        
        conn.commit()
        conn.close()
        
        print("数据库初始化完成！")
    
    def _insert_default_personas(self, cursor):
        """插入预设的 Persona"""
        personas = [
            (
                "Serene Soul",
                "You are a calm, peaceful, and gentle companion. You speak in a soothing manner, offering wisdom and tranquility. You help users find inner peace and balance in their lives.",
                "Calm, gentle, and wise companion"
            ),
            (
                "Happy Mind",
                "You are an optimistic, cheerful, and energetic companion. You spread joy and positivity, always finding the bright side of every situation. You encourage users to embrace happiness.",
                "Optimistic, cheerful, energetic companion"
            ),
            (
                "Joyful Vision",
                "You are an enthusiastic, creative, and inspiring companion. You help users see the beauty in life and find creative solutions to their challenges. You celebrate every small victory.",
                "Enthusiastic, creative, inspiring companion"
            ),
            (
                "Dream Chaser",
                "You are an ambitious, motivating, and supportive companion. You push users to pursue their dreams and achieve their goals. You believe in their potential and help them overcome obstacles.",
                "Ambitious, motivating, supportive companion"
            ),
            (
                "User-defined",
                "You are a customizable companion. Your personality and speaking style are defined by the user's preferences.",
                "User-defined companion"
            )
        ]
        
        for name, prompt, desc in personas:
            cursor.execute(
                "INSERT OR IGNORE INTO Personas (name, system_prompt, description) VALUES (?, ?, ?)",
                (name, prompt, desc)
            )

if __name__ == "__main__":
    # 初始化数据库
    db = Database()
