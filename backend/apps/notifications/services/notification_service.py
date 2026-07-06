from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from typing import List, Optional, Dict, Any
from ..models import Notification, NotificationTemplate


class NotificationService:
    """通知服务 - 封装所有通知相关的业务逻辑"""

    @classmethod
    def create_notification(
        cls,
        recipient,
        title: str,
        content: str,
        notification_type: str,
        sender=None,
        priority: str = 'medium',
        is_persistent: bool = True,
        link: str = '',
        object_id: int = None,
        content_type_str: str = None,
        metadata: dict = None,
        expires_at = None
    ) -> Optional[Notification]:
        """
        创建单条通知（保存到数据库）

        Args:
            recipient: User实例 (接收者)
            title: 通知标题
            content: 通知内容
            notification_type: 通知类型 (system/learning/practice/interaction/announcement)
            sender: User实例 (发送者，可选)
            priority: 优先级 (low/medium/high/urgent)
            is_persistent: 是否持久化保存
            link: 跳转链接
            object_id: 关联对象ID
            content_type_str: 关联对象类型字符串 (如 'practice.practicerecord')
            metadata: 元数据字典
            expires_at: 过期时间

        Returns:
            Notification实例 或 None(如果不持久化)
        """
        if not is_persistent:
            return None

        ct = None
        if content_type_str and object_id:
            try:
                app_label, model = content_type_str.split('.')
                ct = ContentType.objects.get(app_label=app_label, model=model)
            except Exception as e:
                print(f'[Notification] Failed to get ContentType for {content_type_str}: {e}')

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            content=content,
            notification_type=notification_type,
            sender=sender,
            priority=priority,
            is_persistent=is_persistent,
            link=link,
            object_id=object_id,
            content_type=ct,
            metadata=metadata or {},
            expires_at=expires_at
        )

        return notification

    @classmethod
    def send_to_user(
        cls,
        user,
        template_code: str = None,
        context: dict = None,
        **kwargs
    ) -> dict:
        """
        向单个用户发送通知（数据库 + WebSocket推送）

        使用模板方式:
            NotificationService.send_to_user(
                user=user,
                template_code='practice_completed',
                context={'score': 85}
            )

        直接指定内容:
            NotificationService.send_to_user(
                user=user,
                title='自定义标题',
                content='自定义内容',
                notification_type='system'
            )

        Args:
            user: 接收通知的User实例
            template_code: 模板代码（可选）
            context: 模板变量字典
            **kwargs: 直接指定的参数（title, content等）

        Returns:
            {'success': bool, 'notification_id': int or None}
        """
        # 如果使用模板，先渲染模板
        if template_code:
            try:
                template = NotificationTemplate.objects.get(
                    template_code=template_code,
                    is_active=True
                )
                rendered = template.render(context or {})

                # 合并渲染结果到kwargs（只保留create_notification接受的参数）
                allowed_params = {
                    'title', 'content', 'notification_type', 'sender',
                    'priority', 'is_persistent', 'link', 'object_id',
                    'content_type_str', 'metadata', 'expires_at'
                }
                filtered_rendered = {k: v for k, v in rendered.items() if k in allowed_params}
                kwargs.update(filtered_rendered)

            except NotificationTemplate.DoesNotExist:
                raise ValueError(f'Notification template "{template_code}" not found or inactive')

        # 验证必要字段
        if not all(k in kwargs for k in ['title', 'content', 'notification_type']):
            raise ValueError('Must provide title, content and notification_type')

        # 创建数据库记录
        notification = cls.create_notification(
            recipient=user,
            **kwargs
        )

        # 构造WebSocket消息payload
        payload = {
            'id': notification.id if notification else None,
            'title': kwargs.get('title', ''),
            'content': kwargs.get('content', ''),
            'notification_type': kwargs.get('notification_type', 'system'),
            'priority': kwargs.get('priority', 'medium'),
            'link': kwargs.get('link', ''),
            'metadata': kwargs.get('metadata', {}),
            'created_at': notification.created_at.isoformat() if notification else timezone.now().isoformat()
        }

        # WebSocket实时推送
        try:
            cls._push_to_user(user, payload)
        except Exception as e:
            # WebSocket推送失败不影响主流程（已保存到数据库）
            print(f'[Notification] WebSocket push failed: {e}')

        return {
            'success': True,
            'notification_id': notification.id if notification else None
        }

    @classmethod
    def broadcast(cls, recipients: List, **kwargs) -> List[dict]:
        """
        向多个用户批量发送通知

        Args:
            recipients: User实例列表
            **kwargs: 与send_to_user相同的参数

        Returns:
            结果列表 [{'success': True, ...}, ...]
        """
        results = []

        for user in recipients:
            try:
                result = cls.send_to_user(user=user, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'user_id': user.id
                })

        return results

    @classmethod
    def _push_to_user(cls, user, payload: dict):
        """
        通过WebSocket向用户推送消息

        内部方法，不直接调用

        Args:
            user: 目标User实例
            payload: 消息内容字典
        """
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()

            # 发送到用户的专属channel group
            group_name = f'user_{user.id}'

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notify',
                    'message': {
                        'type': 'new_notification',
                        'payload': payload,
                        'timestamp': timezone.now().isoformat()
                    }
                }
            )

        except ImportError:
            # channels未安装时跳过WebSocket推送
            print('[Notification] Django Channels not installed, skipping WebSocket push')
        except Exception as e:
            # 其他错误记录日志但不中断流程
            print(f'[Notification] Failed to push via WebSocket: {e}')

    @classmethod
    def get_unread_count(cls, user) -> int:
        """获取用户的未读通知数量"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()

    @classmethod
    def get_unread_count_by_type(cls, user) -> Dict[str, int]:
        """获取各类型的未读数量"""
        from django.db.models import Count

        result = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).values('notification_type').annotate(count=Count('id'))

        return {item['notification_type']: item['count'] for item in result}

    @classmethod
    def mark_as_read_safe(cls, notification_id: int, user):
        """
        安全标记已读（使用select_for_update避免竞态）

        Args:
            notification_id: 通知ID
            user: 用户实例

        Returns:
            Notification实例 或 None
        """
        from django.db import transaction

        with transaction.atomic():
            try:
                notification = Notification.objects.select_for_update().get(
                    id=notification_id,
                    recipient_id=user.id
                )
                notification.mark_as_read()
                return notification
            except Notification.DoesNotExist:
                return None

    @classmethod
    def mark_all_as_read(cls, user) -> int:
        """
        标记用户的所有通知为已读

        Args:
            user: 用户实例

        Returns:
            更新的通知数量
        """
        now = timezone.now()
        count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(is_read=True, read_at=now)

        return count

    @classmethod
    def cleanup_expired_notifications(cls) -> int:
        """
        清理过期通知（标记为已读）

        可通过定时任务调用

        Returns:
            处理的通知数量
        """
        now = timezone.now()
        count = Notification.objects.filter(
            expires_at__lt=now,
            is_read=False
        ).update(is_read=True, read_at=now)

        return count
