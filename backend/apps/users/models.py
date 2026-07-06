from django.db import models
from django.contrib.auth.models import AbstractUser


class ClassInfo(models.Model):
    """班级模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='班级名称')
    grade = models.CharField(max_length=10, verbose_name='年级')
    major = models.CharField(max_length=50, verbose_name='专业')
    class_number = models.CharField(max_length=10, verbose_name='班号')
    description = models.CharField(max_length=200, blank=True, default='', verbose_name='备注')

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['grade', 'major', 'class_number']

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()


class UserProfile(AbstractUser):
    """增强用户模型 - 支持教育场景的三级权限体系"""

    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='角色',
        db_index=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='手机号'
    )

    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='头像'
    )

    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='学号',
        help_text='仅学生角色需要填写，全局唯一'
    )

    semester = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='学期',
        help_text='格式: 2024-2025-1'
    )

    major = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='专业'
    )

    teacher = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        limit_choices_to={'role': 'teacher'},
        verbose_name='指导教师',
        help_text='仅学生角色需要选择'
    )

    real_name = models.CharField(
        max_length=50,
        default='',
        blank=True,
        verbose_name='真实姓名',
        help_text='必填'
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        default=None,
        verbose_name='工号',
        help_text='仅教师角色需要填写，全局唯一'
    )

    class_info = models.ForeignKey(
        ClassInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='班级',
        help_text='学生所属班级'
    )

    must_change_password = models.BooleanField(
        default=False,
        verbose_name='需修改密码',
        help_text='首次登录后强制修改密码'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'
        ordering = ['-date_joined']

    def __str__(self):
        if self.real_name:
            if self.role == 'student' and self.student_id:
                return f'{self.real_name} ({self.student_id})'
            elif self.role == 'teacher' and self.employee_id:
                return f'{self.real_name} ({self.employee_id})'
            return self.real_name
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role in ['admin', 'teacher']
