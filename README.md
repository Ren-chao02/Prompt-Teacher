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
- Docker & Docker Compose（生产环境推荐）
- Ollama（本地LLM支持，可选）

---

## 🐳 一键部署（推荐）

### 方式一：Docker 一键部署（生产环境推荐）

**最简单的部署方式，适合生产环境！**

#### 1. 克隆项目

```bash
git clone <repository-url>
cd "Prompt Teacher"
```

#### 2. 一键初始化

```bash
chmod +x deploy.sh
./deploy.sh init
```

#### 3. 配置环境变量

编辑 `.env` 文件，修改以下配置：

```env
# 必须修改的配置
SECRET_KEY=your-random-secret-key-here
DB_PASSWORD=your-secure-password

# LLM 配置（选择其一）
# 选项 1: Ollama 本地模型
LLM_API_URL=http://ollama:11434/v1/chat/completions
LLM_MODEL=qwen2.5:7b

# 选项 2: OpenAI
# LLM_API_URL=https://api.openai.com/v1/chat/completions
# LLM_API_KEY=sk-your-api-key
# LLM_MODEL=gpt-4

# 选项 3: DeepSeek
# LLM_API_URL=https://api.deepseek.com/v1/chat/completions
# LLM_API_KEY=your-api-key
# LLM_MODEL=deepseek-chat
```

#### 4. 启动服务

```bash
./deploy.sh start
```

#### 5. 创建管理员账号

```bash
./deploy.sh superuser
```

**🎉 部署完成！访问 http://localhost 即可使用！**

---

### 部署脚本命令

```bash
./deploy.sh init        # 初始化部署环境
./deploy.sh start       # 启动所有服务
./deploy.sh stop        # 停止所有服务
./deploy.sh restart     # 重启所有服务
./deploy.sh status      # 查看服务状态
./deploy.sh logs        # 查看日志
./deploy.sh backup      # 备份数据
./deploy.sh restore <dir>  # 恢复数据
./deploy.sh superuser   # 创建超级用户
./deploy.sh shell       # 进入容器
./deploy.sh update      # 更新服务
```

---

### 方式二：手动部署（开发环境）

#### 1. 克隆项目

```bash
git clone <repository-url>
cd "Prompt Teacher"
```

#### 2. 后端配置

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

#### 3. 前端配置

```bash
cd admin-panel

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

#### 4. Ollama配置（可选）

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

---

## 🏭 生产环境部署

### 安全建议

1. **修改默认密码**：修改 `.env` 中的所有默认密码
2. **使用强密码**：至少 16 位，包含大小写字母、数字和特殊字符
3. **配置防火墙**：只开放必要端口（80, 443）
4. **启用 HTTPS**：使用 Let's Encrypt 配置 SSL 证书

### SSL/HTTPS 配置

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 性能优化

1. **调整 Worker 数量**：根据 CPU 核心数调整 Gunicorn workers
2. **启用缓存**：配置 Redis 缓存（可选）
3. **CDN 加速**：使用 CDN 加速静态资源
4. **数据库优化**：配置连接池和索引

### 监控与备份

```bash
# 每天自动备份
crontab -e

# 添加以下行（每天凌晨 2 点备份）
0 2 * * * cd /path/to/prompt-teacher && ./deploy.sh backup >> /var/log/backup.log 2>&1
```

### 高可用部署

- 使用 **Docker Swarm** 或 **Kubernetes** 进行容器编排
- 配置 **数据库主从复制**
- 使用 **负载均衡器**（Nginx、HAProxy）

---

## ❓ 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
netstat -tlnp | grep -E '80|5432|8001'

# 修改 docker-compose.yml 中的端口映射
```

### 2. 数据库连接失败

```bash
# 检查数据库容器状态
docker ps | grep prompt-teacher-db

# 查看数据库日志
./deploy.sh logs db
```

### 3. 前端无法访问后端 API

- 检查 Nginx 配置：[deploy/nginx.conf](deploy/nginx.conf)
- 检查后端服务状态：`./deploy.sh status`
- 查看后端日志：`./deploy.sh logs backend`

### 4. LLM 模型无法连接

- **Ollama**：确保 Ollama 容器已启动，`./deploy.sh start` 时添加 `--profile ollama`
- **OpenAI/DeepSeek**：检查 API Key 是否正确，网络是否可访问

### 5. 数据迁移问题

```bash
# 进入后端容器
./deploy.sh shell backend

# 手动执行迁移
python manage.py migrate

# 检查迁移状态
python manage.py showmigrations
```

---

## 📚 更多文档

- [部署详细指南](deploy/README.md)
- [API 文档](http://localhost/api/docs/)
- [项目技术方案](提示词教学网站%20—%20技术方案与项目规划%20🚀.md)