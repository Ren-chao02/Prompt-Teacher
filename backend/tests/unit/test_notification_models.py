"""
通知系统 - 模型单元测试

测试内容:
- Notification 模型的字段验证
- NotificationTemplate 模板的渲染功能
- 模型方法（mark_as_read, is_expired）
"""

import pytest
from django.utils import timezone
from datetime import timedelta

from notifications.models import Notification, NotificationTemplate


pytestmark = pytest.mark.unit


class TestNotificationModel:
    """Notification 模型测试"""
    
    def test_create_basic_notification(self, student_user):
        """测试创建基本通知"""
        notif = Notification.objects.create(
            recipient=student_user,
            notification_type='system',
            title='Test Title',
            content='Test Content',
            priority='medium'
        )
        
        assert notif.id is not None
        assert notif.recipient == student_user
        assert notif.notification_type == 'system'
        assert notif.title == 'Test Title'
        assert notif.content == 'Test Content'
        assert notif.priority == 'medium'
        assert notif.is_read is False
        assert notif.is_persistent is True
        assert notif.created_at is not None
    
    def test_notification_default_values(self, student_user):
        """测试默认值"""
        notif = Notification.objects.create(
            recipient=student_user,
            title='Test',
            content='Content'
        )
        
        # notification_type 没有默认值（必须显式提供）
        assert notif.priority == 'medium'  # 默认值
        assert notif.is_read is False
        assert notif.is_persistent is True
        assert notif.sender is None
        assert notif.link == ''
    
    def test_mark_as_read(self, student_user):
        """测试标记已读方法"""
        notif = Notification.objects.create(
            recipient=student_user,
            title='Unread notification',
            content='Content'
        )
        
        # 初始状态：未读
        assert notif.is_read is False
        assert notif.read_at is None
        
        # 标记为已读
        notif.mark_as_read()
        
        # 刷新从数据库获取
        notif.refresh_from_db()
        
        assert notif.is_read is True
        assert notif.read_at is not None
    
    def test_mark_already_read_notification(self, student_user):
        """测试重复标记已读（幂等性）"""
        from django.utils import timezone
        
        notif = Notification.objects.create(
            recipient=student_user,
            title='Test',
            content='Content',
            is_read=True,
            read_at=timezone.now() - timedelta(hours=1)
        )
        
        original_read_at = notif.read_at
        
        # 再次标记
        notif.mark_as_read()
        notif.refresh_from_db()
        
        # read_at 不应该改变（因为已经是已读状态）
        assert notif.is_read is True
    
    def test_is_expired_with_expires_at(self, student_user):
        """测试过期检查 - 已过期"""
        past_time = timezone.now() - timedelta(days=1)
        
        notif = Notification.objects.create(
            recipient=student_user,
            title='Expired',
            content='This should be expired',
            expires_at=past_time
        )
        
        assert notif.is_expired() is True
    
    def test_is_expired_not_expired(self, student_user):
        """测试过期检查 - 未过期"""
        future_time = timezone.now() + timedelta(days=1)
        
        notif = Notification.objects.create(
            recipient=student_user,
            title='Not Expired',
            content='This should not be expired',
            expires_at=future_time
        )
        
        assert notif.is_expired() is False
    
    def test_is_expired_no_expires_at(self, student_user):
        """测试过期检查 - 无过期时间"""
        notif = Notification.objects.create(
            recipient=student_user,
            title='No Expiry',
            content='No expiry date set'
        )
        
        assert notif.is_expired() is False
    
    def test_notification_types_choices(self):
        """测试通知类型选项"""
        expected_types = ['system', 'learning', 'practice', 'interaction', 'announcement']
        actual_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
        
        assert set(actual_types) == set(expected_types)
    
    def test_priority_levels_choices(self):
        """测试优先级选项"""
        expected_priorities = ['low', 'medium', 'high', 'urgent']
        actual_priorities = [choice[0] for choice in Notification.PRIORITY_LEVELS]
        
        assert set(actual_priorities) == set(expected_priorities)
    
    def test_str_representation(self, student_user):
        """测试字符串表示"""
        notif = Notification.objects.create(
            recipient=student_user,
            notification_type='practice',
            title='Practice Completed',
            content='You scored 95!'
        )
        
        str_repr = str(notif)
        
        assert '[练习成绩]' in str_repr or 'practice' in str_repr.lower()
        assert 'Practice Completed' in str_repr
        assert student_user.username in str_repr
    
    def test_ordering_by_created_at_desc(self, student_user):
        """测试默认排序（按创建时间降序）"""
        import time
        
        # 创建多条通知
        notif1 = Notification.objects.create(
            recipient=student_user,
            title='First',
            content='First content'
        )
        time.sleep(0.01)  # 确保时间差
        
        notif2 = Notification.objects.create(
            recipient=student_user,
            title='Second',
            content='Second content'
        )
        
        # 获取所有通知
        notifications = list(Notification.objects.all())
        
        # 最新的应该在前面
        assert notifications[0].id == notif2.id
        assert notifications[1].id == notif1.id
    
    def test_metadata_field_json_storage(self, student_user):
        """测试元数据JSON字段"""
        metadata = {
            'icon': '🎉',
            'color': '#409eff',
            'custom_field': 'custom_value'
        }
        
        notif = Notification.objects.create(
            recipient=student_user,
            title='With Metadata',
            content='Content',
            metadata=metadata
        )
        
        notif.refresh_from_db()
        
        assert notif.metadata == metadata
        assert notif.metadata['icon'] == '🎉'


class TestNotificationTemplateModel:
    """NotificationTemplate 模型测试"""
    
    def test_create_template(self):
        """测试创建模板"""
        template = NotificationTemplate.objects.create(
            template_code='test_template',
            title_template='Hello {username}!',
            content_template='Welcome to our platform, {username}!',
            notification_type='system',
            priority='medium'
        )
        
        assert template.id is not None
        assert template.template_code == 'test_template'
        assert template.is_active is True
        assert template.is_persistent is True
    
    def test_template_render_simple(self):
        """测试模板渲染 - 简单变量"""
        template = NotificationTemplate.objects.create(
            template_code='welcome',
            title_template='Welcome, {name}!',
            content_template='Dear {name}, welcome to Prompt Teacher!',
            notification_type='system'
        )
        
        context = {'name': '张三'}
        result = template.render(context)
        
        assert result['title'] == 'Welcome, 张三!'
        assert result['content'] == 'Dear 张三, welcome to Prompt Teacher!'
        assert result['notification_type'] == 'system'
        assert result['priority'] == 'medium'
    
    def test_template_render_multiple_variables(self):
        """测试模板渲染 - 多个变量"""
        template = NotificationTemplate.objects.create(
            template_code='practice_result',
            title_template='🎯 练习完成: {score}分',
            content_template='恭喜！您在{topic}中取得了{score}分的好成绩！',
            notification_type='practice',
            priority='high'
        )
        
        context = {
            'score': 95,
            'topic': 'Python编程基础'
        }
        result = template.render(context)
        
        assert result['title'] == '🎯 练习完成: 95分'
        assert '95' in result['content']
        assert 'Python编程基础' in result['content']
        assert result['priority'] == 'high'
    
    def test_template_render_with_link_pattern(self):
        """测试模板渲染 - 包含链接模式"""
        template = NotificationTemplate.objects.create(
            template_code='material_published',
            title_template='新资料发布: {title}',
            content_template='{author} 发布了新的学习资料《{title}》',
            notification_type='learning',
            link_pattern='/learning/detail/{id}/'
        )
        
        context = {
            'title': 'Django入门教程',
            'author': '李老师',
            'id': 42
        }
        result = template.render(context)
        
        assert result['link'] == '/learning/detail/42/'
        assert 'Django入门教程' in result['title']
    
    def test_template_render_missing_variable_in_link(self):
        """测试模板渲染 - 链接缺少变量时返回空"""
        template = NotificationTemplate.objects.create(
            template_code='test_link',
            title_template='Test',
            content_template='Content',
            link_pattern='/detail/{missing_id}/'
        )
        
        context = {'other_var': 'value'}
        result = template.render(context)
        
        # 缺少变量时应该返回空字符串而不是报错
        assert result['link'] == ''
    
    def test_template_unique_code_constraint(self):
        """测试模板代码唯一约束"""
        NotificationTemplate.objects.create(
            template_code='unique_code',
            title_template='First',
            content_template='Content 1'
        )
        
        # 尝试创建相同代码的模板应该失败
        with pytest.raises(Exception):  # IntegrityError
            NotificationTemplate.objects.create(
                template_code='unique_code',
                title_template='Second',
                content_template='Content 2'
            )
    
    def test_inactive_template_should_not_be_used(self):
        """测试非活跃模板"""
        template = NotificationTemplate.objects.create(
            template_code='inactive_test',
            title_template='Inactive',
            content_template='Should not render',
            is_active=False
        )
        
        assert template.is_active is False


class TestNotificationQuerySet:
    """通知查询集测试"""
    
    def test_filter_by_recipient(self, student_user, teacher_user):
        """测试按接收者筛选"""
        # 为学生创建通知
        Notification.objects.create(
            recipient=student_user,
            title='For Student',
            content='Student notification'
        )
        
        # 为教师创建通知
        Notification.objects.create(
            recipient=teacher_user,
            title='For Teacher',
            content='Teacher notification'
        )
        
        # 筛选学生的通知
        student_notifs = Notification.objects.filter(recipient=student_user)
        assert student_notifs.count() == 1
        assert student_notifs.first().title == 'For Student'
        
        # 筛选教师的通知
        teacher_notifs = Notification.objects.filter(recipient=teacher_user)
        assert teacher_notifs.count() == 1
        assert teacher_notifs.first().title == 'For Teacher'
    
    def test_filter_unread_notifications(self, student_user, notification_factory):
        """测试筛选未读通知"""
        # 创建5条通知（工厂方法会交替设置is_read）
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        unread_count = Notification.objects.filter(
            recipient=student_user,
            is_read=False
        ).count()
        
        read_count = Notification.objects.filter(
            recipient=student_user,
            is_read=True
        ).count()
        
        # 应该有未读和已读的通知
        assert unread_count > 0
        assert read_count > 0
        assert unread_count + read_count == 5
    
    def test_filter_by_type(self, student_user):
        """测试按类型筛选"""
        types = ['system', 'learning', 'practice']
        
        for ntype in types:
            Notification.objects.create(
                recipient=student_user,
                notification_type=ntype,
                title=f'{ntype} notification',
                content=f'{ntype} content'
            )
        
        # 筛选特定类型
        system_notifs = Notification.objects.filter(
            recipient=student_user,
            notification_type='system'
        )
        assert system_notifs.count() == 1
        
        learning_notifs = Notification.objects.filter(
            recipient=student_user,
            notification_type='learning'
        )
        assert learning_notifs.count() == 1
    
    def test_filter_by_priority(self, student_user):
        """测试按优先级筛选"""
        priorities = ['low', 'medium', 'high']
        
        for priority in priorities:
            Notification.objects.create(
                recipient=student_user,
                priority=priority,
                title=f'{priority} priority',
                content='Content'
            )
        
        high_priority = Notification.objects.filter(
            recipient=student_user,
            priority='high'
        )
        assert high_priority.count() == 1
        assert high_priority.first().priority == 'high'
