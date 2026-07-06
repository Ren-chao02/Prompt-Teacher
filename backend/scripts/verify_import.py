import os
import sys
import django

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
django.setup()

from practice.models import PracticeScenario, PracticeTopic

print('=' * 60)
print('数据库验证报告')
print('=' * 60)

print(f'\n📊 统计信息:')
print(f'  - 场景总数: {PracticeScenario.objects.count()}')
print(f'  - 主题总数: {PracticeTopic.objects.count()}')

print(f'\n✅ 最新导入的场景 (从markdown表格):')
new_scenarios = PracticeScenario.objects.filter(
    scenario_id__in=[
        'content_creation', 'office_efficiency', 'data_logic',
        'education_growth', 'ai_multimodal', 'product_design',
        'sales_service', 'ecommerce_trade', 'legal_compliance',
        'business_strategy', 'creative_writing',
        'medical_health', 'finance_investment', 'hr_recruitment', 'tourism_hotel'
    ]
).order_by('order')

for scenario in new_scenarios:
    topics_count = scenario.topics.count()
    print(f'\n  {scenario.icon} {scenario.title}')
    print(f'    - ID: {scenario.scenario_id}')
    print(f'    - 难度: {scenario.difficulty}')
    print(f'    - 状态: {scenario.status}')
    print(f'    - 主题数: {topics_count}')
    
    if topics_count > 0:
        for topic in scenario.topics.all()[:2]:
            print(f'      • 主题{topic.topic_number}: {topic.title}')

print('\n' + '=' * 60)
print('验证完成！')
print('=' * 60)