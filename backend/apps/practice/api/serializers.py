from rest_framework import serializers
from ..models import PracticeScenario, PracticeTopic, PracticeRecord, LLMConfig


class PracticeScenarioListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True, default='')
    topics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PracticeScenario
        fields = [
            'id', 'scenario_id', 'title', 'description', 'icon',
            'difficulty', 'status', 'order', 'is_active',
            'view_count', 'practice_count', 'avg_score',
            'author', 'author_name', 'topics_count',
            'created_at', 'updated_at'
        ]
    
    def get_topics_count(self, obj):
        return obj.topics.filter(is_active=True).count()


class PracticeScenarioDetailSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PracticeScenario
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at']
    
    def get_author_info(self, obj):
        if obj.author:
            try:
                avatar_url = obj.author.avatar.url if obj.author.avatar else None
            except (ValueError, AttributeError):
                avatar_url = None

            return {
                'id': obj.author.id,
                'username': obj.author.username,
                'role': getattr(obj.author, 'role', ''),
                'avatar': avatar_url
            }
        return None
    
    def get_topics(self, obj):
        topics = obj.topics.all().order_by('order', 'topic_number')
        return PracticeTopicListSerializer(topics, many=True).data
    
    def validate_scenario_id(self, value):
        if not value or len(value) > 50:
            raise serializers.ValidationError("场景ID不能为空且长度不超过50字符")
        
        qs = PracticeScenario.objects.filter(scenario_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError(f"场景ID '{value}' 已存在")
        
        return value
    
    def validate_title(self, value):
        if not value or len(value) < 2:
            raise serializers.ValidationError("标题长度至少2个字符")
        if len(value) > 100:
            raise serializers.ValidationError("标题长度不超过100个字符")
        return value

    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("排序权重不能为负数")
        return value


class PracticeScenarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeScenario
        fields = [
            'scenario_id', 'title', 'description', 'icon', 'cover_image',
            'difficulty', 'status', 'order', 'is_active'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user if request else None
        
        instance = super().create(validated_data)
        return instance


class PracticeScenarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeScenario
        fields = [
            'title', 'description', 'icon', 'cover_image',
            'difficulty', 'status', 'order', 'is_active'
        ]


class PracticeTopicListSerializer(serializers.ModelSerializer):
    scenario_title = serializers.CharField(source='scenario.title', read_only=True)
    difficulty = serializers.CharField(source='scenario.difficulty', read_only=True)
    
    class Meta:
        model = PracticeTopic
        fields = [
            'id', 'scenario', 'scenario_title', 'topic_number',
            'title', 'description', 'topic_type', 'difficulty',
            'max_score', 'time_limit_minutes',
            'order', 'is_active', 'created_at', 'updated_at'
        ]


class PracticeTopicDetailSerializer(serializers.ModelSerializer):
    scenario_info = serializers.SerializerMethodField()
    topic_type_display = serializers.CharField(source='get_topic_type_display', read_only=True)
    
    class Meta:
        model = PracticeTopic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_scenario_info(self, obj):
        return {
            'id': obj.scenario.id,
            'title': obj.scenario.title,
            'scenario_id': obj.scenario.scenario_id,
            'difficulty': obj.scenario.difficulty,
            'icon': obj.scenario.icon
        }
    
    def validate_evaluation_criteria(self, value):
        if isinstance(value, dict):
            required_keys = ['criteria', 'weights']
            for key in required_keys:
                if key not in value:
                    raise serializers.ValidationError(f"评估标准缺少必要字段: {key}")
            
            if not isinstance(value.get('criteria'), list):
                raise serializers.ValidationError("'criteria' 必须是数组")
            
            if not isinstance(value.get('weights'), dict):
                raise serializers.ValidationError("'weights' 必须是对象")
            
            total_weight = sum(value.get('weights', {}).values())
            if total_weight != 100 and total_weight != 1.0:
                raise serializers.ValidationError("权重总和应为100或1.0")
        
        return value
    
    def validate_topic_number(self, value):
        if value <= 0:
            raise serializers.ValidationError("主题编号必须大于0")
        return value
    
    def validate_max_score(self, value):
        if value <= 0:
            raise serializers.ValidationError("满分必须大于0")
        if value > 200:
            raise serializers.ValidationError("满分不能超过200")
        return value


class PracticeTopicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeTopic
        fields = [
            'scenario', 'topic_number', 'title', 'description',
            'topic_type', 'example_prompt', 'evaluation_criteria',
            'max_score', 'time_limit_minutes', 'order', 'is_active'
        ]


class PracticeTopicUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeTopic
        fields = [
            'topic_number', 'title', 'description', 'topic_type',
            'example_prompt', 'evaluation_criteria',
            'max_score', 'time_limit_minutes', 'order', 'is_active'
        ]


class PracticeRecordListSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    scenario_info = serializers.SerializerMethodField()
    topic_info = serializers.SerializerMethodField()
    formatted_duration = serializers.ReadOnlyField()
    score_level_display = serializers.CharField(source='get_score_level_display', read_only=True)
    
    class Meta:
        model = PracticeRecord
        fields = [
            'id', 'user', 'user_info', 'scenario', 'scenario_info',
            'topic', 'topic_info', 'overall_score', 'score_level',
            'score_level_display', 'duration_seconds', 'formatted_duration',
            'is_completed', 'created_at', 'completed_at'
        ]
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'role': getattr(obj.user, 'role', '')
        }
    
    def get_scenario_info(self, obj):
        if obj.scenario:
            return {
                'id': obj.scenario.id,
                'title': obj.scenario.title,
                'icon': obj.scenario.icon,
                'difficulty': obj.scenario.difficulty
            }
        return None
    
    def get_topic_info(self, obj):
        if obj.topic:
            return {
                'id': obj.topic.id,
                'title': obj.topic.title,
                'topic_number': obj.topic.topic_number
            }
        return None


class PracticeRecordDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    scenario_info = serializers.SerializerMethodField()
    topic_info = serializers.SerializerMethodField()
    formatted_duration = serializers.ReadOnlyField()
    score_level_display = serializers.CharField(source='get_score_level_display', read_only=True)
    
    class Meta:
        model = PracticeRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'score_level']
    
    def get_user_info(self, obj):
        user = obj.user
        try:
            avatar_url = user.avatar.url if user.avatar else None
        except (ValueError, AttributeError):
            avatar_url = None

        return {
            'id': user.id,
            'username': user.username,
            'full_name': f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
            'role': getattr(user, 'role', ''),
            'avatar': avatar_url,
            'student_id': getattr(user, 'student_id', None)
        }
    
    def get_scenario_info(self, obj):
        if obj.scenario:
            return {
                'id': obj.scenario.id,
                'title': obj.scenario.title,
                'scenario_id': obj.scenario.scenario_id,
                'icon': obj.scenario.icon,
                'difficulty': obj.scenario.difficulty,
                'description': obj.scenario.description[:200] + ('...' if len(obj.scenario.description) > 200 else '')
            }
        return None
    
    def get_topic_info(self, obj):
        if obj.topic:
            return {
                'id': obj.topic.id,
                'title': obj.topic.title,
                'topic_number': obj.topic.topic_number,
                'evaluation_criteria': obj.topic.evaluation_criteria,
                'max_score': obj.topic.max_score
            }
        return None


class PracticeRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeRecord
        fields = [
            'scenario', 'topic', 'user_prompt', 'system_prompt',
            'llm_response', 'scores', 'suggestions', 'overall_score',
            'duration_seconds', 'is_completed', 'feedback'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        
        record = super().create(validated_data)
        
        if record.is_completed and record.scenario:
            record.scenario.increment_practice_count()
        
        return record


class PracticeRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeRecord
        fields = [
            'llm_response', 'scores', 'suggestions', 'overall_score',
            'duration_seconds', 'is_completed', 'feedback'
        ]

    def update(self, instance, validated_data):
        was_completed = instance.is_completed
        instance = super().update(instance, validated_data)
        
        if not was_completed and instance.is_completed and instance.scenario:
            instance.scenario.increment_practice_count()
        
        return instance


class LLMConfigSerializer(serializers.ModelSerializer):
    """LLM配置序列化器（不含API Key明文）"""
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)

    class Meta:
        model = LLMConfig
        fields = [
            'id', 'name', 'provider', 'provider_display',
            'api_url', 'model_id', 'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs.get('is_default'):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                existing = LLMConfig.objects.filter(
                    owner=request.user,
                    is_default=True
                )
                if self.instance:
                    existing = existing.exclude(pk=self.instance.pk)
                if existing.exists():
                    raise serializers.ValidationError({
                        'is_default': '您已有一个默认模型，请先取消之前的默认设置'
                    })
        return attrs


class LLMConfigCreateSerializer(serializers.ModelSerializer):
    """创建/编辑时使用（含API Key，仅写入不回显）"""
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)

    class Meta:
        model = LLMConfig
        fields = [
            'id', 'name', 'provider', 'provider_display',
            'api_url', 'api_key', 'model_id',
            'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # api_key 仅写入不回显，避免通过创建/更新接口泄露已保存的密钥
            'api_key': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def update(self, instance, validated_data):
        # 修复：编辑时若 api_key 为空字符串，保留已保存的密钥。
        # 原因：list/my_configs 接口出于安全不返回 api_key，前端编辑时输入框为空，
        # 若直接用空串覆盖会把已保存的密钥抹掉，导致第三方 API 调用不带
        # Authorization 头而返回 401（Ollama 无需 key 不受影响，故仅第三方失效）。
        if 'api_key' in validated_data and not validated_data.get('api_key'):
            validated_data.pop('api_key')
        return super().update(instance, validated_data)


class LLMConfigTestSerializer(serializers.Serializer):
    """测试连接专用序列化器"""
    api_url = serializers.CharField(max_length=500)
    api_key = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')
    model_id = serializers.CharField(max_length=100)

    def validate_api_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError('API地址必须以 http:// 或 https:// 开头')
        return value
