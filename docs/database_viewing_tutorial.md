# SQLite 数据库查看完整教程

## 📊 数据库基本信息

- **数据库类型**: SQLite 3
- **数据库文件**: `/home/mjl/Prompt Teacher/db.sqlite3`
- **当前数据统计**:
  - 场景总数: 26个
  - 主题总数: 52个
  - 用户总数: 3个

---

## 🎯 方法一：sqlite3 命令行工具（最推荐）

### 步骤1: 进入数据库交互模式

```bash
cd "/home/mjl/Prompt Teacher"
sqlite3 db.sqlite3
```

你会看到：
```
SQLite version 3.45.1 2024-01-30
Enter ".help" for usage hints.
sqlite>
```

### 步骤2: 常用查看命令

#### 📋 查看所有表
```sql
.tables
```
输出示例：
```
auth_group                          notifications_notification
practice_practicescenario          practice_practicetopic
users_userprofile                  learning_learningmaterial
...
```

#### 🔍 查看表结构
```sql
.schema practice_practicescenario
```

#### 📊 查看数据（基础查询）
```sql
-- 查看所有场景
SELECT * FROM practice_practicescenario;

-- 查看特定字段
SELECT id, scenario_id, title, icon FROM practice_practicescenario;

-- 查看特定场景
SELECT * FROM practice_practicescenario WHERE scenario_id='medical_health';
```

#### 🎨 格式化输出（推荐）
```sql
-- 设置显示模式
.mode column

-- 显示列标题
.headers on

-- 设置列宽度（根据字段数量调整）
.width 5 25 40 8 12

-- 执行查询
SELECT id, scenario_id, title, icon, difficulty, status 
FROM practice_practicescenario 
ORDER BY "order" 
LIMIT 10;
```

输出效果：
```
id  scenario_id         title                            icon     difficulty  status    
--- ------------------- -------------------------------- -------- ----------- ----------
3   content_creation    内容创作与新媒体场景              ✍️       beginner    published 
19  office_efficiency   职场办公与效率提升场景            💼       beginner    published 
```

#### 📈 统计查询
```sql
-- 统计场景数量
SELECT COUNT(*) FROM practice_practicescenario;

-- 统计主题数量
SELECT COUNT(*) FROM practice_practicetopic;

-- 按难度统计场景
SELECT difficulty, COUNT(*) 
FROM practice_practicescenario 
GROUP BY difficulty;
```

#### 🔗 关联查询（场景+主题）
```sql
-- 查看场景及其主题数量
SELECT 
    s.icon, 
    s.title, 
    s.scenario_id, 
    COUNT(t.id) as topic_count
FROM practice_practicescenario s
LEFT JOIN practice_practicetopic t ON s.id = t.scenario_id
GROUP BY s.id
ORDER BY s."order";
```

### 步骤3: 退出sqlite3
```sql
.quit
```
或
```sql
.exit
```

---

## 🐍 方法二：Django Shell（Python方式）

### 步骤1: 打开Django Shell
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py shell
```

### 步骤2: 查询数据示例

```python
# 导入模型
from practice.models import PracticeScenario, PracticeTopic

# 查看所有场景
scenarios = PracticeScenario.objects.all()
for s in scenarios:
    print(f"{s.icon} {s.title} (ID: {s.scenario_id}, 难度: {s.difficulty})")

# 查看特定场景
medical = PracticeScenario.objects.get(scenario_id='medical_health')
print(f"场景: {medical.title}")
print(f"描述: {medical.description}")
print(f"状态: {medical.status}")

# 查看场景的主题
topics = medical.topics.all()
for t in topics:
    print(f"  主题{t.topic_number}: {t.title}")
    print(f"    描述: {t.description}")

# 统计数据
print(f"场景总数: {PracticeScenario.objects.count()}")
print(f"主题总数: {PracticeTopic.objects.count()}")

# 按难度统计
from django.db.models import Count
stats = PracticeScenario.objects.values('difficulty').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['difficulty']}: {stat['count']}个场景")

# 退出
exit()
```

---

## 🚀 方法三：快速查询命令（一行搞定）

### 查看场景列表
```bash
python manage.py shell -c "
from practice.models import PracticeScenario;
for s in PracticeScenario.objects.all().order_by('order'):
    print(f'{s.order}. {s.icon} {s.title} ({s.scenario_id})')
"
```

### 查看主题列表
```bash
python manage.py shell -c "
from practice.models import PracticeTopic;
for t in PracticeTopic.objects.all()[:10]:
    print(f'{t.scenario.title} - 主题{t.topic_number}: {t.title}')
"
```

---

## 📝 实用查询示例

### 1. 查看最新导入的场景
```sql
-- 在sqlite3中执行
SELECT icon, title, scenario_id, difficulty, status
FROM practice_practicescenario
WHERE scenario_id IN (
    'medical_health', 'finance_investment', 
    'hr_recruitment', 'tourism_hotel'
)
ORDER BY "order";
```

### 2. 查看某个场景的所有主题
```sql
SELECT 
    t.topic_number,
    t.title,
    t.description
FROM practice_practicetopic t
JOIN practice_practicescenario s ON t.scenario_id = s.id
WHERE s.scenario_id = 'medical_health'
ORDER BY t.topic_number;
```

### 3. 查看用户数据
```sql
SELECT id, username, email, role FROM users_userprofile;
```

### 4. 查看练习记录（如果有）
```sql
SELECT 
    r.id,
    u.username,
    s.title as scenario,
    r.overall_score,
    r.created_at
FROM practice_practicerecord r
JOIN users_userprofile u ON r.user_id = u.id
JOIN practice_practicescenario s ON r.scenario_id = s.id
ORDER BY r.created_at DESC
LIMIT 10;
```

---

## 🔧 SQLite命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `.tables` | 显示所有表 | `.tables` |
| `.schema 表名` | 显示表结构 | `.schema practice_practicescenario` |
| `.headers on/off` | 显示/隐藏列标题 | `.headers on` |
| `.mode 模式` | 设置输出模式 | `.mode column` |
| `.width 数字...` | 设置列宽度 | `.width 5 20 30` |
| `.output 文件` | 输出到文件 | `.output data.txt` |
| `.output stdout` | 输出到屏幕 | `.output stdout` |
| `.quit` | 退出 | `.quit` |
| `.help` | 显示帮助 | `.help` |

---

## 💾 导出数据到文件

### 导出为CSV格式
```bash
cd "/home/mjl/Prompt Teacher"

sqlite3 db.sqlite3 <<EOF
.headers on
.mode csv
.output scenarios.csv
SELECT id, scenario_id, title, icon, difficulty, status 
FROM practice_practicescenario;
.output stdout
.quit
EOF

# 查看导出的文件
cat scenarios.csv
```

### 导出为JSON格式（需要jq工具）
```bash
sqlite3 db.sqlite3 <<EOF
.mode list
.separator ","
.output scenarios.json
SELECT '[';
SELECT 
    '{"id":"' || id || '",'
    || '"scenario_id":"' || scenario_id || '",'
    || '"title":"' || title || '",'
    || '"icon":"' || icon || '",'
    || '"difficulty":"' || difficulty || '"}'
FROM practice_practicescenario;
SELECT ']';
.output stdout
.quit
EOF
```

---

## 🎓 进阶技巧

### 1. 使用索引优化查询
```sql
-- 查看现有索引
.indexes

-- 创建索引（如果需要）
CREATE INDEX idx_scenario_status ON practice_practicescenario(status);
```

### 2. 使用事务
```sql
BEGIN TRANSACTION;
-- 执行多个操作
UPDATE practice_practicescenario SET status='published' WHERE id=1;
UPDATE practice_practicescenario SET status='published' WHERE id=2;
COMMIT;
```

### 3. 使用视图
```sql
-- 创建视图
CREATE VIEW scenario_summary AS
SELECT 
    s.icon,
    s.title,
    s.scenario_id,
    COUNT(t.id) as topic_count
FROM practice_practicescenario s
LEFT JOIN practice_practicetopic t ON s.id = t.scenario_id
GROUP BY s.id;

-- 使用视图
SELECT * FROM scenario_summary;
```

---

## ⚠️ 注意事项

1. **不要直接修改生产数据库**: 建议通过Django模型或管理界面修改
2. **定期备份**: 备份命令 `cp db.sqlite3 db.sqlite3.backup`
3. **编码问题**: SQLite默认UTF-8，中文显示正常
4. **并发限制**: SQLite不适合高并发场景，生产环境建议用PostgreSQL
5. **字段名冲突**: SQLite的`order`是关键字，查询时要用双引号 `"order"`

---

## 🚀 快速开始（5分钟上手）

### 最简单的查看流程：

```bash
# 1. 进入项目目录
cd "/home/mjl/Prompt Teacher"

# 2. 打开数据库
sqlite3 db.sqlite3

# 3. 设置格式（可选）
.headers on
.mode column

# 4. 查看场景
SELECT icon, title, scenario_id, difficulty FROM practice_practicescenario LIMIT 10;

# 5. 查看主题
SELECT topic_number, title FROM practice_practicetopic LIMIT 10;

# 6. 退出
.quit
```

---

## 📚 附录：主要数据表说明

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| `practice_practicescenario` | 练习场景 | id, scenario_id, title, icon, difficulty, status, order |
| `practice_practicetopic` | 练习主题 | id, scenario_id, topic_number, title, description, example_prompt |
| `practice_practicerecord` | 练习记录 | id, user_id, scenario_id, topic_id, overall_score, created_at |
| `users_userprofile` | 用户信息 | id, username, email, role, avatar |
| `learning_learningmaterial` | 学习资料 | id, title, category, content, status |
| `notifications_notification` | 通知消息 | id, user_id, title, content, is_read |

---

## 🎉 总结

你现在掌握了：
- ✅ 如何打开SQLite数据库
- ✅ 如何查看表和数据
- ✅ 如何格式化输出
- ✅ 如何使用Django Shell查询
- ✅ 如何导出数据
- ✅ 常用查询命令

**推荐学习路径**：
1. 先用sqlite3命令行熟悉基本操作
2. 然后学习Django Shell的Python查询方式
3. 最后掌握高级查询和导出技巧

**下一步**：
- 尝试自己查询其他表的数据
- 学习如何通过Django Admin管理数据
- 了解如何切换到PostgreSQL数据库

---

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看SQLite官方文档: https://www.sqlite.org/docs.html
2. 使用 `.help` 命令查看内置帮助
3. 查看Django文档: https://docs.djangoproject.com/

祝你学习愉快！🎉