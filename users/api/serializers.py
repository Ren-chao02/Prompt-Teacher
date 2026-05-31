from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import UserProfile


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(max_length=150, help_text='用户名')
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('用户名或密码错误')

        if not user.is_active:
            raise serializers.ValidationError('该账号已被禁用')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'role', 'phone',
            'avatar', 'student_id', 'semester', 'major',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')
    password_confirm = serializers.CharField(max_length=128, write_only=True, help_text='确认密码')

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'role', 'phone', 'student_id', 'semester', 'major', 'teacher'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        
        if attrs.get('role') == 'student' and not attrs.get('student_id'):
            raise serializers.ValidationError({'student_id': '学生角色必须填写学号'})

        if attrs.get('role') == 'student' and not attrs.get('teacher'):
            raise serializers.ValidationError({'teacher': '学生角色必须选择指导教师'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = UserProfile(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(max_length=128, write_only=True, help_text='旧密码')
    new_password = serializers.CharField(max_length=128, write_only=True, help_text='新密码')
    new_password_confirm = serializers.CharField(max_length=128, write_only=True, help_text='确认新密码')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码不正确')
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({'new_password_confirm': '两次输入的新密码不一致'})
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """更新用户信息序列化器（支持部分更新）"""
    
    class Meta:
        model = UserProfile
        fields = [
            'email', 'phone', 'avatar', 'student_id',
            'semester', 'major', 'teacher'
        ]
    
    def validate_student_id(self, value):
        """验证学号唯一性"""
        user = self.context['request'].user
        
        # 检查学号是否已被其他用户使用
        queryset = UserProfile.objects.filter(student_id=value)
        
        # 如果是更新操作，排除当前用户
        if user.pk:
            queryset = queryset.exclude(pk=user.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('该学号已存在')
        
        return value

    def validate_teacher(self, value):
        """验证教师角色"""
        if value and value.role not in ['admin', 'teacher']:
            raise serializers.ValidationError('只能选择管理员或教师作为指导教师')
        return value
