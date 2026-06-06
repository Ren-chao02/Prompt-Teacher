import re
import os
import sys
import django

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
django.setup()

from practice.models import PracticeScenario, PracticeTopic


def parse_markdown_table(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    scenarios_data = []
    
    for line in lines:
        if line.startswith('|') and not line.startswith('| ---') and not line.startswith('|  |'):
            parts = [part.strip() for part in line.split('|')]
            parts = [p for p in parts if p]
            
            if len(parts) >= 5 and not parts[0].startswith('编程'):
                scenario_full = parts[0]
                topic1_title = parts[1]
                topic1_example = parts[2]
                topic2_title = parts[3]
                topic2_example = parts[4]
                
                match = re.match(r'^(.+?)\s*\((.+?)\)', scenario_full)
                if match:
                    scenario_name = match.group(1).strip()
                    target_audience = match.group(2).strip()
                else:
                    scenario_name = scenario_full
                    target_audience = ''
                
                if '医疗健康' in scenario_name or '生命科学' in scenario_name:
                    scenario_id = 'medical_health'
                    icon = '🏥'
                    difficulty = 'advanced'
                elif '金融投资' in scenario_name or '风险管理' in scenario_name:
                    scenario_id = 'finance_investment'
                    icon = '💰'
                    difficulty = 'advanced'
                elif '人力资源' in scenario_name or '招聘' in scenario_name:
                    scenario_id = 'hr_recruitment'
                    icon = '👥'
                    difficulty = 'intermediate'
                elif '旅游' in scenario_name or '酒店' in scenario_name:
                    scenario_id = 'tourism_hotel'
                    icon = '🏨'
                    difficulty = 'beginner'
                elif '内容创作' in scenario_name or '新媒体' in scenario_name:
                    scenario_id = 'content_creation'
                    icon = '✍️'
                    difficulty = 'beginner'
                elif '职场办公' in scenario_name or '效率提升' in scenario_name:
                    scenario_id = 'office_efficiency'
                    icon = '💼'
                    difficulty = 'beginner'
                elif '数据分析' in scenario_name or '逻辑处理' in scenario_name:
                    scenario_id = 'data_logic'
                    icon = '📊'
                    difficulty = 'intermediate'
                elif '教育' in scenario_name or '个人成长' in scenario_name:
                    scenario_id = 'education_growth'
                    icon = '📚'
                    difficulty = 'beginner'
                elif 'AI' in scenario_name or '绘画' in scenario_name or '多模态' in scenario_name:
                    scenario_id = 'ai_multimodal'
                    icon = '🎨'
                    difficulty = 'intermediate'
                elif '产品经理' in scenario_name or '体验设计' in scenario_name:
                    scenario_id = 'product_design'
                    icon = '🎯'
                    difficulty = 'intermediate'
                elif '销售' in scenario_name or '客户服务' in scenario_name:
                    scenario_id = 'sales_service'
                    icon = '📢'
                    difficulty = 'intermediate'
                elif '电子商务' in scenario_name or '跨境贸易' in scenario_name:
                    scenario_id = 'ecommerce_trade'
                    icon = '🛒'
                    difficulty = 'intermediate'
                elif '法律' in scenario_name or '合规' in scenario_name:
                    scenario_id = 'legal_compliance'
                    icon = '⚖️'
                    difficulty = 'advanced'
                elif '商业战略' in scenario_name or '创业策划' in scenario_name:
                    scenario_id = 'business_strategy'
                    icon = '💡'
                    difficulty = 'advanced'
                elif '创意写作' in scenario_name or '游戏' in scenario_name or '剧本' in scenario_name:
                    scenario_id = 'creative_writing'
                    icon = '🎭'
                    difficulty = 'intermediate'
                else:
                    scenario_id = scenario_name.lower().replace(' ', '_').replace('/', '_')
                    icon = '🎯'
                    difficulty = 'intermediate'
                
                description = f"{scenario_name}相关能力，面向{target_audience}"
                
                topic1_example_clean = topic1_example.replace('如：', '').strip()
                topic2_example_clean = topic2_example.replace('如：', '').strip()
                
                scenario_data = {
                    'scenario_id': scenario_id,
                    'title': scenario_name,
                    'description': description,
                    'icon': icon,
                    'difficulty': difficulty,
                    'order': len(scenarios_data) + 13,
                    'topics': [
                        {
                            'topic_number': 1,
                            'title': topic1_title,
                            'description': topic1_title,
                            'example_prompt': topic1_example_clean
                        },
                        {
                            'topic_number': 2,
                            'title': topic2_title,
                            'description': topic2_title,
                            'example_prompt': topic2_example_clean
                        }
                    ]
                }
                
                scenarios_data.append(scenario_data)
    
    return scenarios_data


def import_scenarios(scenarios_data):
    imported_count = 0
    topics_count = 0
    
    for scenario_data in scenarios_data:
        try:
            scenario, created = PracticeScenario.objects.update_or_create(
                scenario_id=scenario_data['scenario_id'],
                defaults={
                    'title': scenario_data['title'],
                    'description': scenario_data['description'],
                    'icon': scenario_data['icon'],
                    'difficulty': scenario_data['difficulty'],
                    'order': scenario_data['order'],
                    'status': 'published',
                    'is_active': True
                }
            )
            
            imported_count += 1
            action = '创建' if created else '更新'
            print(f'{action}场景: {scenario.title} (ID: {scenario.scenario_id})')
            
            for topic_data in scenario_data['topics']:
                topic, created = PracticeTopic.objects.update_or_create(
                    scenario=scenario,
                    topic_number=topic_data['topic_number'],
                    defaults={
                        'title': topic_data['title'],
                        'description': topic_data['description'],
                        'example_prompt': topic_data.get('example_prompt', ''),
                        'is_active': True
                    }
                )
                
                topics_count += 1
                action = '创建' if created else '更新'
                print(f'  {action}主题{topic.topic_number}: {topic.title}')
        
        except Exception as e:
            print(f'❌ 导入场景失败: {scenario_data["title"]}, 错误: {str(e)}')
            continue
    
    return imported_count, topics_count


def main():
    markdown_file = '/home/mjl/Prompt Teacher/docs/prompt_scenarios_table.md'
    
    print('📖 开始解析markdown表格...')
    scenarios_data = parse_markdown_table(markdown_file)
    print(f'✅ 解析完成，共提取 {len(scenarios_data)} 个场景')
    
    print('\n💾 开始导入数据库...')
    imported_count, topics_count = import_scenarios(scenarios_data)
    
    print(f'\n🎉 导入完成！')
    print(f'  - 成功导入 {imported_count} 个场景')
    print(f'  - 成功导入 {topics_count} 个主题')


if __name__ == '__main__':
    main()