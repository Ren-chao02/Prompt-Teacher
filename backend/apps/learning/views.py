from django.shortcuts import render, get_object_or_404
from .models import LearningMaterial


def learning_list(request):
    category = request.GET.get('category', 'all')
    
    if category != 'all':
        materials = LearningMaterial.objects.filter(category=category)
    else:
        materials = LearningMaterial.objects.all()
    
    categories = LearningMaterial.CATEGORY_CHOICES
    
    return render(request, 'learning.html', {
        'materials': materials,
        'categories': categories,
        'selected_category': category
    })


def learning_detail(request, material_id):
    material = get_object_or_404(LearningMaterial, id=material_id)
    
    # 获取前后章节（按order_index排序）
    all_materials = LearningMaterial.objects.order_by('order_index', 'id')
    
    material_list = list(all_materials)
    current_index = None
    
    for idx, mat in enumerate(material_list):
        if mat.id == material.id:
            current_index = idx
            break
    
    prev_material = None
    next_material = None
    
    if current_index is not None:
        if current_index > 0:
            prev_material = material_list[current_index - 1]
        if current_index < len(material_list) - 1:
            next_material = material_list[current_index + 1]
    
    return render(request, 'learning_detail.html', {
        'material': material,
        'prev_material': prev_material,
        'next_material': next_material
    })
