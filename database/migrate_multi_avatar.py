"""
数据库迁移脚本：支持多 Avatar 功能
- 移除 Avatars 表的 user_id UNIQUE 约束
- 添加 avatar_name 字段用于区分不同的 Avatar
- 将 ChatHistory 的 persona_id 改为 avatar_id
"""

import sqlite3
import os

def migrate_database(db_path='mindmate.db'):
    """执行数据库迁移"""
    
    print("开始数据库迁移...")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. 备份现有的 Avatars 数据
        print("步骤 1: 备份现有 Avatars 数据...")
        cursor.execute("SELECT * FROM Avatars")
        old_avatars = cursor.fetchall()
        
        # 2. 备份现有的 ChatHistory 数据
        print("步骤 2: 备份现有 ChatHistory 数据...")
        cursor.execute("SELECT * FROM ChatHistory")
        old_chat_history = cursor.fetchall()
        
        # 3. 删除旧的 Avatars 表
        print("步骤 3: 删除旧的 Avatars 表...")
        cursor.execute("DROP TABLE IF EXISTS Avatars")
        
        # 4. 创建新的 Avatars 表（支持多个 Avatar）
        print("步骤 4: 创建新的 Avatars 表...")
        cursor.execute('''
            CREATE TABLE Avatars (
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
        
        # 5. 恢复数据（添加默认名称）
        print("步骤 5: 恢复 Avatars 数据（添加默认名称）...")
        for avatar in old_avatars:
            # 获取 Persona 名称作为 Avatar 名称
            cursor.execute("SELECT name FROM Personas WHERE id = ?", (avatar['persona_id'],))
            persona = cursor.fetchone()
            avatar_name = persona['name'] if persona else "My Avatar"
            
            cursor.execute('''
                INSERT INTO Avatars (id, user_id, avatar_name, appearance_type, custom_image_path, persona_id, custom_persona, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                avatar['id'],
                avatar['user_id'],
                avatar_name,
                avatar['appearance_type'],
                avatar['custom_image_path'],
                avatar['persona_id'],
                avatar['custom_persona'],
                avatar['updated_at']
            ))
        
        # 6. 删除旧的 ChatHistory 表
        print("步骤 6: 删除旧的 ChatHistory 表...")
        cursor.execute("DROP TABLE IF EXISTS ChatHistory")
        
        # 7. 创建新的 ChatHistory 表（使用 avatar_id）
        print("步骤 7: 创建新的 ChatHistory 表...")
        cursor.execute('''
            CREATE TABLE ChatHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                avatar_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (avatar_id) REFERENCES Avatars(id)
            )
        ''')
        
        # 8. 恢复聊天历史数据（将 persona_id 映射到 avatar_id）
        print("步骤 8: 恢复 ChatHistory 数据...")
        for msg in old_chat_history:
            # 查找对应的 avatar_id
            persona_id = msg['persona_id'] if 'persona_id' in msg.keys() else 1
            cursor.execute(
                "SELECT id FROM Avatars WHERE user_id = ? AND persona_id = ? LIMIT 1",
                (msg['user_id'], persona_id)
            )
            avatar = cursor.fetchone()
            avatar_id = avatar['id'] if avatar else 1
            
            cursor.execute('''
                INSERT INTO ChatHistory (id, user_id, avatar_id, sender, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                msg['id'],
                msg['user_id'],
                avatar_id,
                msg['sender'],
                msg['message'],
                msg['timestamp']
            ))
        
        # 提交事务
        conn.commit()
        print("✅ 数据库迁移成功！")
        
        # 显示统计信息
        cursor.execute("SELECT COUNT(*) as count FROM Avatars")
        avatar_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM ChatHistory")
        chat_count = cursor.fetchone()['count']
        
        print(f"📊 迁移统计:")
        print(f"  - Avatars: {len(old_avatars)} → {avatar_count}")
        print(f"  - ChatHistory: {len(old_chat_history)} → {chat_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # 检查数据库文件是否存在
    db_path = 'mindmate.db'
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        exit(1)
    
    # 执行迁移
    migrate_database(db_path)
