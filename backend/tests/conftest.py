"""
测试配置文件 - 全局Fixtures

提供:
- 测试用户（admin/teacher/student）
- 认证客户端
- 测试数据工厂
- 数据库清理
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """为所有测试启用数据库访问"""
    pass


@pytest.fixture
def api_client():
    """未认证的API客户端"""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """管理员用户"""
    return User.objects.create_user(
        username='admin_test',
        password='testpass123',
        email='admin@test.com',
        role='admin',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def teacher_user(db):
    """教师用户"""
    return User.objects.create_user(
        username='teacher_test',
        password='testpass123',
        email='teacher@test.com',
        role='teacher'
    )


@pytest.fixture
def student_user(db):
    """学生用户"""
    return User.objects.create_user(
        username='student_test',
        password='testpass123',
        email='student@test.com',
        role='student'
    )


@pytest.fixture
def admin_client(admin_user):
    """已认证的管理员API客户端"""
    client = APIClient()
    token = AccessToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    client.user = admin_user
    return client


@pytest.fixture
def teacher_client(teacher_user):
    """已认证的教师API客户端"""
    client = APIClient()
    token = AccessToken.for_user(teacher_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    client.user = teacher_user
    return client


@pytest.fixture
def student_client(student_user):
    """已认证的学生API客户端"""
    client = APIClient()
    token = AccessToken.for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    client.user = student_user
    return client


@pytest.fixture
def sample_users(db):
    """创建多个测试用户"""
    users = []
    
    # 创建3个学生
    for i in range(1, 4):
        user = User.objects.create_user(
            username=f'student_{i}',
            password='testpass123',
            email=f'student{i}@test.com',
            role='student'
        )
        users.append(user)
    
    # 创建2个教师
    for i in range(1, 3):
        user = User.objects.create_user(
            username=f'teacher_{i}',
            password='testpass123',
            email=f'teacher{i}@test.com',
            role='teacher'
        )
        users.append(user)
    
    return users


class NotificationTestDataFactory:
    """通知测试数据工厂"""
    
    @staticmethod
    def create_notification(recipient, **kwargs):
        from notifications.models import Notification
        
        defaults = {
            'notification_type': 'system',
            'title': 'Test notification',
            'content': 'This is a test notification content',
            'priority': 'medium',
            'is_read': False,
            'sender': None,
        }
        defaults.update(kwargs)
        
        return Notification.objects.create(
            recipient=recipient,
            **defaults
        )
    
    @staticmethod
    def create_multiple_notifications(user, count=5, **kwargs):
        """创建多条测试通知"""
        notifications = []
        
        types = ['system', 'learning', 'practice', 'interaction']
        priorities = ['low', 'medium', 'high']
        
        for i in range(count):
            notif = NotificationTestDataFactory.create_notification(
                recipient=user,
                title=f'Test Notification #{i+1}',
                content=f'Content for notification #{i+1} with some details',
                notification_type=types[i % len(types)],
                priority=priorities[i % len(priorities)],
                is_read=(i % 2 == 0),  # 奇数未读，偶数已读
                **kwargs
            )
            notifications.append(notif)
        
        return notifications


@pytest.fixture
def notification_factory():
    """通知数据工厂fixture"""
    return NotificationTestDataFactory


@pytest.fixture
def auth_tokens(admin_user, teacher_user, student_user):
    """返回所有角色的JWT Token字典"""
    def get_token(user):
        return str(AccessToken.for_user(user))
    
    return {
        'admin': get_token(admin_user),
        'teacher': get_token(teacher_user),
        'student': get_token(student_user),
    }
