from django.contrib import admin
from .models import LearningMaterial


@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order_index', 'created_at']
    list_filter = ['category']
    search_fields = ['title']
    list_editable = ['order_index']
