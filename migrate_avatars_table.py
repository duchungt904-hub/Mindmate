#!/usr/bin/env python3
"""
迁移 Avatars 表以支持多个 Avatar
"""
import sqlite3
import os

def migrate_avatars_table(db_path='mindmate.db'):
    """更新 Avatars 表结构以支持多个 Avatar"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 检查是否已经有 avatar_name 列
        cursor.execute("PRAGMA table_info(Avatars)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'avatar_name' in columns:
            print("✅ Avatars 表已经是最新版本")
            return
        
        print("开始迁移 Avatars 表...")
        
        # 2. 创建新的 Avatars 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Avatars_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                avatar_name TEXT NOT NULL,
                appearance_type TEXT NOT NULL,
                custom_image_path TEXT,
                persona_id INTEGER NOT NULL,
                custom_persona TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (persona_id) REFERENCES Personas(id)
            )
        ''')
        
        # 3. 迁移旧数据（如果存在）
        cursor.execute("SELECT COUNT(*) FROM Avatars")
        old_count = cursor.fetchone()[0]
        
        if old_count > 0:
            print(f"发现 {old_count} 条旧 Avatar 数据，正在迁移...")
            
            # 获取旧数据
            cursor.execute('''
                SELECT a.*, p.name as persona_name 
                FROM Avatars a 
                LEFT JOIN Personas p ON a.persona_id = p.id
            ''')
            old_avatars = cursor.fetchall()
            
            # 插入到新表
            for avatar in old_avatars:
                user_id = avatar[1]
                appearance_type = avatar[2]
                custom_image_path = avatar[3]
                persona_id = avatar[4]
                custom_persona = avatar[5]
                persona_name = avatar[7] if len(avatar) > 7 else "My Avatar"
                
                cursor.execute('''
                    INSERT INTO Avatars_new 
                    (user_id, avatar_name, appearance_type, custom_image_path, persona_id, custom_persona)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, persona_name, appearance_type, custom_image_path, persona_id, custom_persona))
            
            print(f"✅ 已迁移 {old_count} 条数据")
        
        # 4. 删除旧表，重命名新表
        cursor.execute("DROP TABLE Avatars")
        cursor.execute("ALTER TABLE Avatars_new RENAME TO Avatars")
        
        # 5. 更新 ChatHistory 表，添加 avatar_id 列
        cursor.execute("PRAGMA table_info(ChatHistory)")
        chat_columns = [col[1] for col in cursor.fetchall()]
        
        if 'avatar_id' not in chat_columns:
            print("更新 ChatHistory 表...")
            
            # 创建新的 ChatHistory 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ChatHistory_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    avatar_id INTEGER,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (avatar_id) REFERENCES Avatars(id)
                )
            ''')
            
            # 迁移旧聊天记录
            cursor.execute("SELECT * FROM ChatHistory")
            old_chats = cursor.fetchall()
            
            if old_chats:
                print(f"迁移 {len(old_chats)} 条聊天记录...")
                
                for chat in old_chats:
                    chat_id = chat[0]
                    user_id = chat[1]
                    sender = chat[3]
                    message = chat[4]
                    timestamp = chat[5]
                    
                    # 获取用户的第一个 Avatar
                    cursor.execute("SELECT id FROM Avatars WHERE user_id = ? LIMIT 1", (user_id,))
                    avatar_result = cursor.fetchone()
                    avatar_id = avatar_result[0] if avatar_result else None
                    
                    cursor.execute('''
                        INSERT INTO ChatHistory_new 
                        (user_id, avatar_id, sender, message, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, avatar_id, sender, message, timestamp))
            
            # 删除旧表，重命名新表
            cursor.execute("DROP TABLE ChatHistory")
            cursor.execute("ALTER TABLE ChatHistory_new RENAME TO ChatHistory")
            
            print("✅ ChatHistory 表已更新")
        
        conn.commit()
        print("✅ 数据库迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    # 检查数据库文件
    db_path = 'mindmate.db'
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行 python database/db_manager.py 初始化数据库")
    else:
        migrate_avatars_table(db_path)
