from django.contrib import admin
from .models import UserProfile, ClassInfo


@admin.register(ClassInfo)
class ClassInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'major', 'class_number',)
    list_filter = ('grade', 'major',)
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'username', 'role', 'student_id', 'employee_id', 'class_info', 'is_active')
    list_filter = ('role', 'is_active', 'class_info',)
    search_fields = ('username', 'real_name', 'student_id', 'employee_id', 'email')
