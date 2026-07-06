"""
将历史 SQLite 数据库 (db.sqlite3) 的数据迁移到当前部署的 PostgreSQL。

用法（在 backend 容器内执行）:
    python manage.py shell -c "exec(open('/app/scripts/migrate_sqlite_to_pg.py').read())"
或:
    python /app/scripts/migrate_sqlite_to_pg.py

数据来源: /app/data/db.sqlite3  （需先把宿主机的 db.sqlite3 拷进容器 /app/data/）

迁移内容:
  - users.ClassInfo          (班级)
  - users.UserProfile        (用户, 含密码哈希; 自引用 teacher 在第二遍回填)
  - learning.LearningMaterial(学习资料)
  - practice.PracticeScenario(练习场景)
  - practice.PracticeTopic   (练习主题)
  - practice.PracticeRecord  (练习记录)
  - practice.LLMConfig       (LLM 配置)

迁移后会:
  - 按文档规则重置所有教师/学生密码为「手机号后6位 / 标识符后6位 / 123456」
  - 管理员密码重置为 admin123
  - must_change_password 置为 False（方便验证；可后续在 UI 中改密）
  - 重置 PostgreSQL 自增序列
"""
import os
import sys
import json
import sqlite3

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
django.setup()

from django.db import transaction, connection
from django.db import models as dj_models

from users.models import UserProfile, ClassInfo
from learning.models import LearningMaterial, MaterialInteraction
from practice.models import PracticeScenario, PracticeTopic, PracticeRecord, LLMConfig

SQLITE_PATH = '/app/data/db.sqlite3'

# 表名 -> 模型，按外键依赖排序（被依赖者在前）
IMPORT_ORDER = [
    ('users_classinfo',            ClassInfo),
    ('users_userprofile',          UserProfile),   # 自引用 teacher 第二遍回填
    ('learning_learningmaterial',  LearningMaterial),
    ('practice_practicescenario',  PracticeScenario),
    ('practice_practicetopic',     PracticeTopic),
    ('practice_practicerecord',    PracticeRecord),
    ('practice_llmconfig',         LLMConfig),
]


def read_sqlite_rows(table):
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table}')
    cols = [d[0] for d in cur.description]
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return cols, rows


def parse_json_val(field, val):
    """sqlite 中 JSONField 存为文本，需还原为 Python 对象"""
    if isinstance(field, dj_models.JSONField) and val is not None and isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, ValueError):
            return val
    return val


@transaction.atomic
def migrate():
    if not os.path.exists(SQLITE_PATH):
        print(f'❌ 找不到 SQLite 文件: {SQLITE_PATH}')
        sys.exit(1)

    # ---------- 1. 清空现有 PG 数据 ----------
    print('🧹 清空现有 PostgreSQL 数据...')
    LLMConfig.objects.all().delete()
    PracticeRecord.objects.all().delete()
    PracticeTopic.objects.all().delete()
    PracticeScenario.objects.all().delete()
    MaterialInteraction.objects.all().delete()
    LearningMaterial.objects.all().delete()
    UserProfile.objects.all().delete()
    ClassInfo.objects.all().delete()

    # ---------- 2. 按顺序导入各表 ----------
    for table, model in IMPORT_ORDER:
        cols, rows = read_sqlite_rows(table)
        sqlite_cols = set(cols)
        # 收集模型具体字段
        concrete = [f for f in model._meta.concrete_fields]

        # UserProfile 的自引用 teacher 字段第一遍跳过
        skip_atts = set()
        if model is UserProfile:
            skip_atts.add('teacher')

        instances = []
        for row in rows:
            obj = model()
            obj.pk = row['id']
            for f in concrete:
                if f.attname in skip_atts:
                    continue
                col = f.column
                if col in sqlite_cols:
                    val = parse_json_val(f, row[col])
                    if f.is_relation:
                        setattr(obj, f.attname, val)   # 设 xxx_id
                    else:
                        setattr(obj, f.attname, val)
                # 列不在 sqlite 中则保留模型默认值
            instances.append(obj)

        model.objects.bulk_create(instances, batch_size=200)
        print(f'  ✅ {table:32s} -> {model.__name__:20s}  {len(instances)} 条')

    # ---------- 3. 回填 UserProfile.teacher 自引用 ----------
    cols, rows = read_sqlite_rows('users_userprofile')
    updated = 0
    for row in rows:
        tid = row.get('teacher_id')
        if tid:
            UserProfile.objects.filter(id=row['id']).update(teacher_id=tid)
            updated += 1
    print(f'  🔗 回填 teacher 自引用: {updated} 条')

    # ---------- 4. 重置密码为已知规则 ----------
    print('\n🔑 重置密码为已知规则...')
    rule_counts = {'phone': 0, 'ident': 0, 'fallback': 0, 'admin': 0}

    def default_pwd(user):
        if user.phone and len(user.phone) >= 6:
            return user.phone[-6:], 'phone'
        ident = user.employee_id or user.student_id or user.username
        if ident and len(ident) >= 6:
            return ident[-6:], 'ident'
        return '123456', 'fallback'

    for user in UserProfile.objects.all():
        if user.role == 'admin' or user.is_superuser:
            user.set_password('admin123')
            user.must_change_password = False
            user.save()
            rule_counts['admin'] += 1
            continue
        pwd, kind = default_pwd(user)
        user.set_password(pwd)
        user.must_change_password = False
        user.save()
        rule_counts[kind] = rule_counts.get(kind, 0) + 1
    print(f'  密码重置完成: {rule_counts}')

    # ---------- 5. 重置 PostgreSQL 自增序列 ----------
    print('\n🔢 重置自增序列...')
    seq_models = [ClassInfo, UserProfile, LearningMaterial, MaterialInteraction,
                  PracticeScenario, PracticeTopic, PracticeRecord, LLMConfig]
    with connection.cursor() as cur:
        for m in seq_models:
            tbl = m._meta.db_table
            sql = (
                f"SELECT setval(pg_get_serial_sequence('{tbl}','id'), "
                f"COALESCE((SELECT MAX(id) FROM {tbl}), 1), true);"
            )
            cur.execute(sql)
    print('  ✅ 序列已重置')

    # ---------- 6. 汇总 + 样例账号 ----------
    print('\n' + '=' * 70)
    print('📊 迁移结果汇总:')
    print(f'  班级 ClassInfo        : {ClassInfo.objects.count()} 条')
    print(f'  用户 UserProfile      : {UserProfile.objects.count()} 条')
    print(f'    - admin             : {UserProfile.objects.filter(role="admin").count()}')
    print(f'    - teacher           : {UserProfile.objects.filter(role="teacher").count()}')
    print(f'    - student           : {UserProfile.objects.filter(role="student").count()}')
    print(f'  学习资料 LearningMaterial : {LearningMaterial.objects.count()} 条')
    print(f'  练习场景 PracticeScenario : {PracticeScenario.objects.count()} 条')
    print(f'  练习主题 PracticeTopic    : {PracticeTopic.objects.count()} 条')
    print(f'  练习记录 PracticeRecord   : {PracticeRecord.objects.count()} 条')
    print(f'  LLM 配置 LLMConfig       : {LLMConfig.objects.count()} 条')

    print('\n👤 样例账号（密码规则: 手机号后6位 / 标识符后6位 / 123456; 管理员=admin123）:')
    samples = (
        UserProfile.objects.filter(role='admin').first(),
        UserProfile.objects.filter(role='teacher').first(),
        UserProfile.objects.filter(role='student').first(),
    )
    for u in samples:
        if not u:
            continue
        pwd, _ = ('admin123', 'admin') if (u.role == 'admin' or u.is_superuser) else default_pwd(u)
        ident = u.employee_id or u.student_id or u.username
        print(f'  [{u.role:7s}] {u.real_name:8s}  标识符={ident:12s}  手机={u.phone or "无":14s}  密码={pwd}')


if __name__ == '__main__':
    migrate()
