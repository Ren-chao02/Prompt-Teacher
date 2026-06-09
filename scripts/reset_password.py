"""
重置教师/学生密码为手机号后6位
用法: python reset_password.py [--role teacher|student|all] [--identifier 工号/学号]
"""
import os
import sys
import django
import argparse

sys.path.insert(0, '/home/mjl/Prompt Teacher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
django.setup()

from users.models import UserProfile


def get_default_password(user):
    """获取用户默认密码：手机号后6位，无手机号则用123456"""
    if user.phone and len(user.phone) >= 6:
        return user.phone[-6:]
    ident = user.employee_id or user.student_id or user.username
    return ident[-6:] if len(ident) >= 6 else '123456'


def reset_password(role='all', identifier=None):
    queryset = UserProfile.objects.filter(is_active=True)

    if role != 'all':
        queryset = queryset.filter(role=role)

    if identifier:
        if role == 'teacher':
            queryset = queryset.filter(employee_id=identifier)
        elif role == 'student':
            queryset = queryset.filter(student_id=identifier)
        else:
            queryset = queryset.filter(username=identifier)

    count = queryset.count()
    if count == 0:
        print("❌ 没有找到匹配的用户")
        return

    print(f"\n找到 {count} 个用户，密码将重置为: 手机号后6位 (无手机号则用标识符后6位)")
    print("-" * 60)

    for user in queryset:
        pwd = get_default_password(user)
        user.set_password(pwd)
        user.must_change_password = True
        user.save()

        role_label = {'admin': '管理员', 'teacher': '教师', 'student': '学生'}.get(user.role, user.role)
        ident = user.employee_id or user.student_id or user.username
        phone_display = f"手机:{user.phone}" if user.phone else "无手机号"
        print(f"✅ {role_label}: {user.real_name or ident} ({ident}) → 密码: {pwd} [{phone_display}]")

    print("-" * 60)
    print(f"已完成 {count} 个用户密码重置")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='重置用户密码')
    parser.add_argument('--role', choices=['teacher', 'student', 'admin', 'all'], default='all',
                        help='角色筛选 (默认: all)')
    parser.add_argument('--identifier', help='工号/学号/用户名 (可选)')
    args = parser.parse_args()

    reset_password(args.role, args.identifier)
