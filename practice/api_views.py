from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PracticeTopic, PracticeScenario


@csrf_exempt
@login_required
def api_get_topics(request):
    scenario_id = request.GET.get('scenario')
    
    if not scenario_id:
        return JsonResponse({'error': '缺少场景ID'}, status=400)
    
    try:
        scenario = PracticeScenario.objects.get(scenario_id=scenario_id)
        topics = scenario.topics.all().values('id', 'topic_number', 'title')
        
        return JsonResponse({
            'success': True,
            'topics': list(topics)
        })
    
    except PracticeScenario.DoesNotExist:
        return JsonResponse({'error': '场景不存在'}, status=404)
