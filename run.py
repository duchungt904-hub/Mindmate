#!/usr/bin/env python3
"""
MindMate 应用启动脚本
"""
import os
import sys

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import openai
        from dotenv import load_dotenv
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("\n请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    if not os.path.exists('.env'):
        print("✗ .env 文件不存在")
        print("\n请复制 .env.example 为 .env 并配置：")
        print("  cp .env.example .env")
        print("\n然后编辑 .env 文件，填入你的 OpenAI API Key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("✗ 未配置 OPENAI_API_KEY")
        print("\n请在 .env 文件中设置有效的 OpenAI API Key")
        return False
    
    print("✓ 环境变量配置正确")
    return True

def init_database():
    """初始化数据库"""
    try:
        from database import Database
        db = Database()
        print("✓ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("MindMate 应用启动检查")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境变量
    if not check_env_file():
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("所有检查通过！正在启动应用...")
    print("=" * 50 + "\n")
    
    # 启动应用
    from app import app
    
    # 确保上传目录存在
    os.makedirs('static/uploads/avatars', exist_ok=True)
    os.makedirs('static/uploads/avatar_images', exist_ok=True)
    
    print("\n应用已启动！")
    print("访问地址: http://localhost:5001")
    print("按 Ctrl+C 停止应用\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )

if __name__ == '__main__':
    main()
