import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPTService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        
        print(f"[DEBUG] OPENAI_API_KEY 已加载: {api_key[:10]}..." if api_key else "[ERROR] OPENAI_API_KEY 未找到")
        
        if not api_key or api_key == 'your_openai_api_key_here' or 'DEMO' in api_key:
            print("警告：未配置有效的 OPENAI_API_KEY，请在 .env 文件中配置")
        
        # 创建 OpenAI 客户端，支持自定义 base_url
        base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        print(f"[DEBUG] OPENAI_BASE_URL: {base_url}")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 根据 base_url 自动选择模型
        if 'deepseek' in base_url.lower():
            self.model = "deepseek-chat"  # DeepSeek 模型
            print(f"[INFO] 使用 DeepSeek 模型: {self.model}")
        else:
            self.model = "gpt-3.5-turbo"  # OpenAI 模型
            print(f"[INFO] 使用 OpenAI 模型: {self.model}")
    
    def generate_response(self, user_message, chat_history, system_prompt, user_profile=None):
        """
        生成 AI 回复
        
        Args:
            user_message: 用户当前的消息
            chat_history: 聊天历史记录列表
            system_prompt: Avatar 的系统提示（Persona）
            user_profile: 用户资料（可选，用于个性化）
        """
        # 构建增强的系统提示 - 先强调核心原则，再加入性格设定
        core_principles = """CORE PRINCIPLES (MOST IMPORTANT):
1. Be authentic and sincere - speak from the heart, not from a script
2. Address the user's actual question directly - get to the point quickly
3. Keep responses concise and focused - avoid unnecessary elaboration
4. Listen to what the user really needs, not just what they say
5. Use simple, natural language - be conversational, not formal
6. Your personality should influence HOW you speak, not WHETHER you help effectively

Remember: Your primary goal is to genuinely help and connect with the user. Personality is secondary to being helpful and sincere.

---

"""
        
        # 将核心原则放在最前面，然后是 Persona 设定
        enhanced_prompt = core_principles + system_prompt
        
        if user_profile:
            profile_info = []
            if user_profile.get('name'):
                profile_info.append(f"用户的名字是 {user_profile['name']}")
            if user_profile.get('gender'):
                gender_text = {'male': '男性', 'female': '女性'}.get(user_profile['gender'], '')
                if gender_text:
                    profile_info.append(f"用户是{gender_text}")
            if user_profile.get('goal'):
                profile_info.append(f"用户的座右铭是：{user_profile['goal']}")
            if user_profile.get('date_birth'):
                profile_info.append(f"用户的生日是 {user_profile['date_birth']}")
            if user_profile.get('self_description'):
                profile_info.append(f"用户这样描述自己：{user_profile['self_description']}")
            
            if profile_info:
                enhanced_prompt += "\n\n用户信息：\n" + "\n".join(profile_info)
                enhanced_prompt += "\n\n请在对话中适当地参考这些信息，让对话更加个性化和贴心。"
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": enhanced_prompt}
        ]
        
        # 添加历史消息（限制数量以避免超出 token 限制）
        max_history = 10
        recent_history = chat_history[-max_history:] if len(chat_history) > max_history else chat_history
        
        for msg in recent_history:
            role = "user" if msg['sender'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['message']})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # 降低温度使回答更集中、更稳定
                max_tokens=300  # 减少 token 使回答更简洁
            )
            
            return {
                "success": True,
                "message": response.choices[0].message.content
            }
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] GPT API 调用失败: {error_msg}")
            print(f"[DEBUG] 完整错误信息: {repr(e)}")
            
            # 提供更友好的错误提示
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
                user_msg = f"API 密钥无效，请检查配置\n错误详情: {error_msg}"
            elif "rate_limit" in error_msg.lower():
                user_msg = "API 调用次数限制，请稍后再试"
            elif "model" in error_msg.lower():
                user_msg = f"模型 {self.model} 不可用，请检查配置"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                user_msg = "网络连接失败，请检查网络或稍后重试"
            else:
                user_msg = f"抱歉，我现在无法回复。\n错误: {error_msg}"
            
            return {
                "success": False,
                "error": user_msg,
                "message": user_msg  # 添加 message 字段用于直接显示
            }
    
    def analyze_mood_from_text(self, text):
        """
        从文本中分析心情
        返回一个 emoji 表情
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个情绪分析助手。根据用户的文本内容，判断用户的整体心情，并返回一个最合适的 emoji 表情。只返回一个 emoji，不要返回其他内容。可选的 emoji：😊（开心）、😢（难过）、😌（平静）、😤（生气）、😰（焦虑）、🤔（思考）、😴（疲惫）、🥳（兴奋）"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            emoji = response.choices[0].message.content.strip()
            return emoji
        except Exception as e:
            print(f"心情分析失败: {str(e)}")
            return "😊"  # 默认返回开心
