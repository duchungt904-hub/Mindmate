# MindMate 应用

基于 Python 和 Flask 的 AI 聊天伙伴应用，支持个性化 Avatar、情绪追踪等功能。

## 功能特性

- ✅ 用户认证（注册/登录）
- ✅ 个人资料管理
- ✅ 自定义 AI Avatar（外观和性格）
- ✅ GPT 驱动的智能聊天
- ✅ 日历心情追踪（手动和自动）
- ✅ 响应式移动端界面

## 技术栈

- **后端**: Python, Flask
- **数据库**: SQLite
- **AI**: OpenAI GPT API
- **前端**: HTML, CSS, JavaScript

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_PATH=mindmate.db
```

### 3. 初始化数据库

```bash
python database/db_manager.py
```

### 4. 运行应用

```bash
python app.py
```

应用将在 http://localhost:5000 启动。

## 使用说明

1. **注册账号**: 访问 `/register` 创建新账号
2. **完善资料**: 在 `/profile` 填写个人信息
3. **配置 Avatar**: 在 `/avatar` 选择外观和性格
4. **开始聊天**: 在 `/chat` 与 AI 伙伴对话
5. **追踪心情**: 在 `/calendar` 查看和记录心情

## 项目结构

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

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/check` - 检查登录状态

### 个人资料
- `GET /api/profile/` - 获取用户资料
- `POST /api/profile/` - 更新用户资料

### Avatar
- `GET /api/avatar/personas` - 获取所有 Persona
- `GET /api/avatar/` - 获取用户 Avatar 配置
- `POST /api/avatar/` - 保存 Avatar 配置

### 聊天
- `GET /api/chat/history` - 获取聊天历史
- `POST /api/chat/send` - 发送消息

### 心情
- `POST /api/mood/set` - 手动设置心情
- `POST /api/mood/auto-analyze` - 自动分析心情
- `GET /api/mood/get` - 获取某天的心情
- `GET /api/mood/month` - 获取某月的心情

## 注意事项

- 需要有效的 OpenAI API Key
- 建议在生产环境中更改 SECRET_KEY
- 上传的文件存储在 `static/uploads/` 目录

## License

MIT
