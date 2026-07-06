from django.contrib import admin
from .models import PracticeRecord, LLMConfig


@admin.register(PracticeRecord)
class PracticeRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['user_prompt']
    readonly_fields = ['created_at']


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'provider', 'model_id', 'is_default', 'is_active']
    list_filter = ['provider', 'is_default', 'is_active']
    search_fields = ['name', 'model_id', 'owner__username']
