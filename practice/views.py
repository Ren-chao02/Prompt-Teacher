from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Max, Q
from django.utils import timezone
import time
import json

from .models import PracticeScenario, PracticeTopic, PracticeRecord, LLMConfig
from .services.llm_service import llm_service


@login_required
def practice_list(request):
    scenarios = PracticeScenario.objects.filter(is_active=True)
    return render(request, 'practice_list.html', {'scenarios': scenarios})


@login_required
def practice_detail(request, scenario_id):
    scenario = get_object_or_404(PracticeScenario, scenario_id=scenario_id, is_active=True)
    topics = scenario.topics.all()
    user_records = PracticeRecord.objects.filter(
        user=request.user,
        scenario=scenario
    ).order_by('-created_at')[:10]

    if request.method == 'POST':
        start_time = time.time()
        
        topic_id = request.POST.get('topic')
        user_prompt = request.POST.get('user_prompt', '')

        if not user_prompt.strip():
            messages.error(request, '请输入提示词')
            return render(request, 'practice_detail.html', {
                'scenario': scenario,
                'topics': topics,
                'records': user_records,
                'selected_topic_id': topic_id
            })

        topic = None
        system_prompt = f"场景：{scenario.title}\n描述：{scenario.description}\n"

        if topic_id:
            try:
                topic = topics.get(id=topic_id)
                system_prompt += f"\n选择的主题：{topic.title}\n主题描述：{topic.description}"
            except PracticeTopic.DoesNotExist:
                pass

        # 支持使用用户选择的LLM模型
        llm_config = None
        llm_config_id = request.POST.get('llm_config_id')
        if llm_config_id:
            try:
                llm_config = LLMConfig.objects.get(id=llm_config_id, owner=request.user, is_active=True)
            except (LLMConfig.DoesNotExist, ValueError):
                pass

        result = llm_service.evaluate_prompt(user_prompt, system_prompt, config=llm_config)

        end_time = time.time()
        duration_seconds = int(end_time - start_time)

        if result['success']:
            practice_record = PracticeRecord.objects.create(
                user=request.user,
                scenario=scenario,
                topic=topic,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                llm_response=result.get('raw_response', ''),
                scores=result['data'].get('scores', {}),
                suggestions=result['data'].get('suggestions', ''),
                overall_score=result['data'].get('overall_score', 0),
                duration_seconds=duration_seconds
            )

            return render(request, 'practice_detail.html', {
                'scenario': scenario,
                'topics': topics,
                'records': PracticeRecord.objects.filter(
                    user=request.user,
                    scenario=scenario
                ).order_by('-created_at')[:10],
                'selected_topic_id': topic_id,
                'result': result['data'],
                'record_id': practice_record.id
            })
        else:
            messages.error(request, f'评估失败: {result["error"]}')
            return render(request, 'practice_detail.html', {
                'scenario': scenario,
                'topics': topics,
                'records': user_records,
                'selected_topic_id': topic_id
            })

    return render(request, 'practice_detail.html', {
        'scenario': scenario,
        'topics': topics,
        'records': user_records
    })


@login_required
def practice_history(request):
    user = request.user
    
    base_queryset = PracticeRecord.objects.filter(user=user)
    
    filter_scenario = request.GET.get('scenario')
    filter_topic = request.GET.get('topic')
    filter_date_from = request.GET.get('date_from')
    filter_date_to = request.GET.get('date_to')
    filter_score_min = request.GET.get('score_min')
    
    if filter_scenario and filter_scenario != '':
        base_queryset = base_queryset.filter(scenario__scenario_id=filter_scenario)
    
    if filter_topic and filter_topic != '':
        base_queryset = base_queryset.filter(topic__id=filter_topic)
    
    if filter_date_from:
        try:
            from_date = timezone.datetime.strptime(filter_date_from, '%Y-%m-%d')
            base_queryset = base_queryset.filter(created_at__date__gte=from_date.date())
        except ValueError:
            pass
    
    if filter_date_to:
        try:
            to_date = timezone.datetime.strptime(filter_date_to, '%Y-%m-%d')
            base_queryset = base_queryset.filter(created_at__date__lte=to_date.date())
        except ValueError:
            pass
    
    if filter_score_min:
        try:
            score_min = int(filter_score_min)
            base_queryset = base_queryset.filter(overall_score__gte=score_min)
        except ValueError:
            pass
    
    records = base_queryset.select_related('scenario', 'topic').order_by('-created_at')[:50]
    
    scenarios = PracticeScenario.objects.filter(is_active=True).annotate(
        user_practice_count=Count('practicerecord', filter=Q(practicerecord__user=user))
    )
    
    stats = base_queryset.aggregate(
        total_count=Count('id'),
        total_duration=Sum('duration_seconds'),
        avg_score=Avg('overall_score'),
        max_score=Max('overall_score')
    )

    def format_duration(total_seconds):
        if not total_seconds:
            return "0h 0m"
        total_seconds = int(total_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"

    stats['formatted_total_duration'] = format_duration(stats.get('total_duration'))

    scenario_stats = base_queryset.values(
        'scenario__scenario_id',
        'scenario__title',
        'scenario__icon'
    ).annotate(
        count=Count('id'),
        total_duration=Sum('duration_seconds'),
        avg_score=Avg('overall_score')
    ).order_by('-count')[:12]

    scenario_stats_list = list(scenario_stats)
    for stat in scenario_stats_list:
        stat['formatted_duration'] = format_duration(stat.get('total_duration'))
    
    recent_7_days = base_queryset.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    recent_30_days = base_queryset.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()

    context = {
        'records': records,
        'scenarios': scenarios,
        'stats': stats,
        'scenario_stats': scenario_stats_list,
        'recent_7_days': recent_7_days,
        'recent_30_days': recent_30_days,
        'filter_scenario': filter_scenario or '',
        'filter_topic': filter_topic or '',
        'filter_date_from': filter_date_from or '',
        'filter_date_to': filter_date_to or '',
        'filter_score_min': filter_score_min or '',
    }
    
    return render(request, 'practice_history.html', context)




@login_required
def practice_record_detail(request, record_id):
    record = get_object_or_404(PracticeRecord, id=record_id, user=request.user)
    return render(request, 'practice_record_detail.html', {'record': record})
