"""
数据分析 API 序列化器
定义响应数据结构
"""

from rest_framework import serializers


class OverviewStatsSerializer(serializers.Serializer):
    """概览统计数据序列化器"""
    
    # 学习模块统计
    total_materials = serializers.IntegerField(default=0)
    today_new = serializers.IntegerField(default=0)
    completion_rate = serializers.FloatField(default=0.0)
    avg_read_time = serializers.FloatField(default=0.0)
    
    # 练习模块统计
    total_records = serializers.IntegerField(default=0)
    avg_score = serializers.FloatField(default=0.0)
    pass_rate = serializers.FloatField(default=0.0)
    
    # 用户统计
    active_today = serializers.IntegerField(default=0)
    new_this_week = serializers.IntegerField(default=0)
    retention_rate = serializers.FloatField(default=0.0)


class TrendDataPointSerializer(serializers.Serializer):
    """趋势数据点"""
    date = serializers.DateField()
    value = serializers.FloatField()
    count = serializers.IntegerField(default=0)


class TopContentItemSerializer(serializers.Serializer):
    """热门内容项"""
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    category = serializers.CharField(required=False, allow_blank=True)
    views = serializers.IntegerField(default=0)
    completions = serializers.IntegerField(default=0)


class TopUserItemSerializer(serializers.Serializer):
    """优秀用户项 (管理员/教师视角)"""
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    role = serializers.CharField(max_length=20)
    total_practices = serializers.IntegerField(default=0)
    avg_score = serializers.FloatField(default=0.0)


class OverviewResponseSerializer(serializers.Serializer):
    """概览接口完整响应"""
    
    learning = OverviewStatsSerializer(required=False)
    practice = OverviewStatsSerializer(required=False)
    users = OverviewStatsSerializer(required=False)
    
    daily_trend = TrendDataPointSerializer(many=True, required=False)
    top_content = TopContentItemSerializer(many=True, required=False)
    top_users = TopUserItemSerializer(many=True, required=False)


class LearningTimelineSerializer(serializers.Serializer):
    """学习时间线数据"""
    dates = serializers.ListField(child=serializers.CharField(), default=list)
    read_minutes = serializers.ListField(child=serializers.IntegerField(), default=list)
    completed_count = serializers.ListField(child=serializers.IntegerField(), default=list)


class CategoryCompletionSerializer(serializers.Serializer):
    """分类完成情况"""
    category = serializers.CharField()
    total = serializers.IntegerField(default=0)
    completed = serializers.IntegerField(default=0)
    rate = serializers.FloatField(default=0.0)


class LearningProgressResponseSerializer(serializers.Serializer):
    """学习进度接口响应"""
    
    timeline = LearningTimelineSerializer(required=False)
    completion = serializers.DictField(required=False)
    popular_content = TopContentItemSerializer(many=True, required=False)
    reading_habits = serializers.DictField(required=False)


class ScoreDistributionSerializer(serializers.Serializer):
    """分数分布"""
    excellent = serializers.IntegerField(default=0)  # 90-100
    good = serializers.IntegerField(default=0)        # 80-89
    average = serializers.IntegerField(default=0)      # 70-79
    below_average = serializers.IntegerField(default=0)  # 60-69
    fail = serializers.IntegerField(default=0)         # 0-59
    
    mean = serializers.FloatField(default=0.0)
    median = serializers.FloatField(default=0.0)
    std_dev = serializers.FloatField(default=0.0)


class ScenarioComparisonSerializer(serializers.Serializer):
    """场景对比数据"""
    scenario_id = serializers.IntegerField()
    scenario_title = serializers.CharField()
    icon = serializers.CharField(required=False)
    difficulty = serializers.CharField(required=False)
    avg_score = serializers.FloatField(default=0.0)
    practice_count = serializers.IntegerField(default=0)
    best_score = serializers.FloatField(default=0.0)
    improvement_rate = serializers.CharField(required=False, allow_blank=True)


class WeakPointSerializer(serializers.Serializer):
    """薄弱点识别"""
    topic_id = serializers.IntegerField()
    topic_title = serializers.CharField()
    error_rate = serializers.FloatField(default=0.0)
    total_attempts = serializers.IntegerField(default=0)
    suggestion = serializers.CharField(required=False, allow_blank=True)


class PracticeStatisticsResponseSerializer(serializers.Serializer):
    """练习统计接口响应"""
    
    score_trend = LearningTimelineSerializer(required=False)
    distribution = ScoreDistributionSerializer(required=False)
    scenario_comparison = ScenarioComparisonSerializer(many=True, required=False)
    weak_points = WeakPointSerializer(many=True, required=False)
    ranking = TopUserItemSerializer(many=True, required=False)
