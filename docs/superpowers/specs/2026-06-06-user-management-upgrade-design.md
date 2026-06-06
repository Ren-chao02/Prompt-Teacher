# 用户管理系统升级设计文档

> 日期: 2026-06-06
> 状态: 待用户确认

## 1. 目标

将现有用户管理从「通用账号体系」升级为**真实教学环境适配**的体系：
- 学生用学号登录，教师用工号登录
- 支持真实姓名、班级管理
- 支持批量 Excel 导入用户
- Dashboard 增加班级维度统计

## 2. 数据模型变更

### 2.1 新增 Class 模型（班级）

```python
# users/models.py

class ClassInfo(models.Model):
    """班级模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='班级名称')
    grade = models.CharField(max_length=10, verbose_name='年级')        # 如 "2023"
    major = models.CharField(max_length=50, verbose_name='专业')
    class_number = models.CharField(max_length=10, verbose_name='班号')   # 如 "01"
    description = models.CharField(max_length=200, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['grade', 'major', 'class_number']

    def __str__(self):
        return self.name
```

### 2.2 UserProfile 模型扩展

```python
# users/models.py - UserProfile 新增/修改字段

class UserProfile(AbstractUser):
    # === 现有字段保留 ===
    role, phone, avatar, semester, teacher, created_at  # 不变

    # === 新增字段 ===
    real_name = models.CharField(
        max_length=50,
        verbose_name='真实姓名',
        help_text='必填'
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='工号',
        help_text='仅教师角色'
    )

    # === 修改字段 ===
    class_info = models.ForeignKey(          # 替代原有 major 文本字段
        ClassInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='班级'
    )

    # student_id 保留不变（已有 unique 约束）
    # major 字段标记为 deprecated，后续迁移可删除
```

### 2.3 字段对照表

| 用途 | 旧方案 | 新方案 |
|------|--------|--------|
| 登录标识 | username | 学生: student_id / 教师: employee_id / 管理员: username |
| 姓名 | first_name/last_name（未使用） | real_name（必填） |
| 班级/专业 | major（纯文本） | class_info FK → ClassInfo 模型 |
| 工号 | 无 | employee_id（教师唯一） |
| username | 用户手动填写 | 自动生成（= 学号或工号），对用户隐藏 |

## 3. 登录体系改造

### 3.1 前端：三 Tab 登录页

```
┌──────────────────────────────────────────────┐
│  [学生登录]  [教师登录]  [管理员登录]           │
├──────────────────────────────────────────────┤
│                                              │
│  学生 Tab 输入框:                             │
│    学号  [________________]                   │
│    密码  [________________]                   │
│    [登 录]                                   │
│                                              │
│  教师 Tab 输入框:                             │
│    工号  [________________]                   │
│    密码  [________________]                   │
│    [登 录]                                   │
│                                              │
│  管理员 Tab 输入框:                           │
│    用户名 [________________]                  │
│    密码   [________________]                 │
│    [登 录]                                   │
└──────────────────────────────────────────────┘
```

### 3.2 后端：自定义认证 Backend

```python
# users/auth_backends.py

class RoleBasedAuthBackend(ModelBackend):
    """基于角色的认证后端 - 支持学号/工号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_type = kwargs.get('login_type', 'username')  # 'student_id' | 'employee_id' | 'username'

        if login_type == 'student_id':
            user = UserProfile.objects.filter(student_id=username).first()
        elif login_type == 'employee_id':
            user = UserProfile.objects.filter(employee_id=username).first()
        else:
            user = UserProfile.objects.filter(username=username).first()

        if not user:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
```

### 3.3 settings.py 配置

```python
AUTHENTICATION_BACKENDS = [
    'users.auth_backends.RoleBasedAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # 兜底
]
```

### 3.4 API 调整

LoginSerializer 增加 `login_type` 参数：

```python
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text='学号/工号/用户名')
    password = serializers.CharField(write_only=True)
    login_type = serializers.ChoiceField(
        choices=['student_id', 'employee_id', 'username'],
        default='username'
    )
```

## 4. 批量导入功能

### 4.1 Excel 导入流程

1. **下载模板**: 后端生成标准 .xlsx 模板（含表头+示例行）
2. **上传文件**: 前端拖拽/选择上传 `.xlsx`
3. **预览校验**: 后端解析返回预览数据 + 错误提示
4. **确认导入**: 用户确认后批量创建

### 4.2 Excel 模板格式

| 角色 (role) | 学号/工号 (identifier) | 姓名 (real_name) | 班级名称 (class_name) | 手机号 (phone) |
|---|---|---|---|---|
| student | 202301001 | 张三 | 计算机科学2301班 | 138xxxx |
| teacher | T10001 | 王教授 | - | 139xxxx |

### 4.3 后端处理逻辑

```python
@action(detail=False, methods=['post'])
def batch_import(self, request):
    file = request.FILES['file']
    wb = openpyxl.load_workbook(file)
    ws = wb.active

    results = []
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        role, identifier, name, class_name, phone = row

        # 校验 + 构建用户数据
        # 班级不存在则自动创建
        # username = identifier（自动）
        # 默认密码 = identifier[-6:] 或 "123456"

    return Response({
        'code': 200,
        'data': {
            'preview': results,
            'errors': errors,
            'total': len(results)
        }
    })
```

### 4.4 前端组件

新建 `BatchImportDialog.vue`:
- 三步式 UI（下载模板 → 上传 → 预览确认）
- 错误行高亮显示
- 进度条反馈

## 5. 班级管理

### 5.1 后端

新增 `ClassInfoViewSet`（ModelViewSet）:
- CRUD 完整支持
- 仅管理员可操作
- 注册路由: `/api/v1/classes/`

### 5.2 前端

新增班级管理页面 `views/class/index.vue`:
- 表格展示所有班级（年级、专业、班号、人数统计）
- 新建/编辑/删除班级
- 关联学生数量实时显示

### 5.3 用户列表增强

- 顶部增加「按班级筛选」下拉框
- 表格列增加: real_name、class_info.name、login_identifier

## 6. 用户对话框改造

### 6.1 动态表单（按角色切换）

**学生模式:**
- 姓名（real_name）、学号（student_id）、班级（FK 下拉选）、指导教师（FK 下拉选）、手机号
- 隐藏: 工号、邮箱（可选）

**教师模式:**
- 姓名（real_name）、工号（employee_id）、手机号、邮箱
- 隐藏: 学号、班级、指导教师

**管理员模式:**
- 姓名（real_name）、邮箱、手机号
- 隐藏: 学号、工号、班级、指导教师

### 6.2 创建逻辑调整

```python
def create(self, validated_data):
    password = validated_data.pop('password', '123456')  # 默认密码
    role = validated_data.get('role', 'student')

    if role == 'student':
        validated_data['username'] = validated_data['student_id']
    elif role == 'teacher':
        validated_data['username'] = validated_data['employee_id']

    user = UserProfile(**validated_data)
    user.set_password(password)
    user.save()
    return user
```

## 7. Dashboard 班级维度统计

在现有 Dashboard 中增加:

```
┌───────────────────────────────────────┐
│ 各班级学习情况                        │
│ ┌─────────┬──────┬──────┬──────┬────┐ │
│ │ 班级     │ 人数 │ 练习 │ 均分 │活跃│ │
│ ├─────────┼──────┼──────┼──────┼────┤ │
│ │ 计算机23 │ 45   │ 320  │ 82  │ 89%│ │
│ │ 数学23   │ 38   │ 210  │ 78  │ 76%│ │
│ └─────────┴──────┴──────┴──────┴────┘ │
└───────────────────────────────────────┘
```

## 8. 数据迁移策略

```python
# 迁移步骤
# 1. makemigrations → 创建 ClassInfo 表 + UserProfile 新字段
# 2. 数据迁移脚本:
#    - 将现有 major 文本值迁移为 ClassInfo 记录
#    - 将现有 first_name/last_name 合并到 real_name
#    - 为现有学生生成 employee_id 占位（如需要）
# 3. migrate → 应用 schema 变更
```

## 9. 文件变更清单

### 后端 (Python/Django)

| 文件 | 操作 | 说明 |
|------|------|------|
| `users/models.py` | 修改 | 新增 ClassInfo 模型；UserProfile 加 real_name/employee_id/class_info FK |
| `users/auth_backends.py` | 新建 | RoleBasedAuthBackend 自定义认证 |
| `users/api/views.py` | 修改 | LoginAPIView 支持 login_type；新增 batch_import action；新增 ClassInfoViewSet |
| `users/api/serializers.py` | 修改 | LoginSerializer 加 login_type；UserCreateSerializer 自动生成 username；新增 ClassInfoSerializer |
| `users/api/urls.py` | 修改 | 注册 classes 路由 |
| `users/admin.py` | 修改 | 注册 ClassInfo 到 Admin |
| `prompt_teaching/settings.py` | 修改 | AUTHENTICATION_BACKENDS 配置 |
| `requirements.txt` | 修改 | 添加 openpyxl 依赖 |

### 前端 (Vue)

| 文件 | 操作 | 说明 |
|------|------|------|
| `views/login/index.vue` | 重写 | 三 Tab 登录页（学生/教师/管理员） |
| `views/user/list.vue` | 修改 | 增加班级筛选、表格列调整 |
| `views/user/components/UserDialog.vue` | 重写 | 动态表单（按角色切换） |
| `views/user/components/BatchImportDialog.vue` | 新建 | Excel 批量导入三步对话框 |
| `views/class/index.vue` | 新建 | 班级管理页面 |
| `api/user.js` | 修改 | 新增 batchImport/getClassList 等 API |
| `api/auth.js` | 修改 | login 函数加 login_type 参数 |
| `router/index.js` | 修改 | 注册班级管理路由 |
| `dashboard/index.vue` | 修改 | 增加班级维度统计卡片 |

## 10. 实施顺序建议

1. **数据模型** — ClassInfo + UserProfile 扩展 + 迁移
2. **认证 Backend** — RoleBasedAuthBackend + settings 配置
3. **API 层** — 序列化器调整 + 批量导入接口 + 班级 CRUD 接口
4. **前端登录页** — 三 Tab 重写
5. **前端用户管理** — 对话框改造 + 列表页增强
6. **批量导入** — BatchImportDialog 组件
7. **班级管理** — 班级页面 + 筛选集成
8. **Dashboard** — 班级维度统计
9. **联调测试** — 全链路验证
