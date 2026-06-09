from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import UserProfile, ClassInfo


class LoginSerializer(serializers.Serializer):
    """登录序列化器 - 支持多类型标识"""
    identifier = serializers.CharField(help_text='学号/工号/用户名')
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')
    login_type = serializers.ChoiceField(
        choices=['student_id', 'employee_id', 'username'],
        default='username',
        help_text='登录方式'
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=identifier,
            password=password,
        )

        if not user:
            raise serializers.ValidationError('账号或密码错误')

        if not user.is_active:
            raise serializers.ValidationError('该账号已被禁用')

        attrs['user'] = user
        return attrs


class ClassInfoSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClassInfo
        fields = ['id', 'name', 'grade', 'major', 'class_number', 'description', 'student_count']
        read_only_fields = ['id', 'student_count']


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class_name = serializers.CharField(source='class_info.name', read_only=True, default='')
    class_id = serializers.IntegerField(source='class_info.id', read_only=True, default=None)
    login_identifier = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'real_name', 'email', 'role', 'phone',
            'avatar', 'student_id', 'employee_id', 'semester',
            'class_info', 'class_name', 'class_id',
            'must_change_password',
            'teacher', 'date_joined', 'last_login', 'is_active', 'login_identifier'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def get_login_identifier(self, obj):
        if obj.role == 'student':
            return obj.student_id or obj.username
        elif obj.role == 'teacher':
            return obj.employee_id or obj.username
        return obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password = serializers.CharField(max_length=128, write_only=True, help_text='密码')
    password_confirm = serializers.CharField(max_length=128, write_only=True, help_text='确认密码')

    class Meta:
        model = UserProfile
        fields = [
            'real_name', 'role', 'email', 'password', 'password_confirm',
            'phone', 'student_id', 'employee_id', 'semester',
            'class_info', 'teacher'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})

        role = attrs.get('role', 'student')

        if role == 'student' and not attrs.get('student_id'):
            raise serializers.ValidationError({'student_id': '学生角色必须填写学号'})

        if role == 'student' and not attrs.get('real_name'):
            raise serializers.ValidationError({'real_name': '真实姓名不能为空'})

        if role == 'teacher' and not attrs.get('employee_id'):
            raise serializers.ValidationError({'employee_id': '教师角色必须填写工号'})

        if role == 'teacher' and not attrs.get('real_name'):
            raise serializers.ValidationError({'real_name': '真实姓名不能为空'})

        # 学号唯一性检查
        if attrs.get('student_id'):
            if UserProfile.objects.filter(student_id=attrs['student_id']).exists():
                raise serializers.ValidationError({'student_id': '该学号已存在'})

        # 工号唯一性检查
        if attrs.get('employee_id'):
            if UserProfile.objects.filter(employee_id=attrs['employee_id']).exists():
                raise serializers.ValidationError({'employee_id': '该工号已存在'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password', '123456')
        role = validated_data.get('role', 'student')

        # 自动生成 username
        if role == 'student':
            validated_data['username'] = validated_data.get('student_id', '')
        elif role == 'teacher':
            validated_data['username'] = validated_data.get('employee_id', '')

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
            'real_name', 'email', 'phone', 'avatar', 'student_id',
            'employee_id', 'semester', 'class_info', 'teacher'
        ]

    def validate_student_id(self, value):
        """验证学号唯一性"""
        user = self.context['request'].user

        queryset = UserProfile.objects.filter(student_id=value)

        if user.pk:
            queryset = queryset.exclude(pk=user.pk)

        if queryset.exists():
            raise serializers.ValidationError('该学号已存在')

        return value

    def validate_employee_id(self, value):
        """验证工号唯一性"""
        user = self.context['request'].user

        queryset = UserProfile.objects.filter(employee_id=value)

        if user.pk:
            queryset = queryset.exclude(pk=user.pk)

        if queryset.exists():
            raise serializers.ValidationError('该工号已存在')

        return value

    def validate_teacher(self, value):
        """验证教师角色"""
        if value and value.role not in ['admin', 'teacher']:
            raise serializers.ValidationError('只能选择管理员或教师作为指导教师')
        return value
