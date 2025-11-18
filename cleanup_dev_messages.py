#!/usr/bin/env python3
"""
清理数据库中包含开发模式标记的旧聊天记录
"""
import sqlite3
import os

def cleanup_dev_messages():
    db_path = os.path.join(os.path.dirname(__file__), 'mindmate.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找包含开发模式标记的消息
    dev_keywords = [
        '⚠️ [开发模式]',
        '[开发模式]',
        '模拟回复',
        'DEV_MODE'
    ]
    
    total_deleted = 0
    
    for keyword in dev_keywords:
        cursor.execute(
            "SELECT id, sender, message FROM ChatHistory WHERE message LIKE ?",
            (f'%{keyword}%',)
        )
        
        messages = cursor.fetchall()
        
        if messages:
            print(f"\n找到 {len(messages)} 条包含 '{keyword}' 的消息：")
            
            for msg_id, sender, message in messages:
                # 截取消息预览
                preview = message[:50] + '...' if len(message) > 50 else message
                print(f"  - ID {msg_id} ({sender}): {preview}")
            
            # 删除这些消息
            cursor.execute(
                "DELETE FROM ChatHistory WHERE message LIKE ?",
                (f'%{keyword}%',)
            )
            
            deleted = cursor.rowcount
            total_deleted += deleted
            print(f"  ✅ 已删除 {deleted} 条消息")
    
    conn.commit()
    
    # 显示清理后的统计
    cursor.execute("SELECT COUNT(*) FROM ChatHistory")
    remaining = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n" + "="*50)
    print(f"✅ 清理完成！")
    print(f"📊 删除了 {total_deleted} 条包含开发模式标记的消息")
    print(f"📝 剩余 {remaining} 条正常消息")
    print("="*50)

if __name__ == '__main__':
    print("🧹 开始清理数据库中的开发模式消息...")
    print("="*50)
    cleanup_dev_messages()
    print("\n重启应用后刷新聊天页面即可看到干净的聊天记录。")
