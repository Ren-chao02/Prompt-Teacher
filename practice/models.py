from django.db import models
from django.contrib.auth.models import User


class PracticeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_records')
    user_prompt = models.TextField(verbose_name='用户提示词')
    system_prompt = models.TextField(verbose_name='系统提示词(场景)', default='')
    llm_response = models.TextField(verbose_name='大模型原始回复', blank=True)
    
    scores = models.JSONField(verbose_name='评分数据', default=dict)
    suggestions = models.TextField(verbose_name='修改建议', blank=True)
    overall_score = models.IntegerField(verbose_name='综合得分', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'
    
    def __str__(self):
        return f'{self.user.username} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'
