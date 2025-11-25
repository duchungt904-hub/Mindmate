# MindMate 🧠💬

An AI-powered mental wellness companion built with Python and Flask. Features personalized AI avatars, mood tracking, and intelligent conversations.

---

## 🚀 **Try the Live Demo**

### **👉 [Launch Demo Now](https://mindmate-6a4h.onrender.com/demo) 👈**

**Demo Credentials:**
- Username: `test`
- Password: `test`

*Note: Demo data is automatically cleared on each login.*

---

## ✨ Features

- ✅ User Authentication (Register/Login)
- ✅ Personal Profile Management
- ✅ Customizable AI Avatars (Appearance & Personality)
- ✅ GPT-Powered Intelligent Chat
- ✅ Calendar-Based Mood Tracking (Manual & Auto)
- ✅ Responsive Mobile Interface

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **AI**: OpenAI GPT API (DeepSeek compatible)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Or DeepSeek API URL
SECRET_KEY=your_secret_key_here
DATABASE_PATH=mindmate.db
```

### 3. Initialize Database

```bash
python database/db_manager.py
```

### 4. Run the Application

```bash
python app.py
```

The app will start at http://localhost:5000

## 📖 How to Use

1. **Register Account**: Visit `/register` to create a new account
2. **Complete Profile**: Fill in personal information at `/profile`
3. **Configure Avatar**: Choose appearance and personality at `/avatar`
4. **Start Chatting**: Talk with your AI companion at `/chat`
5. **Track Mood**: View and record your mood at `/calendar`

## 📁 Project Structure

```
Mindmate_Qoder2/
├── app.py                  # Flask 主应用
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
├── database/              # 数据库模块
│   ├── db_manager.py      # 数据库管理
│   └── __init__.py
├── models/                # 数据模型
│   ├── user.py           # 用户模型
│   ├── profile.py        # 资料模型
│   ├── avatar.py         # Avatar 模型
│   ├── chat.py           # 聊天模型
│   ├── mood.py           # 心情模型
│   └── __init__.py
├── routes/               # API 路由
│   ├── auth.py          # 认证路由
│   ├── profile.py       # 资料路由
│   ├── avatar.py        # Avatar 路由
│   ├── chat.py          # 聊天路由
│   ├── mood.py          # 心情路由
│   └── __init__.py
├── utils/               # 工具模块
│   ├── gpt_service.py  # GPT API 服务
│   ├── file_handler.py # 文件处理
│   └── __init__.py
├── templates/           # HTML 模板
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── profile.html
│   ├── avatar.html
│   ├── chat.html
│   └── calendar.html
└── static/              # 静态资源
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── uploads/         # 用户上传文件
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check login status

### Profile
- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Update user profile

### Avatar
- `GET /api/avatar/personas` - Get all personalities
- `GET /api/avatar/` - Get user avatar configuration
- `POST /api/avatar/` - Save avatar configuration
- `GET /api/avatar/list` - List user's avatars

### Chat
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/send` - Send message

### Mood
- `POST /api/mood/set` - Manually set mood
- `POST /api/mood/auto-analyze` - Auto-analyze mood from chat
- `GET /api/mood/get` - Get mood for a specific day
- `GET /api/mood/month` - Get mood calendar for a month

### Demo
- `POST /api/demo/clear` - Clear demo account data
- `GET /api/demo/status` - Check demo account status

## ⚠️ Important Notes

- Requires a valid OpenAI API Key or DeepSeek API Key
- Change `SECRET_KEY` in production environment
- Uploaded files are stored in `static/uploads/` directory
- Future dates are disabled in mood calendar (only today and past dates)
- AI responds primarily in English for better practice

## 🌐 Live Deployment

**Production URL**: https://mindmate-6a4h.onrender.com

**Demo URL**: https://mindmate-6a4h.onrender.com/demo

## 📝 License

MIT
