#!/usr/bin/env python3
"""
数据库迁移脚本
更新数据库结构以支持新功能
"""
import sqlite3
import os

def migrate_database():
    db_path = os.path.join(os.path.dirname(__file__), 'mindmate.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 开始数据库迁移...")
    print("="*50)
    
    # 1. 为 UserProfiles 表添加 gender 字段
    try:
        cursor.execute("ALTER TABLE UserProfiles ADD COLUMN gender TEXT")
        print("✅ 添加 gender 字段到 UserProfiles 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  gender 字段已存在")
        else:
            print(f"❌ 添加 gender 字段失败: {e}")
    
    # 2. 为 UserProfiles 表添加 user_avatar_path 字段并迁移旧数据
    try:
        cursor.execute("ALTER TABLE UserProfiles ADD COLUMN user_avatar_path TEXT")
        print("✅ 添加 user_avatar_path 字段到 UserProfiles 表")
        
        # 迁移旧的 avatar_path 数据
        cursor.execute("UPDATE UserProfiles SET user_avatar_path = avatar_path WHERE avatar_path IS NOT NULL")
        print("✅ 迁移旧的头像数据")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  user_avatar_path 字段已存在")
        else:
            print(f"❌ 添加 user_avatar_path 字段失败: {e}")
    
    # 3. 为 ChatHistory 表添加 persona_id 字段
    try:
        cursor.execute("ALTER TABLE ChatHistory ADD COLUMN persona_id INTEGER NOT NULL DEFAULT 1")
        print("✅ 添加 persona_id 字段到 ChatHistory 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  persona_id 字段已存在")
        else:
            print(f"❌ 添加 persona_id 字段失败: {e}")
    
    conn.commit()
    conn.close()
    
    print("="*50)
    print("✅ 数据库迁移完成！")
    print("\n请重启应用以使更改生效。")

if __name__ == '__main__':
    migrate_database()
