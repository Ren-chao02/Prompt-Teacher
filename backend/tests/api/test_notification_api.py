"""
通知系统 - API 集成测试（修正版）

测试内容:
- 认证和权限
- CRUD 操作
- 自定义 action (mark_read, mark_all_read, unread_count)
- 筛选、搜索、排序
- 批量操作

注意: API响应使用自定义包装格式 {code, message, data}
"""

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.api


class TestNotificationAuthentication:
    """通知API认证测试"""
    
    def test_unauthenticated_access_denied(self, api_client):
        """未认证用户无法访问通知列表"""
        url = reverse('notification-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_authenticated_access_allowed(self, student_client):
        """已认证用户可以访问通知列表"""
        url = reverse('notification-list')
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


class TestNotificationListAPI:
    """通知列表API测试"""
    
    def test_empty_notification_list(self, student_client):
        """空列表返回"""
        url = reverse('notification-list')
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        data = response.data['data']
        assert data['count'] == 0
        assert len(data['results']) == 0
    
    def test_list_notifications(self, student_user, student_client, notification_factory):
        """获取通知列表"""
        # 创建5条通知
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        url = reverse('notification-list')
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['count'] == 5
        assert len(data['results']) == 5
        
        # 验证返回字段
        notif = data['results'][0]
        required_fields = ['id', 'title', 'content', 'notification_type', 
                          'priority', 'is_read', 'created_at']
        for field in required_fields:
            assert field in notif, f"Missing field: {field}"
    
    def test_list_only_own_notifications(self, admin_client, student_user, 
                                        teacher_user, notification_factory):
        """只能看到自己的通知"""
        # 为学生创建3条通知
        notification_factory.create_multiple_notifications(student_user, count=3)
        
        # 为教师创建2条通知
        notification_factory.create_multiple_notifications(teacher_user, count=2)
        
        # 学生登录查看
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import AccessToken
        
        client = APIClient()
        token = AccessToken.for_user(student_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('notification-list')
        response = client.get(url)
        
        # 应该只看到学生的3条通知
        data = response.data['data']
        assert data['count'] == 3


class TestNotificationDetailAPI:
    """通知详情API测试"""
    
    def test_retrieve_own_notification(self, student_user, student_client, 
                                       notification_factory):
        """获取自己的通知详情"""
        notifications = notification_factory.create_multiple_notifications(
            student_user, count=1
        )
        notif = notifications[0]
        
        url = reverse('notification-detail', kwargs={'pk': notif.id})
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['id'] == notif.id
        assert data['title'] == notif.title
    
    def test_cannot_retrieve_others_notification(self, admin_user, admin_client,
                                                student_user, notification_factory):
        """不能获取他人的通知"""
        # 创建给学生的通知
        notifications = notification_factory.create_multiple_notifications(
            student_user, count=1
        )
        notif = notifications[0]
        
        # 管理员尝试访问（应该被过滤掉）
        url = reverse('notification-detail', kwargs={'pk': notif.id})
        response = admin_client.get(url)
        
        # 应该返回404（因为查询集已过滤）
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMarkAsReadAPI:
    """标记已读API测试"""
    
    def test_mark_single_as_read(self, student_user, student_client,
                                 notification_factory):
        """标记单条通知为已读"""
        # 创建未读通知
        notif = notification_factory.create_notification(
            recipient=student_user,
            is_read=False
        )
        
        url = reverse('notification-mark-read', kwargs={'pk': notif.id})
        response = student_client.put(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Notification marked as read'
        
        # 验证数据库状态
        notif.refresh_from_db()
        assert notif.is_read is True
        assert notif.read_at is not None
    
    def test_mark_already_read_notification(self, student_user, student_client,
                                           notification_factory):
        """重复标记已读通知"""
        notif = notification_factory.create_notification(
            recipient=student_user,
            is_read=True
        )
        
        url = reverse('notification-mark-read', kwargs={'pk': notif.id})
        response = student_client.put(url)
        
        # 应该仍然成功（幂等性）
        assert response.status_code == status.HTTP_200_OK


class TestMarkAllReadAPI:
    """批量标记已读API测试"""
    
    def test_mark_all_as_read(self, student_user, student_client,
                              notification_factory):
        """标记所有通知为已读"""
        # 创建5条未读通知
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        # 验证初始状态有未读通知
        from notifications.models import Notification
        unread_count = Notification.objects.filter(
            recipient=student_user,
            is_read=False
        ).count()
        assert unread_count > 0
        
        # 调用批量标记接口
        url = reverse('notification-mark-all-read')
        response = student_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'marked_count' in response.data
        
        # 验证所有通知都已读
        unread_count_after = Notification.objects.filter(
            recipient=student_user,
            is_read=False
        ).count()
        assert unread_count_after == 0
    
    def test_mark_all_read_when_all_already_read(self, student_user, student_client):
        """所有通知都已读时调用"""
        url = reverse('notification-mark-all-read')
        response = student_client.post(url)
        
        # 应该成功，但marked_count为0
        assert response.status_code == status.HTTP_200_OK
        assert response.data['marked_count'] == 0


class TestUnreadCountAPI:
    """未读数量统计API测试"""
    
    def test_get_unread_count(self, student_user, student_client,
                              notification_factory):
        """获取未读通知数量"""
        # 创建5条通知（工厂方法会交替设置is_read）
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        url = reverse('notification-unread-count')
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert 'total_unread' in data
        assert 'by_type' in data
        
        # 验证总数正确
        from notifications.models import Notification
        actual_unread = Notification.objects.filter(
            recipient=student_user,
            is_read=False
        ).count()
        assert data['total_unread'] == actual_unread
    
    def test_unread_count_by_type(self, student_user, student_client,
                                  notification_factory):
        """按类型统计未读数"""
        # 创建不同类型的通知
        notification_factory.create_multiple_notifications(student_user, count=10)
        
        url = reverse('notification-unread-count')
        response = student_client.get(url)
        
        data = response.data['data']
        by_type = data['by_type']
        
        # 验证各类型的计数
        total_by_type = sum(by_type.values())
        assert total_by_type == data['total_unread']


class TestNotificationFiltering:
    """通知筛选功能测试"""
    
    def test_filter_by_type(self, student_user, student_client, 
                            notification_factory):
        """按通知类型筛选"""
        # 创建多种类型的通知
        notification_factory.create_multiple_notifications(student_user, count=6)
        
        # 只筛选 system 类型
        url = reverse('notification-list') + '?notification_type=system'
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['data']['results']
        
        # 验证结果都是system类型
        for notif in results:
            assert notif['notification_type'] == 'system'
    
    def test_filter_by_is_read(self, student_user, student_client,
                               notification_factory):
        """按已读/未读筛选"""
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        # 只看未读的
        url = reverse('notification-list') + '?is_read=false'
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['data']['results']
        for notif in results:
            assert notif['is_read'] is False
    
    def test_filter_by_priority(self, student_user, student_client,
                                notification_factory):
        """按优先级筛选"""
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        # 只看高优先级
        url = reverse('notification-list') + '?priority=high'
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['data']['results']
        for notif in results:
            assert notif['priority'] in ['high', 'urgent']
    
    def test_search_by_title(self, student_user, student_client,
                             notification_factory):
        """按标题搜索"""
        notification_factory.create_notification(
            recipient=student_user,
            title='Important Announcement',
            content='Content'
        )
        notification_factory.create_notification(
            recipient=student_user,
            title='Regular Message',
            content='Other content'
        )
        
        # 搜索 "Announcement"
        url = reverse('notification-list') + '?search=Announcement'
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['data']['results']
        assert len(results) >= 1
        assert all('Announcement' in n['title'] or 'Announcement' in n['content']
                   for n in results)
    
    def test_ordering_by_created_at(self, student_user, student_client,
                                    notification_factory):
        """按创建时间排序"""
        import time
        
        notification_factory.create_multiple_notifications(student_user, count=5)
        
        # 默认降序排列（最新的在前）
        url = reverse('notification-list') + '?ordering=-created_at'
        response = student_client.get(url)
        
        results = response.data['data']['results']
        if len(results) >= 2:
            assert results[0]['created_at'] >= results[1]['created_at']


class TestSendNotificationAPI:
    """发送通知API测试（管理员/教师权限）"""
    
    def test_admin_can_send_notification(self, admin_client, student_user):
        """管理员可以发送通知"""
        url = reverse('notification-send')
        data = {
            'recipient_id': student_user.id,
            'title': 'Admin Notice',
            'content': 'This is an admin notice',
            'notification_type': 'system',
            'priority': 'high'
        }
        
        response = admin_client.post(url, data=data)
        
        # 验证数据库中存在
        from notifications.models import Notification
        assert Notification.objects.filter(
            recipient=student_user,
            title='Admin Notice'
        ).exists()
    
    def test_student_cannot_send_notification(self, student_client, admin_user):
        """学生无权发送通知"""
        url = reverse('notification-send')
        data = {
            'recipient_id': admin_user.id,
            'title': 'Student trying to send',
            'content': 'Should fail',
            'notification_type': 'system'
        }
        
        response = student_client.post(url, data=data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_send_with_template(self, admin_client, student_user):
        """使用模板发送通知"""
        from notifications.models import NotificationTemplate
        
        # 先创建模板
        template = NotificationTemplate.objects.create(
            template_code='test_template',
            title_template='Hello {name}!',
            content_template='Welcome {name} to the platform',
            notification_type='learning'
        )
        
        url = reverse('notification-send')
        data = {
            'recipient_id': student_user.id,
            'template_code': template.template_code,
            'context': {'name': 'TestUser'}
        }
        
        response = admin_client.post(url, data=data)


class TestPagination:
    """分页功能测试"""
    
    def test_default_pagination(self, student_user, student_client,
                                notification_factory):
        """默认分页大小"""
        # 创建超过默认分页数量的通知
        notification_factory.create_multiple_notifications(student_user, count=25)
        
        url = reverse('notification-list')
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data
        
        # 默认每页20条
        assert len(data['results']) <= 20
    
    def test_custom_page_size(self, student_user, student_client,
                              notification_factory):
        """自定义每页大小"""
        notification_factory.create_multiple_notifications(student_user, count=15)
        
        url = reverse('notification-list') + '?page_size=5'
        response = student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert len(data['results']) <= 5


class TestDeleteNotification:
    """删除通知API测试"""
    
    def test_delete_own_notification(self, student_user, student_client,
                                     notification_factory):
        """删除自己的通知"""
        notif = notification_factory.create_notification(recipient=student_user)
        
        url = reverse('notification-detail', kwargs={'pk': notif.id})
        response = student_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # 验证已删除
        from notifications.models import Notification
        assert not Notification.objects.filter(id=notif.id).exists()
