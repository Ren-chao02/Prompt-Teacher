# 自定义LLM模型评估系统 - 设计文档

> 日期: 2026-06-07
> 状态: 待审核
> 范围: Phase 1 - 模型配置 + 提示词评估（对话功能后续迭代）

## 1. 目标

让每位用户可以配置自己的外部LLM模型，用于：
- **提示词评估**：选择不同模型对学生的提示词进行评分和分析
- **AI对话**（Phase 2）：使用自定义模型进行交互式教学

## 2. 数据模型

### LLMConfig 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| owner | FK(UserProfile) | 所属用户 |
| name | VARCHAR(100) | 显示名称，如"GPT-4o"、"DeepSeek" |
| provider | VARCHAR(50) | 提供商标识：openai / ollama / qwen / deepseek / custom |
| api_url | VARCHAR(500) | API完整地址 |
| api_key | VARCHAR(500) | API密钥（加密存储） |
| model_id | VARCHAR(100) | 模型标识符，如"gpt-4o"、"qwen-plus" |
| is_default | Boolean | 是否为用户的默认评估模型 |
| is_active | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**约束**：
- 每个用户只能有一个 `is_default=True` 的模型
- `api_key` 使用 Django 的 `encrypt` 或简单 base64 编码存储
- 删除用户时级联删除其所有模型配置

### 预设提供商模板

| provider | 名称 | API地址模板 | 常用模型示例 |
|----------|------|------------|-------------|
| openai | OpenAI | https://api.openai.com/v1/chat/completions | gpt-4o, gpt-3.5-turbo, gpt-4-turbo |
| ollama | Ollama本地 | http://localhost:11434/v1/chat/completions | qwen2.5:7b, llama3, deepseek-r1 |
| qwen | 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions | qwen-plus, qwen-max, qwen-turbo |
| deepseek | DeepSeek | https://api.deepseek.com/chat/completions | deepseek-chat, deepseek-reasoner |
| custom | 自定义 | 用户手动填写 | — |

## 3. 后端架构

### 3.1 新增文件

```
practice/
├── models.py              # 新增 LLMConfig 模型
├── api/
│   ├── serializers.py     # 新增 LLMConfigSerializer
│   ├── views.py           # 新增 LLMConfigViewSet
│   └── urls.py            # 注册 /llm-configs/ 路由
└── services/
    └── llm_service.py     # 重构：支持动态模型调用
```

### 3.2 API 接口

**LLMConfigViewSet** (`/api/v1/practice/llm-configs/`)

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 列出当前用户的所有模型配置 | 已登录 |
| POST | `/` | 创建新的模型配置 | 已登录 |
| GET | `/{id}/` | 获取单个配置详情 | 所有者 |
| PUT | `/{id}/` | 更新配置 | 所有者 |
| DELETE | `/{id}/` | 删除配置 | 所有者 |
| POST | `/{id}/set_default/` | 设为默认模型 | 所有者 |
| POST | `/test_connection/` | 测试API连接是否可用 | 已登录 |

**请求/响应格式**

POST 创建:
```json
{
  "name": "GPT-4o",
  "provider": "openai",
  "api_url": "https://api.openai.com/v1/chat/completions",
  "api_key": "sk-xxx...",
  "model_id": "gpt-4o",
  "is_default": true
}
```

响应:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "GPT-4o",
    "provider": "openai",
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model_id": "gpt-4o",
    "is_default": true,
    "is_active": true,
    // 注意：不返回 api_key 明文
    "created_at": "2026-06-07T12:00:00Z"
  }
}
```

测试连接 POST `/test_connection/`:
```json
// 请求
{ "api_url": "...", "api_key": "...", "model_id": "..." }

// 成功响应
{ "code": 200, "data": { "success": true, "model_name": "gpt-4o", "latency_ms": 1234 } }

// 失败响应
{ "code": 400, "error": "连接失败: Connection timeout" }
```

### 3.3 LLMService 重构

```python
class LLMService:
    def __init__(self):
        self.default_api_url = os.getenv('LLM_API_URL', 'http://localhost:11434/v1/chat/completions')
        self.default_api_key = os.getenv('LLM_API_KEY', '')
        self.default_model = os.getenv('LLM_MODEL', 'qwen2.5:7b')

    def _call_api(self, messages, temperature=0.3, max_tokens=2000, config=None):
        """统一调用 OpenAI 兼容接口"""
        if config:
            url = config.api_url
            key = config.api_key
            model = config.model_id
        else:
            url = self.default_api_url
            key = self.default_api_key
            model = self.default_model

        # 统一请求格式，兼容所有 OpenAI API 格式的服务
        ...

    def evaluate_prompt(self, user_prompt, system_prompt='', config=None):
        """评估提示词，支持传入自定义模型配置"""
        # 复用现有评估逻辑，只是调用时使用动态配置
        ...

    def chat(self, user_prompt, system_prompt='', history=None, config=None):
        """对话功能（Phase 2）"""
        ...
```

### 3.4 评估流程改动

```
之前: 用户提交 → 固定调用 Ollama → 返回评分
之后: 用户提交 → 选择模型 → 用该模型的API调用 → 返回评分
                       ↓ (未选)
                    回退到系统默认模型
```

practice/views.py 的 submit 视图改动：
- 接收前端传来的 `llm_config_id` 参数
- 根据 ID 查询用户的 LLMConfig
- 将 config 传递给 llm_service.evaluate_prompt()

## 4. 前端设计

### 4.1 个人中心 → 我的模型 页面

新增页面路由: `/profile/models/` 或在个人中心内嵌 tab

**功能列表**：
1. **模型卡片列表**：展示用户已添加的所有模型
   - 显示名称、提供商图标、模型ID、默认标记、状态
   - 操作按钮：编辑、删除、设为默认、测试连接
2. **添加模型弹窗/表单**
   - 选择提供商（下拉框，带预设模板）
   - 填写名称、API地址、API Key、模型ID
   - 设为默认开关
3. **测试连接**：点击后发送测试请求，显示延迟和模型信息

### 4.2 练习页面改造

在 [practice_detail.html](file:///home/mjl/Prompt%20Teacher/core/templates/practice_detail.html) 的提交表单中：

- 在「提交」按钮上方新增「选择评估模型」下拉框
- 下拉选项来源：当前用户的所有 `is_active=True` 的 LLMConfig
- 默认选中 `is_default=True` 的模型
- 如果用户没有配置任何模型，隐藏此选择器，使用系统默认

### 4.3 管理后台（可选）

管理员可查看所有用户的模型配置统计（只读），不做强制要求。

## 5. 安全考虑

1. **API Key 加密存储**：使用 Django 的加密字段或 Fernet 对称加密
2. **权限隔离**：用户只能看到和操作自己的模型配置
3. **API Key 不返回给前端**：序列化器排除 api_key 字段，编辑时需要重新输入
4. **测试连接频率限制**：防止滥用，同一用户每分钟最多测试3次

## 6. 数据库迁移

```python
# practice/migrations/xxxx_llm_config.py
class Migration(migrations.Migration):
    dependencies = [('practice', 'previous_migration')]

    operations = [
        migrations.CreateModel(
            name='LLMConfig',
            fields=[
                ('id', models.BigAutoField(...)),
                ('name', models.CharField(max_length=100)),
                ('provider', models.CharField(max_length=50)),
                ('api_url', models.CharField(max_length=500)),
                ('api_key', models.CharField(max_length=500)),
                ('model_id', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(to='users.UserProfile', ...)),
            ],
        ),
    ]
```
