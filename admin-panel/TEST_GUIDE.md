# 🧪 Prompt Teacher 管理系统 - 测试账号说明

## ✅ 问题已修复

**问题原因**: 
- 测试账号密码未正确设置
- 系统中只有 admin 账号，缺少教师和学生账号

**解决方案**:
- ✅ 已重置所有测试账号密码
- ✅ 已创建完整的测试账号体系

---

## 👥 测试账号列表

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| **管理员** | `admin` | `admin123` | 拥有所有权限，可管理用户、查看全部数据 |
| **教师** | `teacher1` | `teacher123` | 可管理学习内容、练习、查看自己的学生数据 |
| **学生** | `student1` | `student123` | 可查看自己的学习进度和成绩 |

---

## 🚀 登录步骤

### 1. 启动后端服务
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py runserver 0.0.0.0:8000
```

### 2. 启动前端服务（已在运行）
```bash
cd "/home/mjl/Prompt Teacher/admin-panel"
npm run dev
```
**访问地址**: http://localhost:8002/

### 3. 登录测试

**方式一：使用管理员账号**
```
用户名: admin
密码: admin123
```

**方式二：使用教师账号**
```
用户名: teacher1
密码: teacher123
```

**方式三：使用学生账号**
```
用户名: student1
密码: student123
```

---

## 📊 权限对照表

| 功能模块 | 管理员 (admin) | 教师 (teacher) | 学生 (student) |
|---------|:---:|:---:|:---:|
| 仪表盘 | ✅ | ✅ | ✅ |
| 用户管理 | ✅ | ❌ | ❌ |
| 学习管理 | ✅ | ✅ | ❌ |
| 练习系统 | ✅ | ✅ | ❌ |
| 数据分析 | ✅ | ❌ | ❌ |
| 个人中心 | ✅ | ✅ | ✅ |

---

## 🔍 测试场景

### 场景 1：管理员完整功能测试
```bash
# 1. 使用 admin 登录
# 2. 访问 /users/list - 应该能看到3个用户
# 3. 点击"新建用户" - 可以创建新用户
# 4. 选择某个用户，点击"编辑" - 可以修改信息
# 5. 选择某个用户，点击"重置密码" - 可以重置密码
# 6. 勾选多个用户，点击"批量删除" - 可以批量删除
# 7. 切换用户的启用/禁用状态开关
# 8. 访问 /profile - 可以修改个人信息和密码
```

### 场景 2：教师权限测试
```bash
# 1. 使用 teacher1 登录
# 2. 应该看到仪表盘和个人中心菜单
# 3. 不应该看到"用户管理"菜单（权限控制）
# 4. 访问 /users/list 会显示403页面
# 5. 访问 /profile 可以正常显示
```

### 场景 3：学生权限测试
```bash
# 1. 使用 student1 登录
# 2. 只能看到基本的仪表盘和个人中心
# 3. 大部分管理功能不可见或显示403
```

---

## 🛠️ API 接口测试

### 登录接口
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**预期返回**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      ...
    }
  }
}
```

### 获取当前用户信息
```bash
# 先获取 token
TOKEN="your_access_token_here"

curl http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### 获取用户列表（需要管理员权限）
```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚠️ 常见问题

### Q1: 显示"访问被拒绝"怎么办？
**A**: 
1. 清除浏览器缓存和 localStorage
2. 确认使用的账号和密码正确
3. 检查后端服务是否正常运行

### Q2: 密码忘记了？
**A**: 
- 管理员可以通过"用户管理"页面的"重置密码"功能重置其他用户密码
- 或者在 Django shell 中执行：
  ```python
  from users.models import UserProfile
  user = UserProfile.objects.get(username='admin')
  user.set_password('new_password')
  user.save()
  ```

### Q3: 如何添加新用户？
**A**: 
1. 使用 admin 账号登录
2. 进入"用户管理"页面
3. 点击"新建用户"按钮
4. 填写用户信息并保存

---

## 📞 技术支持

如果遇到问题，请检查：

1. **后端日志**: 查看 Django 控制台输出
2. **前端日志**: 打开浏览器 F12 开发者工具 -> Console
3. **网络请求**: F12 -> Network 标签查看请求详情
4. **浏览器缓存**: Ctrl+Shift+R 强制刷新

---

## 🎯 下一步功能

根据实施计划，接下来将开发：

- [ ] Phase 3: 学习内容管理
- [ ] Phase 4: 练习系统管理  
- [ ] Phase 5: 数据分析与仪表盘增强

---

**✨ 现在可以开始测试了！祝您使用愉快！**
