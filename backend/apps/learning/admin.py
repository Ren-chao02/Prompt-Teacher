from django.contrib import admin
from .models import LearningMaterial, MaterialInteraction


@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order_index', 'created_at']
    list_filter = ['category']
    search_fields = ['title']
    list_editable = ['order_index']


@admin.register(MaterialInteraction)
class MaterialInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'material', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'material__title']
