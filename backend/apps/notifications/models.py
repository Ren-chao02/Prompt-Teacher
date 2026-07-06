from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Notification(models.Model):
    """通知主表 - 存储所有持久化通知"""

    NOTIFICATION_TYPES = [
        ('system', '系统通知'),
        ('learning', '学习任务'),
        ('practice', '练习成绩'),
        ('interaction', '互动消息'),
        ('announcement', '公告'),
    ]

    PRIORITY_LEVELS = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    id = models.BigAutoField(primary_key=True)

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        db_index=True,
        verbose_name='通知类型'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='通知标题'
    )

    content = models.TextField(
        verbose_name='通知内容',
        help_text='支持HTML格式'
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='发送者'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        db_index=True,
        verbose_name='优先级'
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='是否已读'
    )

    is_persistent = models.BooleanField(
        default=True,
        verbose_name='是否持久化',
        help_text='True: 保存到数据库; False: 仅实时推送'
    )

    link = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='跳转链接',
        help_text='点击通知后跳转的页面'
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='关联对象ID',
        help_text='关联的学习资料/练习记录等'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='关联对象类型'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='创建时间'
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='阅读时间'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='过期时间',
        help_text='过期后自动标记已读并归档'
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='元数据',
        help_text='存储额外信息，如图标、颜色等'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['recipient', 'notification_type', '-created_at']),
            models.Index(fields=['recipient', 'priority', 'is_read']),
        ]
        verbose_name = '通知'
        verbose_name_plural = '通知列表'

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} -> {self.recipient.username}"

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def is_expired(self):
        """检查是否已过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class NotificationTemplate(models.Model):
    """通知模板 - 预定义的通知格式"""

    TEMPLATE_TYPES = [
        ('practice_completed', '练习完成'),
        ('practice_score_high', '成绩优秀'),
        ('practice_score_low', '成绩警告'),
        ('material_published', '资料发布'),
        ('assignment_due', '作业即将到期'),
        ('assignment_overdue', '作业已逾期'),
        ('system_maintenance', '系统维护'),
        ('new_feature', '新功能发布'),
        ('mentioned', '被@提及'),
        ('comment_replied', '评论回复'),
    ]

    id = models.BigAutoField(primary_key=True)

    template_code = models.CharField(
        max_length=50,
        unique=True,
        choices=[(t[0], t[1]) for t in TEMPLATE_TYPES],
        verbose_name='模板代码'
    )

    title_template = models.CharField(
        max_length=200,
        verbose_name='标题模板',
        help_text='使用 {variable} 占位符'
    )

    content_template = models.TextField(
        verbose_name='内容模板',
        help_text='支持 {variable} 和 HTML'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=Notification.NOTIFICATION_TYPES,
        verbose_name='通知类型'
    )

    priority = models.CharField(
        max_length=10,
        choices=Notification.PRIORITY_LEVELS,
        default='medium',
        verbose_name='默认优先级'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )

    is_persistent = models.BooleanField(
        default=True,
        verbose_name='是否持久化'
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='图标',
        help_text='Element Plus 图标名称或emoji'
    )

    link_pattern = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='链接模式',
        help_text='使用 {id} 等占位符生成链接'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'

    def __str__(self):
        return f"[{self.template_code}] {self.title_template}"

    def render(self, context: dict) -> dict:
        """
        渲染模板，返回标题和内容

        Args:
            context: 变量字典，如 {'username': '张三', 'score': 95}

        Returns:
            {'title': '...', 'content': '...', ...}
        """
        title = self.title_template.format(**context)
        content = self.content_template.format(**context)

        link = ''
        if self.link_pattern:
            try:
                link = self.link_pattern.format(**context)
            except KeyError:
                link = ''

        return {
            'title': title,
            'content': content,
            'link': link,
            'icon': self.icon,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'is_persistent': self.is_persistent
        }
