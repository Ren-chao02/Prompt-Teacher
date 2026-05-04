from django.contrib import admin
from .models import PracticeRecord


@admin.register(PracticeRecord)
class PracticeRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['user_prompt']
    readonly_fields = ['created_at']
