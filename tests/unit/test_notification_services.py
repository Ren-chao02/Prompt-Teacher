"""
通知系统 - 服务层单元测试（修正版）

测试内容:
- NotificationService 核心方法（匹配实际实现）
- 通知创建和发送逻辑
- 模板渲染功能
- 批量操作
- WebSocket推送（模拟）
"""

import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta

pytestmark = pytest.mark.unit


class TestNotificationServiceCreate:
    """NotificationService.create_notification 测试"""
    
    def test_create_basic_notification(self, student_user):
        """创建基本通知"""
        from notifications.services.notification_service import NotificationService
        
        notif = NotificationService.create_notification(
            recipient=student_user,
            title='Test Title',
            content='Test Content',
            notification_type='system'
        )
        
        assert notif is not None
        assert notif.title == 'Test Title'
        assert notif.content == 'Test Content'
        assert notif.notification_type == 'system'
        assert notif.recipient == student_user
        assert notif.is_read is False
    
    def test_create_with_all_parameters(self, student_user, admin_user):
        """创建包含所有参数的通知"""
        from notifications.services.notification_service import NotificationService
        
        future_time = timezone.now() + timedelta(days=7)
        
        notif = NotificationService.create_notification(
            recipient=student_user,
            title='Full Parameter Notification',
            content='<p>HTML content</p>',
            notification_type='practice',
            sender=admin_user,
            priority='high',
            is_persistent=True,
            link='/practice/record/123/',
            object_id=123,
            metadata={'score': 95, 'topic': 'Python'},
            expires_at=future_time
        )
        
        assert notif.sender == admin_user
        assert notif.priority == 'high'
        assert notif.link == '/practice/record/123/'
        assert notif.object_id == 123
        assert notif.metadata['score'] == 95
        assert notif.expires_at is not None
        assert notif.is_expired() is False
    
    def test_create_non_persistent_notification_returns_none(self, student_user):
        """创建非持久化通知返回None（不保存到数据库）"""
        from notifications.services.notification_service import NotificationService
        
        result = NotificationService.create_notification(
            recipient=student_user,
            title='Temporary',
            content='Will not be saved to DB',
            notification_type='system',
            is_persistent=False
        )
        
        # 非持久化通知应该返回None
        assert result is None


class TestNotificationServiceSendToUser:
    """NotificationService.send_to_user 测试"""
    
    def test_send_without_template(self, student_user):
        """不使用模板发送通知"""
        from notifications.services.notification_service import NotificationService
        
        result = NotificationService.send_to_user(
            user=student_user,
            title='Direct Send',
            content='This is a direct notification',
            notification_type='learning'
        )
        
        assert result['success'] is True
        assert result['notification_id'] is not None
    
    @patch('notifications.services.notification_service.NotificationService._push_to_user')
    def test_send_triggers_websocket(self, mock_ws_push, student_user):
        """发送通知时触发WebSocket推送"""
        from notifications.services.notification_service import NotificationService
        
        NotificationService.send_to_user(
            user=student_user,
            title='WS Test',
            content='Should trigger WS',
            notification_type='system'
        )
        
        # 验证WebSocket方法被调用
        assert mock_ws_push.called
    
    def test_send_with_template(self, student_user):
        """使用模板发送通知"""
        from notifications.models import NotificationTemplate
        from notifications.services.notification_service import NotificationService
        
        # 创建模板
        template = NotificationTemplate.objects.create(
            template_code='welcome',
            title_template='Welcome {name}!',
            content_template='Hello {name}, welcome!',
            notification_type='system'
        )
        
        result = NotificationService.send_to_user(
            user=student_user,
            template_code='welcome',
            context={'name': '张三'}
        )
        
        assert result['success'] is True
        assert result['notification_id'] is not None
        
        # 验证数据库中存在该通知
        from notifications.models import Notification
        notif = Notification.objects.get(id=result['notification_id'])
        assert '张三' in notif.title
        assert '张三' in notif.content


class TestNotificationServiceBroadcast:
    """NotificationService.broadcast 测试"""
    
    def test_broadcast_to_multiple_users(self, sample_users):
        """向多个用户广播通知"""
        from notifications.services.notification_service import NotificationService
        
        results = NotificationService.broadcast(
            recipients=sample_users[:3],
            title='Broadcast Message',
            content='This goes to everyone',
            notification_type='announcement',
            priority='urgent'
        )
        
        assert len(results) == 3
        for result in results:
            assert result['success'] is True
            assert result['notification_id'] is not None
    
    def test_broadcast_empty_list(self):
        """空接收者列表"""
        from notifications.services.notification_service import NotificationService
        
        results = NotificationService.broadcast(
            recipients=[],
            title='No recipients',
            content='Should handle gracefully',
            notification_type='system'
        )
        
        assert len(results) == 0


class TestNotificationServiceMarkRead:
    """标记已读相关方法测试"""
    
    def test_mark_as_read_safe(self, student_user, notification_factory):
        """通过ID安全标记已读"""
        from notifications.services.notification_service import NotificationService
        
        notif = notification_factory.create_notification(
            recipient=student_user,
            is_read=False
        )
        
        result = NotificationService.mark_as_read_safe(notif.id, student_user)
        
        assert result is not None
        assert result.is_read is True
        assert result.read_at is not None
    
    def test_mark_nonexistent_notification(self, student_user):
        """标记不存在的通知"""
        from notifications.services.notification_service import NotificationService
        
        result = NotificationService.mark_as_read_safe(99999, student_user)
        
        assert result is None
    
    def test_mark_all_as_read_for_user(self, student_user, notification_factory):
        """为用户标记所有通知已读"""
        from notifications.services.notification_service import NotificationService
        
        # 创建5条未读通知
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        marked_count = NotificationService.mark_all_as_read(student_user)
        
        assert marked_count > 0
        
        # 验证所有通知都已读
        from notifications.models import Notification
        unread_count = Notification.objects.filter(
            recipient=student_user,
            is_read=False
        ).count()
        assert unread_count == 0


class TestNotificationServiceGetUnreadCount:
    """未读数量统计测试"""
    
    def test_get_unread_count(self, student_user, notification_factory):
        """获取未读总数"""
        from notifications.services.notification_service import NotificationService
        
        # 创建5条通知
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        total_unread = NotificationService.get_unread_count(student_user)
        
        assert isinstance(total_unread, int)
        assert total_unread > 0
    
    def test_get_unread_count_by_type(self, student_user, notification_factory):
        """按类型获取未读数"""
        from notifications.services.notification_service import NotificationService
        
        # 创建不同类型的通知
        notification_factory.create_multiple_notifications(student_user, count=10)
        
        by_type = NotificationService.get_unread_count_by_type(student_user)
        
        assert isinstance(by_type, dict)
        assert len(by_type) > 0
        
        # 各类型总和应等于总未读数
        total_unread = NotificationService.get_unread_count(student_user)
        sum_by_type = sum(by_type.values())
        assert sum_by_type == total_unread
    
    def test_get_unread_count_no_notifications(self, student_user):
        """无通知时的统计"""
        from notifications.services.notification_service import NotificationService
        
        total_unread = NotificationService.get_unread_count(student_user)
        by_type = NotificationService.get_unread_count_by_type(student_user)
        
        assert total_unread == 0
        assert by_type == {}


class TestNotificationServiceQuery:
    """查询方法测试（使用ORM直接查询）"""
    
    def test_query_user_notifications(self, student_user, notification_factory):
        """获取用户通知列表"""
        # 创建10条通知
        notification_factory.create_multiple_notifications(student_user, count=10)
        
        from notifications.models import Notification
        notifications = Notification.objects.filter(recipient=student_user).order_by('-created_at')[:5]
        
        assert len(notifications) <= 5
    
    def test_filter_by_type(self, student_user, notification_factory):
        """按类型筛选"""
        # 创建多种类型的通知
        notification_factory.create_multiple_notifications(student_user, count=8)
        
        from notifications.models import Notification
        system_notifs = Notification.objects.filter(
            recipient=student_user,
            notification_type='system'
        )
        
        for notif in system_notifs:
            assert notif.notification_type == 'system'


class TestNotificationServiceErrorHandling:
    """错误处理测试"""
    
    def test_create_notification_missing_required_params(self, student_user):
        """缺少必需参数时创建失败"""
        from notifications.services.notification_service import NotificationService
        
        with pytest.raises(TypeError):  # 缺少 notification_type
            NotificationService.create_notification(
                recipient=student_user,
                title='Test',
                content='Content'
            )
    
    def test_send_with_invalid_template_code(self, student_user):
        """无效的模板代码"""
        from notifications.services.notification_service import NotificationService
        
        with pytest.raises(ValueError, match='not found or inactive'):
            NotificationService.send_to_user(
                user=student_user,
                template_code='nonexistent_template'
            )


class TestNotificationCleanup:
    """通知清理测试"""
    
    def test_cleanup_expired_notifications(self, student_user, notification_factory):
        """清理过期通知（标记为已读）"""
        from notifications.services.notification_service import NotificationService
        from django.utils import timezone
        from datetime import timedelta
        from notifications.models import Notification
        
        # 创建过期通知
        past_time = timezone.now() - timedelta(days=1)
        expired_notif = notification_factory.create_notification(
            recipient=student_user,
            title='Expired',
            notification_type='system',
            expires_at=past_time
        )
        
        # 创建未过期通知
        valid_notif = notification_factory.create_notification(
            recipient=student_user,
            title='Valid',
            notification_type='system'
        )
        
        cleaned_count = NotificationService.cleanup_expired_notifications()
        
        assert cleaned_count >= 1
        
        # 过期通知应被标记为已读（不是删除）
        expired_notif.refresh_from_db()
        assert expired_notif.is_read is True
        
        # 未过期的应该保持不变
        valid_notif.refresh_from_db()
        assert valid_notif.is_read is False
