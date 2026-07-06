from rest_framework import serializers
from ..models import Notification, NotificationTemplate
from users.models import UserProfile


class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息简化序列化器"""

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'avatar']


class NotificationSerializer(serializers.ModelSerializer):
    """通知列表序列化器"""

    sender_info = UserInfoSerializer(source='sender', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'content',
            'priority',
            'is_read',
            'is_persistent',
            'sender_info',
            'link',
            'created_at',
            'read_at',
            'metadata',
            'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'read_at', 'time_ago']

    def get_time_ago(self, obj):
        """计算相对时间"""
        from django.utils import timezone
        import math

        if not obj.created_at:
            return ''

        now = timezone.now()
        diff = now - obj.created_at
        total_seconds = diff.total_seconds()

        if total_seconds < 60:
            return '刚刚'
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f'{minutes}分钟前'
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f'{hours}小时前'
        elif total_seconds < 604800:
            days = int(total_seconds / 86400)
            return f'{days}天前'
        else:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')


class NotificationDetailSerializer(NotificationSerializer):
    """通知详情序列化器 (包含完整内容)"""

    class Meta(NotificationSerializer.Meta):
        fields = NotificationSerializer.Meta.fields + ['object_id', 'expires_at']


class UnreadCountSerializer(serializers.Serializer):
    """未读数量响应"""

    count = serializers.IntegerField()
    breakdown = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="各类型的未读数量: {'system': 2, 'learning': 5, ...}"
    )


class SendNotificationSerializer(serializers.Serializer):
    """发送通知请求"""

    recipient_id = serializers.IntegerField(required=False, help_text="单个接收者ID")
    recipients = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="多个接收者ID列表"
    )
    template_code = serializers.CharField(
        required=False,
        max_length=50,
        help_text="模板代码"
    )
    context = serializers.DictField(
        required=False,
        help_text="模板变量"
    )
    title = serializers.CharField(
        required=False,
        max_length=200,
        help_text="自定义标题"
    )
    content = serializers.CharField(
        required=False,
        help_text="自定义内容"
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        required=False,
        help_text="通知类型"
    )
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_LEVELS,
        default='medium',
        help_text="优先级"
    )
    link = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="跳转链接"
    )
    is_persistent = serializers.BooleanField(
        default=True,
        help_text="是否持久化保存"
    )
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="过期时间"
    )

    def validate(self, data):
        """
        验证: 必须提供模板 或 直接提供内容
              必须提供接收者 (recipient_id 或 recipients)
        """
        has_template = 'template_code' in data and data['template_code']
        has_content = ('title' in data and data['title']) and \
                     ('content' in data and data['content'])

        if not has_template and not has_content:
            raise serializers.ValidationError({
                "non_field_errors": "必须提供 template_code 或 (title + content)"
            })

        has_recipient = 'recipient_id' in data or 'recipients' in data

        if not has_recipient:
            raise serializers.ValidationError({
                "non_field_errors": "必须提供 recipient_id 或 recipients"
            })

        return data


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """通知模板序列化器"""

    class Meta:
        model = NotificationTemplate
        fields = [
            'id',
            'template_code',
            'title_template',
            'content_template',
            'notification_type',
            'priority',
            'is_active',
            'is_persistent',
            'icon',
            'link_pattern',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
