from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import PracticeRecord
from .services.llm_service import llm_service
from .prompts.evaluation_prompts import SCENARIO_PROMPTS


@login_required
def practice_view(request):
    if request.method == 'POST':
        user_prompt = request.POST.get('user_prompt', '')
        scenario = request.POST.get('scenario', 'general')
        system_prompt = SCENARIO_PROMPTS.get(scenario, SCENARIO_PROMPTS['general'])
        
        if not user_prompt.strip():
            messages.error(request, '请输入提示词')
            return render(request, 'practice.html', {
                'scenarios': SCENARIO_PROMPTS,
                'selected_scenario': scenario
            })
        
        result = llm_service.evaluate_prompt(user_prompt, system_prompt)
        
        if result['success']:
            practice_record = PracticeRecord.objects.create(
                user=request.user,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                llm_response=result.get('raw_response', ''),
                scores=result['data'].get('scores', {}),
                suggestions=result['data'].get('suggestions', ''),
                overall_score=result['data'].get('overall_score', 0)
            )
            
            return render(request, 'practice.html', {
                'scenarios': SCENARIO_PROMPTS,
                'selected_scenario': scenario,
                'result': result['data'],
                'record_id': practice_record.id
            })
        else:
            messages.error(request, f'评估失败: {result["error"]}')
            return render(request, 'practice.html', {
                'scenarios': SCENARIO_PROMPTS,
                'selected_scenario': scenario
            })
    
    return render(request, 'practice.html', {
        'scenarios': SCENARIO_PROMPTS,
        'selected_scenario': 'general'
    })


@login_required
def practice_history(request):
    records = PracticeRecord.objects.filter(user=request.user)[:20]
    return render(request, 'practice_history.html', {'records': records})


@login_required
def practice_detail(request, record_id):
    record = get_object_or_404(PracticeRecord, id=record_id, user=request.user)
    return render(request, 'practice_detail.html', {'record': record})
