from django.db import models
from django.conf import settings


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

    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级')
    ]

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已下架')
    ]

    scenario_id = models.CharField(max_length=50, unique=True, verbose_name='场景ID')
    title = models.CharField(max_length=100, verbose_name='场景标题')
    description = models.TextField(verbose_name='场景描述')
    icon = models.CharField(max_length=50, default='🎯', verbose_name='图标')
    cover_image = models.URLField(blank=True, null=True, verbose_name='封面图片')
    
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='intermediate',
        verbose_name='难度'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
        db_index=True
    )
    
    order = models.IntegerField(default=0, verbose_name='排序权重')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_scenarios',
        verbose_name='创建者'
    )

    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    practice_count = models.PositiveIntegerField(default=0, verbose_name='练习次数')
    avg_score = models.FloatField(default=0, verbose_name='平均分')

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')

    class Meta:
        ordering = ['-order', '-created_at']
        verbose_name = '练习场景'
        verbose_name_plural = '练习场景'

    def __str__(self):
        return self.title

    def increment_view(self):
        self.view_count += 1
        self.save()

    def increment_practice_count(self):
        self.practice_count += 1
        self.save()

    def publish(self):
        from django.utils import timezone
        self.status = 'published'
        self.published_at = timezone.now()
        self.is_active = True
        self.save()

    def archive(self):
        self.status = 'archived'
        self.is_active = False
        self.save()


class PracticeTopic(models.Model):
    TOPIC_TYPE_CHOICES = [
        ('standard', '标准题'),
        ('challenge', '挑战题'),
        ('bonus', '加分题')
    ]

    scenario = models.ForeignKey(
        PracticeScenario,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name='所属场景'
    )
    
    topic_number = models.IntegerField(verbose_name='主题编号')
    title = models.CharField(max_length=200, verbose_name='主题标题')
    description = models.TextField(verbose_name='主题描述')
    
    topic_type = models.CharField(
        max_length=20,
        choices=TOPIC_TYPE_CHOICES,
        default='standard',
        verbose_name='题目类型'
    )
    
    example_prompt = models.TextField(blank=True, verbose_name='示例提示词')
    evaluation_criteria = models.JSONField(default=dict, verbose_name='评估标准')
    
    max_score = models.IntegerField(default=100, verbose_name='满分')
    time_limit_minutes = models.IntegerField(default=30, verbose_name='时间限制(分钟)')
    
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['order', 'topic_number']
        unique_together = ['scenario', 'topic_number']
        verbose_name = '练习主题'
        verbose_name_plural = '练习主题'

    def __str__(self):
        return f'{self.scenario.title} - 主题{self.topic_number}: {self.title}'


class PracticeRecord(models.Model):
    SCORE_LEVEL_CHOICES = [
        ('excellent', '优秀 (90-100)'),
        ('good', '良好 (80-89)'),
        ('average', '中等 (70-79)'),
        ('needs_improvement', '待提高 (60-69)'),
        ('poor', '较差 (<60)')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_records'
    )
    
    scenario = models.ForeignKey(
        PracticeScenario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='练习场景'
    )
    
    topic = models.ForeignKey(
        PracticeTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='选择的主题'
    )

    user_prompt = models.TextField(verbose_name='用户提示词')
    system_prompt = models.TextField(verbose_name='系统提示词(场景)', default='')
    llm_response = models.TextField(verbose_name='大模型原始回复', blank=True)

    scores = models.JSONField(verbose_name='评分数据', default=dict)
    suggestions = models.TextField(verbose_name='修改建议', blank=True)
    overall_score = models.IntegerField(verbose_name='综合得分', default=0)
    
    score_level = models.CharField(
        max_length=20,
        choices=SCORE_LEVEL_CHOICES,
        default='average',
        verbose_name='成绩等级'
    )
    
    duration_seconds = models.IntegerField(default=0, verbose_name='练习时长(秒)')
    
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    feedback = models.TextField(blank=True, verbose_name='学生反馈')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['scenario', '-overall_score']),
            models.Index(fields=['score_level']),
        ]
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

    def save(self, *args, **kwargs):
        if self.overall_score >= 90:
            self.score_level = 'excellent'
        elif self.overall_score >= 80:
            self.score_level = 'good'
        elif self.overall_score >= 70:
            self.score_level = 'average'
        elif self.overall_score >= 60:
            self.score_level = 'needs_improvement'
        else:
            self.score_level = 'poor'
        
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)


class LLMConfig(models.Model):
    """用户自定义LLM模型配置"""

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('ollama', 'Ollama本地'),
        ('qwen', '通义千问'),
        ('deepseek', 'DeepSeek'),
        ('custom', '自定义'),
    ]

    PROVIDER_API_TEMPLATES = {
        'openai': 'https://api.openai.com/v1/chat/completions',
        'ollama': 'http://localhost:11434/v1/chat/completions',
        'qwen': 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
        'deepseek': 'https://api.deepseek.com/chat/completions',
    }

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='llm_configs',
        verbose_name='所属用户'
    )
    name = models.CharField(max_length=100, verbose_name='显示名称')
    provider = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        default='custom',
        verbose_name='提供商'
    )
    api_url = models.CharField(max_length=500, verbose_name='API地址')
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API密钥')
    model_id = models.CharField(max_length=100, verbose_name='模型标识符')
    is_default = models.BooleanField(default=False, verbose_name='默认模型')
    is_active = models.BooleanField(default=True, verbose_name='启用')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'LLM模型配置'
        verbose_name_plural = 'LLM模型配置'
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_llm_per_user'
            )
        ]

    def __str__(self):
        return f'{self.owner.username} - {self.name} ({self.model_id})'

    def save(self, *args, **kwargs):
        if self.is_default:
            LLMConfig.objects.filter(
                owner=self.owner,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_provider_template(cls, provider):
        return cls.PROVIDER_API_TEMPLATES.get(provider, '')
