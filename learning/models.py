from django.db import models
from django.conf import settings


class LearningMaterial(models.Model):
    """学习资料模型 - 增强版"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已下架'),
    ]
    
    CATEGORY_CHOICES = [
        ('basic', '基础入门'),
        ('intermediate', '进阶技巧'),
        ('advanced', '高级应用'),
        ('best_practices', '最佳实践'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    summary = models.TextField(blank=True, default='', verbose_name='摘要')
    content = models.TextField(verbose_name='内容')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='basic', 
        verbose_name='分类'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
        db_index=True
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_materials',
        verbose_name='作者'
    )
    
    cover_image = models.URLField(
        blank=True, 
        default='', 
        verbose_name='封面图片'
    )
    
    tags = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name='标签列表'
    )
    
    order_index = models.IntegerField(default=0, verbose_name='排序权重')
    view_count = models.PositiveIntegerField(default=0, verbose_name='阅读量')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    
    class Meta:
        ordering = ['-order_index', '-created_at']
        verbose_name = '学习资料'
        verbose_name_plural = '学习资料'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def reading_time(self):
        """计算阅读时间（按每分钟100字估算）"""
        minutes = len(self.content) // 100
        return max(1, minutes)
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    def increment_view_count(self):
        """增加阅读量"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def publish(self):
        """发布内容"""
        from django.utils import timezone
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
    
    def archive(self):
        """下架内容"""
        self.status = 'archived'
        self.save()
