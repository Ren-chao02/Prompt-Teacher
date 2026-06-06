# 用户管理系统升级 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将用户管理从通用账号体系升级为真实教学环境适配体系（学号/工号登录、班级管理、批量导入、班级统计）

**Architecture:** 后端在现有 Django AbstractUser 基础上扩展 ClassInfo 模型和 UserProfile 字段，新增 RoleBasedAuthBackend 支持多标识登录，新增 batch_import action 解析 Excel；前端重写登录页为三 Tab、改造用户对话框为动态表单、新增批量导入和班级管理页面

**Tech Stack:** Django 6 / DRF / SQLite(开发) | Vue 3 / Element Plus / Pinia / Vite | openpyxl（Excel 解析）

---

## Task 1: 数据模型 — ClassInfo + UserProfile 扩展

**Files:**
- Modify: `users/models.py`
- Create: `users/migrations/XXXX_add_classinfo_and_user_fields.py` (auto-generated)

- [ ] **Step 1: 在 users/models.py 中添加 ClassInfo 模型**

在文件顶部 import 之后、UserProfile 类之前插入：

```python
class ClassInfo(models.Model):
    """班级模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='班级名称')
    grade = models.CharField(max_length=10, verbose_name='年级')
    major = models.CharField(max_length=50, verbose_name='专业')
    class_number = models.CharField(max_length=10, verbose_name='班号')
    description = models.CharField(max_length=200, blank=True, default='', verbose_name='备注')

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['grade', 'major', 'class_number']

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()
```

- [ ] **Step 2: 在 UserProfile 类中添加新字段**

在 `created_at` 字段之前、`teacher` FK 之后插入：

```python
    real_name = models.CharField(
        max_length=50,
        default='',
        blank=True,
        verbose_name='真实姓名',
        help_text='必填'
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        default=None,
        verbose_name='工号',
        help_text='仅教师角色需要填写，全局唯一'
    )

    class_info = models.ForeignKey(
        ClassInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='班级',
        help_text='学生所属班级'
    )
```

- [ ] **Step 3: 更新 UserProfile.__str__ 方法**

替换现有的 `__str__` 方法：

```python
    def __str__(self):
        if self.real_name:
            if self.role == 'student' and self.student_id:
                return f'{self.real_name} ({self.student_id})'
            elif self.role == 'teacher' and self.employee_id:
                return f'{self.real_name} ({self.employee_id})'
            return self.real_name
        return self.username
```

- [ ] **Step 4: 生成并应用数据库迁移**

Run:
```bash
cd "/home/mjl/Prompt Teacher" && python manage.py makemigrations users --name add_classinfo_and_user_fields
```

Expected: 迁移文件生成成功，包含 ClassInfo 表 + UserProfile 新字段

Then run:
```bash
cd "/home/mjl/Prompt Teacher" && python manage.py migrate users
```

Expected: `OK` + 表创建成功

---

## Task 2: 认证 Backend — RoleBasedAuthBackend

**Files:**
- Create: `users/auth_backends.py`
- Modify: `prompt_teaching/settings.py` (~line 175, after SPECTACULAR_SETTINGS)

- [ ] **Step 1: 创建 users/auth_backends.py**

```python
"""自定义认证后端 - 支持学号/工号/用户名登录"""
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile


class RoleBasedAuthBackend(ModelBackend):
    """
    基于角色的认证后端。

    通过 login_type 参数决定用哪个字段查找用户：
      - 'student_id': 用 student_id 查找
      - 'employee_id': 用 employee_id 查找
      - 'username' (default): 用 username 查找
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_type = kwargs.get('login_type', 'username')

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

- [ ] **Step 2: 在 settings.py 中注册自定义认证 Backend**

在文件末尾 `SPECTACULAR_SETTINGS` 配置之后添加：

```python
# 自定义认证后端 - 支持学号/工号登录
AUTHENTICATION_BACKENDS = [
    'users.auth_backends.RoleBasedAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # 兜底
]
```

- [ ] **Step 3: 验证 Django check 通过**

Run:
```bash
cd "/home/mjl/Prompt Teacher" && python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

---

## Task 3: API 层 — 序列化器调整 + 批量导入接口 + 班级 CRUD 接口

**Files:**
- Modify: `users/api/serializers.py`
- Modify: `users/api/views.py`
- Modify: `users/api/urls.py`
- Modify: `requirements.txt` (添加 openpyxl)
- Modify: `users/admin.py`

### 3a. 序列化器

- [ ] **Step 3a-1: 在 serializers.py 中添加 ClassInfoSerializer**

在文件末尾追加：

```python
class ClassInfoSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClassInfo
        fields = ['id', 'name', 'grade', 'major', 'class_number', 'description', 'student_count']
        read_only_fields = ['id', 'student_count']
```

- [ ] **Step 3a-2: 修改 LoginSerializer 支持 login_type**

将现有 LoginSerializer 替换为：

```python
class LoginSerializer(serializers.Serializer):
    """登录序列化器 - 支持多类型标识"""
    identifier = serializers.CharField(help_text='学号/工号/用户名')
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')
    login_type = serializers.ChoiceField(
        choices=['student_id', 'employee_id', 'username'],
        default='username',
        help_text='登录方式'
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        login_type = attrs.get('login_type', 'username')

        from django.contrib.auth import authenticate
        user = authenticate(
            request=self.context.get('request'),
            username=identifier,
            password=password,
            login_type=login_type
        )

        if not user:
            raise serializers.ValidationError('账号或密码错误')

        if not user.is_active:
            raise serializers.ValidationError('该账号已被禁用')

        attrs['user'] = user
        return attrs
```

- [ ] **Step 3a-3: 更新 UserSerializer 包含新字段**

修改 UserSerializer 的 fields 列表和 Meta：

```python
class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class_name = serializers.CharField(source='class_info.name', read_only=True, default='')
    class_id = serializers.IntegerField(source='class_info.id', read_only=True, default=None)
    login_identifier = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'real_name', 'email', 'role', 'phone',
            'avatar', 'student_id', 'employee_id', 'semester',
            'class_info', 'class_name', 'class_id',
            'teacher', 'date_joined', 'last_login', 'is_active', 'login_identifier'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def get_login_identifier(self, obj):
        if obj.role == 'student':
            return obj.student_id or obj.username
        elif obj.role == 'teacher':
            return obj.employee_id or obj.username
        return obj.username
```

- [ ] **Step 3a-4: 更新 UserCreateSerializer 自动生成 username + real_name 必填**

替换 create 方法：

```python
class UserCreateSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')
    password_confirm = serializers.CharField(max_length=128, write_only=True, help_text='确认密码')

    class Meta:
        model = UserProfile
        fields = [
            'real_name', 'role', 'email', 'password', 'password_confirm',
            'phone', 'student_id', 'employee_id', 'semester',
            'class_info', 'teacher'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})

        role = attrs.get('role', 'student')

        if role == 'student' and not attrs.get('student_id'):
            raise serializers.ValidationError({'student_id': '学生角色必须填写学号'})

        if role == 'student' and not attrs.get('real_name'):
            raise serializers.ValidationError({'real_name': '真实姓名不能为空'})

        if role == 'teacher' and not attrs.get('employee_id'):
            raise serializers.ValidationError({'employee_id': '教师角色必须填写工号'})

        if role == 'teacher' and not attrs.get('real_name'):
            raise serializers.ValidationError({'real_name': '真实姓名不能为空'})

        # 学号唯一性检查
        if attrs.get('student_id'):
            if UserProfile.objects.filter(student_id=attrs['student_id']).exists():
                raise serializers.ValidationError({'student_id': '该学号已存在'})

        # 工号唯一性检查
        if attrs.get('employee_id'):
            if UserProfile.objects.filter(employee_id=attrs['employee_id']).exists():
                raise serializers.ValidationError({'employee_id': '该工号已存在'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password', '123456')
        role = validated_data.get('role', 'student')

        # 自动生成 username
        if role == 'student':
            validated_data['username'] = validated_data.get('student_id', '')
        elif role == 'teacher':
            validated_data['username'] = validated_data.get('employee_id', '')

        user = UserProfile(**validated_data)
        user.set_password(password)
        user.save()

        return user
```

- [ ] **Step 3a-5: 更新 UserUpdateSerializer 包含新字段**

```python
class UserUpdateSerializer(serializers.ModelSerializer):
    """更新用户信息序列化器"""

    class Meta:
        model = UserProfile
        fields = [
            'real_name', 'email', 'phone', 'avatar', 'student_id',
            'employee_id', 'semester', 'class_info', 'teacher'
        ]

    def validate_student_id(self, value):
        user = self.context['request'].user
        queryset = UserProfile.objects.filter(student_id=value)
        if user.pk:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise serializers.ValidationError('该学号已存在')
        return value

    def validate_employee_id(self, value):
        user = self.context['request'].user
        queryset = UserProfile.objects.filter(employee_id=value)
        if user.pk:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise serializers.ValidationError('该工号已存在')
        return value

    def validate_teacher(self, value):
        if value and value.role not in ['admin', 'teacher']:
            raise serializers.ValidationError('只能选择管理员或教师作为指导教师')
        return value
```

### 3b. Views

- [ ] **Step 3b-1: 修改 LoginAPIView 使用新的 LoginSerializer 字段名**

在 views.py 中修改 LoginAPIView.post：

```python
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)

        # 获取用户信息
        user_serializer = UserSerializer(user)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_serializer.data
            }
        }, status=status.HTTP_200_OK)
```

注意：LoginSerializer 已改用 `identifier` + `login_type` 替代原 `username`，但 authenticate 调用方式不变（通过 kwargs 传递 login_type）。

- [ ] **Step 3b-2: 在 views.py 中添加 ClassInfoViewSet**

在 UserViewSet 类之后添加：

```python
class ClassInfoViewSet(viewsets.ModelViewSet):
    """班级管理 ViewSet"""
    queryset = ClassInfo.objects.all().order_by('grade', 'major', 'class_number')
    serializer_class = ClassInfoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade', 'major']
    search_fields = ['name', 'major']
    ordering_fields = ['grade', 'name', 'student_count']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            from ..permissions import IsAdmin
            permission_classes = [IsAdmin]
        return [p() for p in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages
                }
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {'results': serializer.data, 'count': queryset.count()}
        })
```

- [ ] **Step 3b-3: 在 UserViewSet 中添加 batch_import 和 download_template actions**

在 reset_password 方法之后添加：

```python
    @action(detail=False, methods=['post'])
    def batch_import(self, request):
        """批量导入用户（Excel）"""
        if 'file' not in request.FILES:
            return Response({
                'code': 400,
                'message': '请上传 Excel 文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({
                'code': 400,
                'message': '仅支持 .xlsx/.xls 格式'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            import openpyxl
            wb = openpyxl.load_workbook(file)
            ws = wb.active
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'文件解析失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []
        created_classes = {}

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue

            try:
                role_raw, identifier, name, class_name, phone = (
                    str(row[0] or '').strip().lower(),
                    str(row[1] or '').strip(),
                    str(row[2] or '').strip(),
                    str(row[3] or '').strip(),
                    str(row[4] or '').strip() or ''
                )

                if not role_raw or not identifier or not name:
                    errors.append({
                        'row': row_idx,
                        'error': '角色、标识符和姓名为必填项'
                    })
                    continue

                if role_raw not in ('student', 'teacher'):
                    errors.append({
                        'row': row_idx,
                        'error': f'无效的角色: {role_raw}，应为 student 或 teacher'
                    })
                    continue

                # 处理班级自动创建
                class_obj = None
                if class_name and role_raw == 'student':
                    if class_name in created_classes:
                        class_obj = created_classes[class_name]
                    else:
                        class_obj, _ = ClassInfo.objects.get_or_create(
                            name=class_name,
                            defaults={'grade': '', 'major': '', 'class_number': ''}
                        )
                        created_classes[class_name] = class_obj

                # 构建用户数据
                user_data = {
                    'real_name': name,
                    'role': role_raw,
                    'phone': phone,
                    'class_info': class_obj,
                }

                if role_raw == 'student':
                    user_data['student_id'] = identifier
                    if UserProfile.objects.filter(student_id=identifier).exists():
                        errors.append({'row': row_idx, 'error': f'学号 {identifier} 已存在'})
                        continue
                else:
                    user_data['employee_id'] = identifier
                    if UserProfile.objects.filter(employee_id=identifier).exists():
                        errors.append({'row': row_idx, 'error': f'工号 {identifier} 已存在'})
                        continue

                user_data['username'] = identifier
                user = UserProfile(**user_data)
                default_pwd = identifier[-6:] if len(identifier) >= 6 else '123456'
                user.set_password(default_pwd)
                user.save()

                results.append({
                    'row': row_idx,
                    'role': role_raw,
                    'identifier': identifier,
                    'name': name,
                    'class_name': class_name or '-',
                    'default_password': default_pwd,
                    'status': 'success'
                })

            except Exception as e:
                errors.append({'row': row_idx, 'error': str(e)})

        return Response({
            'code': 200,
            'message': f'导入完成：成功 {len(results)} 条，失败 {len(errors)} 条',
            'data': {
                'results': results,
                'errors': errors,
                'total_success': len(results),
                'total_errors': len(errors)
            }
        })

    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """下载导入模板"""
        import openpyxl
        from django.http import HttpResponse
        from io import BytesIO

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '用户导入模板'

        headers = ['角色', '学号/工号', '姓名', '班级名称', '手机号']
        ws.append(headers)

        # 示例行
        ws.append(['student', '202301001', '张三', '计算机科学2301班', '13800138000'])
        ws.append(['teacher', 'T10001', '王教授', '', '13900139000'])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="user_import_template.xlsx"'
        return response
```

- [ ] **Step 3b-4: 在 statistics action 中增加班级维度数据**

修改 existing statistics action 的返回值，增加 `by_class` 字段：

在 statistics 方法中，existing return 之前添加：

```python
        # 班级维度统计
        class_stats = []
        for cls in ClassInfo.objects.all():
            students = UserProfile.objects.filter(class_info=cls, role='student')
            class_stats.append({
                'class_id': cls.id,
                'class_name': cls.name,
                'student_count': students.count(),
            })
```

并在返回 data 中加入 `'by_class': class_stats`。

### 3c. URLs & Admin & Requirements

- [ ] **Step 3c-1: 修改 urls.py 注册 ClassInfoViewSet**

在 router.register 行之后添加：

```python
router.register(r'classes', ClassInfoViewSet, basename='classinfo')
```

并更新 imports:

```python
from .views import (
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
    UserViewSet,
    ClassInfoViewSet,
)
```

- [ ] **Step 3c-2: 注册 ClassInfo 到 admin.py**

```python
from django.contrib import admin
from .models import UserProfile, ClassInfo


@admin.register(ClassInfo)
class ClassInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'major', 'class_number',)
    list_filter = ('grade', 'major',)
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'username', 'role', 'student_id', 'employee_id', 'class_info', 'is_active')
    list_filter = ('role', 'is_active', 'class_info',)
    search_fields = ('username', 'real_name', 'student_id', 'employee_id', 'email')
```

- [ ] **Step 3c-3: 添加 openpyxl 到 requirements.txt**

在 requirements.txt 中添加一行:

```
openpyxl>=3.1.0
```

- [ ] **Step 3c-4: 安装依赖 + 生成迁移 + migrate + check**

Run:
```bash
pip install openpyxl>=3.1.0 && cd "/home/mjl/Prompt Teacher" && python manage.py makemigrations users --name update_serializers_and_views && python manage.py migrate && python manage.py check
```

Expected: 全部 OK

---

## Task 4: 前端 API 层 + 登录页重写

**Files:**
- Modify: `admin-panel/src/api/auth.js`
- Modify: `admin-panel/src/api/user.js`
- Rewrite: `admin-panel/src/views/login/index.vue`

### 4a. API 层

- [ ] **Step 4a-1: 修改 auth.js loginApi 发送新字段**

```javascript
export function loginApi(data) {
  // data: { identifier, password, login_type }
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}
```

- [ ] **Step 4a-2: 在 user.js 中添加新 API 函数**

追加到文件末尾：

```javascript
export function getClassList(params) {
  return request({
    url: '/classes/',
    method: 'get',
    params
  })
}

export function createClass(data) {
  return request({
    url: '/classes/',
    method: 'post',
    data
  })
}

export function updateClass(id, data) {
  return request({
    url: `/classes/${id}/`,
    method: 'put',
    data
  })
}

export function deleteClass(id) {
  return request({
    url: `/classes/${id}/`,
    method: 'delete'
  })
}

export function batchImportUsers(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/users/batch_import/',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}

export function downloadImportTemplate() {
  return request({
    url: '/users/download_template/',
    method: 'get',
    responseType: 'blob'
  })
}
```

### 4b. 登录页重写

- [ ] **Step 4b-1: 重写 login/index.vue 为三 Tab 登录页**

完整替换文件内容：

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="title">Prompt Teacher</h1>
        <p class="subtitle">智能教学管理平台</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <!-- 学生登录 -->
        <el-tab-pane name="student">
          <template #label>
            <span class="tab-label"><el-icon><User /></el-icon>学生登录</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="studentRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入学号" size="large"
                prefix-icon="Postcard" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 教师登录 -->
        <el-tab-pane name="teacher">
          <template #label>
            <span class="tab-label"><el-icon><Briefcase /></el-icon>教师登录</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="teacherRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入工号" size="large"
                prefix-icon="Ticket" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 管理员登录 -->
        <el-tab-pane name="admin">
          <template #label>
            <span class="tab-label"><el-icon><Setting /></el-icon>管理员</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="adminRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入用户名" size="large"
                prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Briefcase, Setting, Postcard, Ticket, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref('student')
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ identifier: '', password: '' })

const requiredRule = { required: true, message: '此项不能为空', trigger: 'blur' }
const pwdRule = { required: true, message: '请输入密码', trigger: 'blur' }

const studentRules = { identifier: [{ ...requiredRule, message: '请输入学号' }], password: pwdRule }
const teacherRules = { identifier: [{ ...requiredRule, message: '请输入工号' }], password: pwdRule }
const adminRules = { identifier: [{ ...requiredRule, message: '请输入用户名' }], password: pwdRule }

async function handleLogin() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch (_e) { return }

  loading.value = true
  try {
    await authStore.login({
      identifier: form.identifier,
      password: form.password,
      login_type: activeTab.value === 'admin' ? 'username' : activeTab.value
    })
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px; padding: 36px 40px 32px;
  background: #fff; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
}
.login-header { text-align: center; margin-bottom: 24px; }
.title { font-size: 26px; font-weight: 700; color: #333; margin: 0 0 6px; }
.subtitle { font-size: 14px; color: #999; margin: 0; }
.login-button { width: 100%; height: 46px; font-size: 16px; border-radius: 8px; }
.tab-label { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; }
.login-tabs :deep(.el-tabs__header) { margin-bottom: 0; }
.login-tabs :deep(.el-tabs__item) { height: 44px; line-height: 44px; font-size: 14px; }
</style>
```

- [ ] **Step 4b-2: 更新 auth store 的 login action 适配新响应格式**

auth store 不需改动——login action 已经从 `res.data` 中取 `access`/`refresh`/`user`，与后端返回格式一致。验证即可。

- [ ] **Step 4b-3: Build 验证**

Run:
```bash
cd "/home/mjl/Prompt Teacher/admin-panel" && npm run build
```

Expected: build 成功

---

## Task 5: 用户对话框动态表单改造

**Files:**
- Rewrite: `admin-panel/src/views/user/components/UserDialog.vue`

- [ ] **Step 5-1: 重写 UserDialog.vue 为按角色切换的动态表单**

核心逻辑：
- `watch(formData.role)` 切换时显示/隐藏不同字段组
- 学生模式: real_name, student_id, class_info(下拉), teacher(下拉), phone
- 教师模式: real_name, employee_id, email, phone
- 管理员模式: real_name, email, phone
- 创建时隐藏 username（自动生成）
- 密码可选填（不填默认 123456）

表单字段映射：

| 角色 | 显示字段 |
|------|---------|
| student | real_name*, student_id*, class_info(下拉), teacher(下拉), phone |
| teacher | real_name*, employee_id*, email, phone |
| admin | real_name*, email, phone |

(* 表示必填)

handleSubmit 使用 Promise 模式调用 validate（参考 ResetPasswordDialog 修复后的正确用法）。

---

## Task 6: 批量导入组件 BatchImportDialog

**Files:**
- Create: `admin-panel/src/views/user/components/BatchImportDialog.vue`

- [ ] **Step 6-1: 创建 BatchImportDialog.vue**

三步式 UI 组件：
1. Step 1: 下载模板按钮 → 调用 `downloadImportTemplate()` 触发下载
2. Step 2: 文件上传区域（拖拽+点击）→ 选择 `.xlsx` 文件
3. Step 3: 预览表格 + 错误列表 + 确认/取消按钮

Props: `visible` (Boolean)
Emits: `update:visible`, `success`

关键实现细节：
- 用 `el-upload` 或原生 input[type=file] 处理文件选择
- 上传后调用 `batchImportUsers(file)` 获取预览结果
- 用 `el-table` 展示预览数据（列: 行号、角色、标识、姓名、班级、状态）
- 错误行用红色高亮
- 确认后弹二次确认框

---

## Task 7: 班级管理页面 + 用户列表增强

**Files:**
- Create: `admin-panel/src/views/class/index.vue`
- Modify: `admin-panel/src/views/user/list.vue`
- Modify: `admin-panel/src/router/index.js`

### 7a. 班级管理页面

- [ ] **Step 7a-1: 创建 views/class/index.vue**

页面结构：
- 顶部操作栏: 新建班级按钮
- 表格: 名称、年级、专业、班号、人数、操作(编辑/删除)
- 新建/编辑 Dialog: name, grade, major, class_number, description
- 分页

### 7b. 用户列表增强

- [ ] **Step 7b-1: 修改 user/list.vue**

变更点：
1. 搜索栏新增「班级筛选」下拉框（调用 `getClassList()` 获取选项）
2. 操作栏新增「批量导入」按钮（打开 BatchImportDialog）和「导出 Excel」按钮
3. 表格列调整: 移除 username 列 → 增加 real_name, class_name, login_identifier 列
4. 引入 BatchImportDialog 组件

- [ ] **Step 7b-2: 注册路由**

在 router/index.js children 数组中 UserList 路由之后添加：

```javascript
{
  path: 'classes/manage',
  name: 'ClassManage',
  component: () => import('@/views/class/index.vue'),
  meta: {
    title: '班级管理',
    icon: 'School',
    roles: ['admin']
  }
},
```

---

## Task 8: Dashboard 班级维度统计

**Files:**
- Modify: `admin-panel/src/views/dashboard/index.vue`

- [ ] **Step 8-1: 在 Dashboard 中增加班级统计卡片**

在现有统计栏下方、学习进度卡片之前，新增一个 el-row 区域：

```
┌─────────────────────────────────────────────┐
│ 各班级学习情况                               │
│ ┌──────┬──────────┬────┬──────┬────┬──────┐ │
│ │ 班级  │ 专业     │ 人数│ 练习 │均分 │活跃率│ │
│ ├──────┼──────────┼────┼──────┼────┼──────┤ │
│ │...   │ ...      │ .. │ ...  │ .. │ ...  │ │
│ └──────┴──────────┴────┴──────┴────┴──────┘ │
└─────────────────────────────────────────────┘
```

数据来源: `getUserStatistics()` 返回的 `by_class` 字段（Task 3b-4 已在后端添加）

如果无班级数据则显示空状态提示。

---

## Task 9: 联调测试 + Build 验证

- [ ] **Step 9-1: 后端全量 check + test**

Run:
```bash
cd "/home/mjl/Prompt Teacher" && python manage.py check && python -m pytest --tb=short
```

Expected: check OK + 测试通过（允许已有通知测试的已知失败）

- [ ] **Step 9-2: 前端 build + test**

Run:
```bash
cd "/home/mjl/Prompt Teacher/admin-panel" && npm run build && npm test
```

Expected: build 成功 + 80 tests pass

- [ ] **Step 9-3: 手动验证清单**

- [ ] 学生 Tab 登录：用已存在学生的 student_id + 密码登录 → 成功跳转 Dashboard
- [ ] 教师 Tab 登录：用已存在教师的 employee_id + 密码登录 → 成功
- [ ] 管理员 Tab 登录：用管理员 username + 密码登录 → 成功
- [ ] 新建学生：填写姓名/学号/班级 → 自动生成 username → 列表中可见
- [ ] 新建教师：填写姓名/工号 → 自动生成 username → 列表中可见
- [ ] 批量导入：上传 Excel → 预览 → 确认 → 用户出现在列表中
- [ ] 班级管理：新建班级 → 用户列表可筛选 → Dashboard 显示班级统计
