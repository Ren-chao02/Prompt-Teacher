# SQLite 数据库查看教程

## 一、数据库基本信息

- **数据库类型**: SQLite 3
- **数据库文件**: `/home/mjl/Prompt Teacher/db.sqlite3`
- **文件大小**: 约 1-2 MB

---

## 二、方法一：使用 sqlite3 命令行工具（推荐）

### 1. 打开数据库

```bash
cd "/home/mjl/Prompt Teacher"
sqlite3 db.sqlite3
```

### 2. 常用命令

#### 显示所有表
```sql
.tables
```

#### 查看表结构
```sql
.schema practice_practicescenario
.schema practice_practicetopic
```

#### 查看场景表数据
```sql
-- 查看所有场景
SELECT id, scenario_id, title, icon, difficulty, status FROM practice_practicescenario;

-- 查看特定场景
SELECT * FROM practice_practicescenario WHERE scenario_id='medical_health';

-- 统计场景数量
SELECT COUNT(*) FROM practice_practicescenario;
```

#### 查看主题表数据
```sql
-- 查看所有主题
SELECT id, scenario_id, topic_number, title FROM practice_practicetopic;

-- 查看某个场景的主题
SELECT t.id, t.topic_number, t.title, s.title as scenario_name
FROM practice_practicetopic t
JOIN practice_practicescenario s ON t.scenario_id = s.id
WHERE s.scenario_id='medical_health';

-- 统计主题数量
SELECT COUNT(*) FROM practice_practicetopic;
```

#### 格式化输出
```sql
-- 设置列显示模式
.mode column

-- 设置标题显示
.headers on

-- 设置输出宽度
.width 5 20 30 10 10

-- 然后执行查询
SELECT id, scenario_id, title, icon, difficulty FROM practice_practicescenario LIMIT 5;
```

### 3. 退出 sqlite3
```sql
.quit
或
.exit
```

---

## 三、方法二：使用 Django Shell（Python方式）

### 1. 打开 Django Shell
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py shell
```

### 2. 查询数据示例

```python
# 导入模型
from practice.models import PracticeScenario, PracticeTopic

# 查看所有场景
scenarios = PracticeScenario.objects.all()
for s in scenarios:
    print(f"{s.icon} {s.title} (ID: {s.scenario_id})")

# 查看特定场景
medical = PracticeScenario.objects.get(scenario_id='medical_health')
print(f"场景: {medical.title}")
print(f"描述: {medical.description}")
print(f"难度: {medical.difficulty}")

# 查看场景的主题
topics = medical.topics.all()
for t in topics:
    print(f"  主题{t.topic_number}: {t.title}")

# 统计数据
print(f"场景总数: {PracticeScenario.objects.count()}")
print(f"主题总数: {PracticeTopic.objects.count()}")

# 退出
exit()
```

---

## 四、方法三：使用 Django DB Shell

### 1. 打开数据库shell
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py dbshell
```

这会自动打开 sqlite3 并连接到正确的数据库。

---

## 五、方法四：查看特定数据（快速命令）

### 查看场景列表
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py shell -c "
from practice.models import PracticeScenario;
for s in PracticeScenario.objects.all().order_by('order'):
    print(f'{s.order}. {s.icon} {s.title} ({s.scenario_id}) - {s.topics.count()}个主题')
"
```

### 查看主题列表
```bash
cd "/home/mjl/Prompt Teacher"
python manage.py shell -c "
from practice.models import PracticeTopic;
for t in PracticeTopic.objects.all().order_by('scenario', 'topic_number')[:10]:
    print(f'{t.scenario.title} - 主题{t.topic_number}: {t.title}')
"
```

---

## 六、实用查询示例

### 1. 查看最新导入的场景（markdown导入的）
```sql
-- 在 sqlite3 中执行
SELECT s.icon, s.title, s.scenario_id, s.difficulty, COUNT(t.id) as topic_count
FROM practice_practicescenario s
LEFT JOIN practice_practicetopic t ON s.id = t.scenario_id
WHERE s.scenario_id IN (
    'content_creation', 'office_efficiency', 'data_logic',
    'education_growth', 'ai_multimodal', 'product_design',
    'sales_service', 'ecommerce_trade', 'legal_compliance',
    'business_strategy', 'creative_writing',
    'medical_health', 'finance_investment', 'hr_recruitment', 'tourism_hotel'
)
GROUP BY s.id
ORDER BY s.order;
```

### 2. 查看用户数据
```sql
-- 查看所有用户
SELECT id, username, email, role FROM users_user;

-- 统计用户数量
SELECT COUNT(*) FROM users_user;
```

### 3. 查看练习记录
```sql
-- 查看最近的练习记录
SELECT r.id, u.username, s.title, r.overall_score, r.created_at
FROM practice_practicerecord r
JOIN users_user u ON r.user_id = u.id
JOIN practice_practicescenario s ON r.scenario_id = s.id
ORDER BY r.created_at DESC
LIMIT 10;
```

---

## 七、导出数据到文件

### 导出场景数据为CSV
```bash
cd "/home/mjl/Prompt Teacher"
sqlite3 db.sqlite3 <<EOF
.headers on
.mode csv
.output scenarios.csv
SELECT id, scenario_id, title, icon, difficulty, status, order FROM practice_practicescenario;
.output stdout
.quit
EOF
```

然后可以查看文件：
```bash
cat scenarios.csv
```

---

## 八、常用SQLite命令速查表

| 命令 | 说明 |
|------|------|
| `.tables` | 显示所有表 |
| `.schema 表名` | 显示表结构 |
| `.headers on/off` | 显示/隐藏列标题 |
| `.mode column/csv/list` | 设置输出模式 |
| `.width 数字...` | 设置列宽度 |
| `.output 文件名` | 输出到文件 |
| `.output stdout` | 输出到屏幕 |
| `.quit` 或 `.exit` | 退出sqlite3 |
| `.help` | 显示帮助 |

---

## 九、注意事项

1. **不要直接修改数据库**: 建议通过Django模型或管理界面修改数据
2. **备份数据库**: 修改前先备份 `db.sqlite3` 文件
3. **编码问题**: SQLite默认使用UTF-8，中文显示正常
4. **性能**: SQLite适合小型项目，大型项目建议切换到PostgreSQL

---

## 十、快速开始（推荐流程）

### 最简单的查看方式：

```bash
# 1. 进入项目目录
cd "/home/mjl/Prompt Teacher"

# 2. 打开数据库
sqlite3 db.sqlite3

# 3. 设置格式
.headers on
.mode column
.width 5 25 40 8 12

# 4. 查看场景
SELECT id, scenario_id, title, icon, difficulty FROM practice_practicescenario LIMIT 10;

# 5. 退出
.quit
```

---

## 附录：数据库表说明

### 主要表结构

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| `practice_practicescenario` | 练习场景 | id, scenario_id, title, icon, difficulty, status |
| `practice_practicetopic` | 练习主题 | id, scenario_id, topic_number, title, description |
| `practice_practicerecord` | 练习记录 | id, user_id, scenario_id, overall_score, created_at |
| `users_user` | 用户表 | id, username, email, role |
| `learning_learningmaterial` | 学习资料 | id, title, category, status |
| `notifications_notification` | 通知消息 | id, user_id, title, message, is_read |

---

祝你查看数据库顺利！如有问题，随时询问。