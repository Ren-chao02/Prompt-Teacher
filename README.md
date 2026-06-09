# Prompt Teacher - 提示词教学平台

> 一个面向提示词工程学习的专业教学平台，提供交互式练习、AI自动评估和个性化学习路径。

## 🌟 功能特性

### 🎯 核心功能
- **提示词练习系统**：基于真实场景的提示词编写练习，支持多维度AI自动评分
- **自定义LLM模型**：支持配置OpenAI/Ollama/Qwen/DeepSeek等多种模型
- **学习资源中心**：系统化的提示词工程教程和最佳实践
- **教师工作台**：班级管理、学生进度追踪、批量导入导出

### 📊 数据分析
- 学习进度可视化
- 练习统计与趋势分析
- 学生表现评估报告

### 🔔 通知系统
- 实时通知推送
- 学习提醒与进度追踪
- WebSocket实时消息

## 🛠️ 技术栈

### 后端
- **框架**: Django 6.0 + Django REST Framework
- **认证**: JWT Token Authentication
- **数据库**: PostgreSQL / SQLite（开发环境）
- **API文档**: drf-spectacular (Swagger/OpenAPI)

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router

### LLM集成
- 支持 OpenAI 兼容接口
- 支持 Ollama 本地模型
- 支持 Qwen（通义千问）
- 支持 DeepSeek

## 📁 项目结构

```
Prompt Teacher/
├── admin-panel/          # Vue管理后台
│   ├── src/
│   │   ├── api/          # API请求封装
│   │   ├── components/   # 公共组件
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   └── views/        # 页面视图
│   └── package.json
├── core/                 # Django核心应用
│   ├── templates/        # 前台模板
│   └── views.py          # 前台视图
├── practice/             # 练习系统
│   ├── models.py         # 练习记录、场景、LLM配置模型
│   ├── services/         # LLM服务
│   └── api/              # 练习API
├── learning/             # 学习资源中心
│   ├── models.py         # 学习材料模型
│   └── api/              # 学习API
├── users/                # 用户管理
│   ├── models.py         # 用户、班级模型
│   └── api/              # 用户API
├── analytics/            # 数据分析
├── notifications/        # 通知系统
├── prompt_teaching/      # Django项目配置
└── scripts/              # 辅助脚本
```

## 🚀 快速开始

### 环境要求
- Python >= 3.11
- Node.js >= 20
- PostgreSQL >= 14（可选，开发可用SQLite）
- Ollama（本地LLM支持，可选）

### 1. 克隆项目

```bash
git clone <repository-url>
cd "Prompt Teacher"
```

### 2. 后端配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 配置数据库连接等信息

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8001
```

### 3. 前端配置

```bash
cd admin-panel

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

### 4. Ollama配置（可选）

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5:7b

# 启动 Ollama 服务
ollama serve
```

## 🌐 访问地址

| 服务 | 地址 |
|------|------|
| Django后台 | http://localhost:8001/admin/ |
| Django原生admin | http://localhost:8001/django-admin/ |
| API文档 | http://localhost:8001/api/docs/ |
| Vue开发服务器 | http://localhost:5173/admin/ |

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
# Django配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置（使用PostgreSQL时）
DB_NAME=prompt_teaching_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# LLM配置（默认使用Ollama）
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b
```

### 生产环境部署

1. 设置 `DEBUG=False`
2. 配置 `ALLOWED_HOSTS`
3. 配置数据库连接
4. 构建前端：`npm run build`
5. 配置静态文件服务

## 📡 API接口

### 主要端点

| 模块 | 端点 | 描述 |
|------|------|------|
| 用户 | `/api/v1/users/` | 用户管理 |
| 练习 | `/api/v1/practice/` | 练习场景、记录、LLM配置 |
| 学习 | `/api/v1/learning/` | 学习材料 |
| 分析 | `/api/v1/analytics/` | 数据分析 |
| 通知 | `/api/v1/notifications/` | 通知管理 |

### API文档

启动服务后访问：
- Swagger UI: http://localhost:8001/api/docs/
- ReDoc: http://localhost:8001/api/redoc/

## 🧪 测试

```bash
# 运行后端测试
python -m pytest tests/ -v

# 运行前端测试
cd admin-panel
npm run test
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题或建议，请通过以下方式联系：
- 邮箱：[your-email@example.com]
- 项目地址：[repository-url]