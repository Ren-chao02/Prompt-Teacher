from django.db import models


class LearningMaterial(models.Model):
    CATEGORY_CHOICES = [
        ('basic', '基础入门'),
        ('intermediate', '进阶技巧'),
        ('advanced', '高级应用'),
        ('best_practices', '最佳实践'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='basic', verbose_name='分类')
    order_index = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['order_index', '-created_at']
        verbose_name = '学习资料'
        verbose_name_plural = '学习资料'
    
    def __str__(self):
        return self.title
    
    @property
    def reading_time(self):
        """计算阅读时间（按每分钟100字估算）"""
        minutes = len(self.content) // 100
        return max(1, minutes)  # 至少显示1分钟
