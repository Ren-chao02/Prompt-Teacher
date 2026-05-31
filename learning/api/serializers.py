from rest_framework import serializers
from ..models import LearningMaterial
from django.contrib.auth import get_user_model

User = get_user_model()


class LearningMaterialListSerializer(serializers.ModelSerializer):
    """学习资料列表序列化器（精简版）"""
    
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LearningMaterial
        fields = [
            'id', 'title', 'summary', 'category', 'category_display',
            'status', 'status_display', 'author', 'author_name',
            'cover_image', 'tags', 'view_count', 'like_count',
            'order_index', 'created_at', 'updated_at', 'reading_time'
        ]
        read_only_fields = ['id', 'view_count', 'like_count', 'created_at', 'updated_at']


class LearningMaterialDetailSerializer(serializers.ModelSerializer):
    """学习资料详情序列化器（完整版）"""
    
    author_info = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LearningMaterial
        fields = [
            'id', 'title', 'summary', 'content', 'category', 'category_display',
            'status', 'status_display', 'author', 'author_info',
            'cover_image', 'tags', 'view_count', 'like_count',
            'order_index', 'created_at', 'updated_at', 'published_at',
            'reading_time', 'is_published'
        ]
        read_only_fields = ['id', 'view_count', 'like_count', 'created_at', 'updated_at', 'published_at']
    
    def get_author_info(self, obj):
        """获取作者详细信息"""
        if obj.author:
            return {
                'id': obj.author.id,
                'username': obj.author.username,
                'email': obj.author.email,
                'avatar': obj.author.avatar,
                'role': obj.author.role
            }
        return None


class LearningMaterialCreateSerializer(serializers.ModelSerializer):
    """创建学习资料序列化器"""
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=[]
    )
    
    class Meta:
        model = LearningMaterial
        fields = [
            'title', 'summary', 'content', 'category', 'status',
            'cover_image', 'tags', 'order_index'
        ]
    
    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError('标题不能为空')
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError('标题长度不能少于2个字符')
        
        if len(value) > 200:
            raise serializers.ValidationError('标题长度不能超过200个字符')
        
        return value.strip()
    
    def validate_content(self, value):
        """验证内容"""
        if not value or not value.strip():
            raise serializers.ValidationError('内容不能为空')
        
        return value
    
    def validate_category(self, value):
        """验证分类合法性"""
        valid_categories = [choice[0] for choice in LearningMaterial.CATEGORY_CHOICES]
        if value not in valid_categories:
            raise serializers.ValidationError(
                f'无效的分类，可选值: {", ".join(valid_categories)}'
            )
        return value
    
    def validate_tags(self, value):
        """验证标签"""
        if isinstance(value, list):
            unique_tags = list(set(tag.strip() for tag in value if tag.strip()))
            
            if len(unique_tags) > 10:
                raise serializers.ValidationError('标签数量不能超过10个')
            
            for tag in unique_tags:
                if len(tag) > 20:
                    raise serializers.ValidationError(f'标签 "{tag}" 长度超过20个字符')
            
            return unique_tags
        
        return []
    
    def validate(self, attrs):
        """综合验证"""
        status = attrs.get('status', 'draft')
        
        # 如果是发布状态，必须填写摘要
        if status == 'published' and not attrs.get('summary'):
            raise serializers.ValidationError({
                'summary': '发布内容时必须填写摘要'
            })
        
        return attrs
    
    def create(self, validated_data):
        """创建学习资料"""
        request = self.context.get('request')
        
        material = LearningMaterial(**validated_data)
        
        if request and request.user.is_authenticated:
            material.author = request.user
        
        # 如果是发布状态，设置发布时间
        if material.status == 'published':
            from django.utils import timezone
            material.published_at = timezone.now()
        
        material.save()
        
        return material


class LearningMaterialUpdateSerializer(serializers.ModelSerializer):
    """更新学习资料序列化器（支持部分更新）"""
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = LearningMaterial
        fields = [
            'title', 'summary', 'content', 'category', 'status',
            'cover_image', 'tags', 'order_index'
        ]
    
    def validate_title(self, value):
        if value is not None:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError('标题长度不能少于2个字符')
            if len(value) > 200:
                raise serializers.ValidationError('标题长度不能超过200个字符')
        return value
    
    def validate_category(self, value):
        if value is not None:
            valid_categories = [choice[0] for choice in LearningMaterial.CATEGORY_CHOICES]
            if value not in valid_categories:
                raise serializers.ValidationError(
                    f'无效的分类，可选值: {", ".join(valid_categories)}'
                )
        return value
    
    def validate_tags(self, value):
        if value is not None and isinstance(value, list):
            unique_tags = list(set(tag.strip() for tag in value if tag.strip()))
            
            if len(unique_tags) > 10:
                raise serializers.ValidationError('标签数量不能超过10个')
            
            for tag in unique_tags:
                if len(tag) > 20:
                    raise serializers.ValidationError(f'标签 "{tag}" 长度超过20个字符')
            
            return unique_tags
        
        return value
    
    def update(self, instance, validated_data):
        """更新学习资料"""
        old_status = instance.status
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 状态变更处理
        new_status = validated_data.get('status')
        if new_status and new_status != old_status:
            from django.utils import timezone
            
            if new_status == 'published' and old_status != 'published':
                instance.published_at = timezone.now()
            elif new_status == 'archived':
                pass
            
        instance.save()
        return instance
