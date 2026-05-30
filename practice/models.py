from django.db import models
from django.contrib.auth.models import User


class PracticeScenario(models.Model):
    SCENARIO_CHOICES = [
        ('coding_quality', '编程与代码质量'),
        ('writing_creation', '提炼（提炼、文案、创作）'),
        ('data_analysis', '数据分析与数据可视化'),
        ('data_diagnosis', '数据分析与问题诊断'),
        ('education_growth', '教育与个人成长'),
        ('ai_training', 'AI训练与多模态'),
        ('product_strategy', '产品经理与战略'),
        ('marketing_service', '营销与客户服务'),
        ('spreadsheet_db', '电子表格和数据库'),
        ('legal_policy', '法律与政策制定'),
        ('business_decision', '商业战略与决策'),
        ('creative_writing', '创意写作与内容创作'),
    ]

    scenario_id = models.CharField(max_length=50, unique=True, verbose_name='场景ID')
    title = models.CharField(max_length=100, verbose_name='场景标题')
    description = models.TextField(verbose_name='场景描述')
    icon = models.CharField(max_length=50, default='🎯', verbose_name='图标')
    difficulty = models.CharField(max_length=20, choices=[('beginner', '初级'), ('intermediate', '中级'), ('advanced', '高级')], default='intermediate', verbose_name='难度')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        ordering = ['order']
        verbose_name = '练习场景'
        verbose_name_plural = '练习场景'

    def __str__(self):
        return self.title


class PracticeTopic(models.Model):
    scenario = models.ForeignKey(PracticeScenario, on_delete=models.CASCADE, related_name='topics', verbose_name='所属场景')
    topic_number = models.IntegerField(verbose_name='主题编号')  # 1 或 2
    title = models.CharField(max_length=200, verbose_name='主题标题')
    description = models.TextField(verbose_name='主题描述')
    example_prompt = models.TextField(blank=True, verbose_name='示例提示词')
    evaluation_criteria = models.JSONField(default=dict, verbose_name='评估标准')

    class Meta:
        ordering = ['topic_number']
        unique_together = ['scenario', 'topic_number']
        verbose_name = '练习主题'
        verbose_name_plural = '练习主题'

    def __str__(self):
        return f'{self.scenario.title} - 主题{self.topic_number}: {self.title}'


class PracticeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_records')
    scenario = models.ForeignKey(PracticeScenario, on_delete=models.CASCADE, null=True, blank=True, verbose_name='练习场景')
    topic = models.ForeignKey(PracticeTopic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='选择的主题')

    user_prompt = models.TextField(verbose_name='用户提示词')
    system_prompt = models.TextField(verbose_name='系统提示词(场景)', default='')
    llm_response = models.TextField(verbose_name='大模型原始回复', blank=True)

    scores = models.JSONField(verbose_name='评分数据', default=dict)
    suggestions = models.TextField(verbose_name='修改建议', blank=True)
    overall_score = models.IntegerField(verbose_name='综合得分', default=0)
    
    duration_seconds = models.IntegerField(default=0, verbose_name='练习时长(秒)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'

    def __str__(self):
        scenario_title = self.scenario.title if self.scenario else '未知场景'
        return f'{self.user.username} - {scenario_title} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    @property
    def formatted_duration(self):
        if self.duration_seconds < 60:
            return f"{self.duration_seconds}秒"
        elif self.duration_seconds < 3600:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            return f"{minutes}分{seconds}秒" if seconds else f"{minutes}分钟"
        else:
            hours = self.duration_seconds // 3600
            minutes = (self.duration_seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟" if minutes else f"{hours}小时"

    def get_topic_display(self):
        if self.topic:
            return self.topic.title
        return "未选择主题"

