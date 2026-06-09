from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Max, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsAdmin, IsAuthenticated

from ..models import PracticeScenario, PracticeTopic, PracticeRecord, LLMConfig
from .serializers import (
    PracticeScenarioListSerializer,
    PracticeScenarioDetailSerializer,
    PracticeScenarioCreateSerializer,
    PracticeScenarioUpdateSerializer,
    PracticeTopicListSerializer,
    PracticeTopicDetailSerializer,
    PracticeTopicCreateSerializer,
    PracticeTopicUpdateSerializer,
    PracticeRecordListSerializer,
    PracticeRecordDetailSerializer,
    PracticeRecordCreateSerializer,
    PracticeRecordUpdateSerializer,
    LLMConfigSerializer,
    LLMConfigCreateSerializer,
    LLMConfigTestSerializer,
)


class PracticeScenarioViewSet(viewsets.ModelViewSet):
    """
    练习场景管理 ViewSet
    
    list: 返回场景列表 (支持分页、筛选、搜索)
    retrieve: 返回场景详情 (包含主题列表)
    create: 创建新场景
    update: 更新场景信息
    partial_update: 部分更新
    destroy: 删除场景
    publish: 发布/下架场景
    statistics: 获取场景统计信息
    reorder: 批量更新排序
    """
    
    queryset = PracticeScenario.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'difficulty', 'is_active']
    search_fields = ['title', 'description', 'scenario_id']
    ordering_fields = ['order', 'created_at', 'updated_at', 'view_count', 'practice_count', 'avg_score']
    ordering = ['-order', '-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PracticeScenarioListSerializer
        elif self.action == 'create':
            return PracticeScenarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PracticeScenarioUpdateSerializer
        return PracticeScenarioDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        if self.action in ['publish', 'reorder']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            return PracticeScenario.objects.filter(
                is_active=True,
                status='published'
            )
        
        if user.role == 'teacher':
            return PracticeScenario.objects.filter(
                Q(is_active=True) | Q(author=user)
            )
        
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        """返回场景列表（包装响应格式）"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.paginator
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': queryset.count()
            }
        })

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        scenario = self.get_object()
        action_type = request.data.get('action', 'publish')
        
        if action_type == 'publish':
            scenario.publish()
            message = f"场景 '{scenario.title}' 已成功发布"
        else:
            scenario.archive()
            message = f"场景 '{scenario.title}' 已下架"
        
        serializer = self.get_serializer(scenario)
        return Response({
            'code': 200,
            'message': message,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        
        base_qs = self.get_queryset()
        
        stats = {
            'total': base_qs.count(),
            'published': base_qs.filter(status='published').count(),
            'draft': base_qs.filter(status='draft').count(),
            'archived': base_qs.filter(status='archived').count(),
            
            'by_difficulty': dict(
                base_qs.values('difficulty')
                .annotate(count=Count('id'))
                .values_list('difficulty', 'count')
            ),
            
            'top_viewed': (
                base_qs.order_by('-view_count')[:5]
                .values_list('id', 'title', 'view_count')
            ),
            
            'most_practiced': (
                base_qs.order_by('-practice_count')[:5]
                .values_list('id', 'title', 'practice_count')
            ),
            
            'recently_created': (
                base_qs.order_by('-created_at')[:5]
                .values_list('id', 'title', 'created_at')
            )
        }
        
        return Response({
            'code': 200,
            'message': '获取统计数据成功',
            'data': stats
        })

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        items = request.data.get('items', [])
        
        if not items or not isinstance(items, list):
            return Response({
                'code': 400,
                'message': '请提供有效的排序数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = 0
        for item in items:
            try:
                scenario_id = item.get('id')
                order = item.get('order', 0)
                
                if scenario_id and order is not None:
                    PracticeScenario.objects.filter(id=scenario_id).update(order=order)
                    updated_count += 1
            except Exception as e:
                continue
        
        return Response({
            'code': 200,
            'message': f'成功更新 {updated_count} 个场景的排序'
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请选择要删除的场景'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = PracticeScenario.objects.filter(id__in=ids).delete()
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个场景'
        })


class PracticeTopicViewSet(viewsets.ModelViewSet):
    """
    练习主题管理 ViewSet
    
    list: 返回主题列表 (支持按场景筛选)
    retrieve: 返回主题详情
    create: 创建新主题
    update: 更新主题信息
    partial_update: 部分更新
    destroy: 删除主题
    by_scenario: 获取指定场景的所有主题
    """
    
    queryset = PracticeTopic.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['scenario', 'topic_type', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'topic_number', 'created_at']
    ordering = ['order', 'topic_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return PracticeTopicListSerializer
        elif self.action == 'create':
            return PracticeTopicCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PracticeTopicUpdateSerializer
        return PracticeTopicDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'student':
            scenario_ids = PracticeScenario.objects.filter(
                is_active=True,
                status='published'
            ).values_list('id', flat=True)
            return queryset.filter(scenario__id__in=scenario_ids, is_active=True)
        
        return queryset.select_related('scenario')

    def list(self, request, *args, **kwargs):
        """返回主题列表（包装响应格式）"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.paginator
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': queryset.count()
            }
        })

    @action(detail=False, methods=['get'])
    def by_scenario(self, request):
        scenario_id = request.query_params.get('scenario_id')
        
        if not scenario_id:
            return Response({
                'code': 400,
                'message': '请提供场景ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        topics = self.get_queryset().filter(scenario_id=scenario_id)
        serializer = self.get_serializer(topics, many=True)
        
        return Response({
            'code': 200,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请选择要删除的主题'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = PracticeTopic.objects.filter(id__in=ids).delete()
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个主题'
        })


class PracticeRecordViewSet(viewsets.ModelViewSet):
    """
    练习记录管理 ViewSet
    
    list: 返回记录列表 (支持多维度筛选)
    retrieve: 返回记录详情 (完整输入输出 + 评分明细)
    create: 创建练习记录
    update: 更新记录
    partial_update: 部分更新
    destroy: 删除记录
    my_records: 我的练习记录 (学生视角)
    export: 导出记录 (Excel/PDF)
    statistics: 练习统计数据分析
    """
    
    queryset = PracticeRecord.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'scenario', 'topic', 'score_level', 'is_completed']
    search_fields = ['user_prompt', 'suggestions', 'feedback']
    ordering_fields = ['created_at', 'overall_score', 'duration_seconds', '-overall_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PracticeRecordListSerializer
        elif self.action == 'create':
            return PracticeRecordCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PracticeRecordUpdateSerializer
        return PracticeRecordDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        if self.action == 'export':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('user', 'scenario', 'topic')
        
        params = self.request.query_params
        
        score_min = params.get('score_min')
        score_max = params.get('score_max')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        
        if score_min:
            queryset = queryset.filter(overall_score__gte=int(score_min))
        if score_max:
            queryset = queryset.filter(overall_score__lte=int(score_max))
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        if user.role == 'student':
            return queryset.filter(user=user)
        
        if user.role == 'teacher':
            student_ids = user.students.values_list('id', flat=True)
            return queryset.filter(user_id__in=student_ids)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """返回记录列表（包装响应格式）"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.paginator
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                    'results': serializer.data,
                    'count': queryset.count()
                }
            })

    def retrieve(self, request, *args, **kwargs):
        """返回记录详情（包装响应格式）"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_records(self, request):
        records = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        base_qs = self.get_queryset()
        
        stats = {
            'overview': {
                'total': base_qs.count(),
                'completed': base_qs.filter(is_completed=True).count(),
                'avg_score': round(base_qs.aggregate(avg=Avg('overall_score'))['avg'] or 0, 1),
                'total_duration': sum(base_qs.values_list('duration_seconds', flat=True))
            },
            
            'by_score_level': dict(
                base_qs.values('score_level')
                .annotate(count=Count('id'))
                .values_list('score_level', 'count')
            ),
            
            'by_scenario': list(
                base_qs.values('scenario__title')
                .annotate(
                    count=Count('id'),
                    avg_score=Avg('overall_score'),
                    total_duration=Sum('duration_seconds')
                )
                .order_by('-count')[:10]
                .values('scenario__title', 'count', 'avg_score', 'total_duration')
            ),
            
            'trend_daily': list(
                base_qs.extra(
                    select={'day': 'date(created_at)'}
                )
                .values('day')
                .annotate(count=Count('id'))
                .order_by('-day')[:30]
            ),
            
            'top_performers': list(
                base_qs.values('user__username', 'user__role')
                .annotate(
                    count=Count('id'),
                    avg_score=Avg('overall_score'),
                    best_score=Max('overall_score')
                )
                .filter(count__gte=5)
                .order_by('-avg_score')[:10]
            ) if user.role in ['admin', 'teacher'] else []
        }
        
        stats['by_scenario'] = list(
            base_qs.values('scenario__title')
            .annotate(
                count=Count('id'),
                avg_score=Avg('overall_score'),
                total_duration=Sum('duration_seconds')
            )
            .order_by('-count')[:10]
            .values('scenario__title', 'count', 'avg_score', 'total_duration')
        )
        
        return Response({
            'code': 200,
            'message': '获取统计数据成功',
            'data': stats
        })

    @action(detail=False, methods=['post'])
    def export(self, request):
        format_type = request.data.get('format', 'excel')
        ids = request.data.get('ids', [])
        
        queryset = self.get_queryset()
        if ids:
            queryset = queryset.filter(id__in=ids)
        
        data = queryset.select_related('user', 'scenario', 'topic')[:1000]
        
        export_data = []
        for record in data:
            export_data.append({
                '用户名': record.user.username,
                '角色': getattr(record.user, 'role', ''),
                '场景': record.scenario.title if record.scenario else '',
                '主题': record.topic.title if record.topic else '',
                '得分': record.overall_score,
                '等级': record.get_score_level_display(),
                '用时(秒)': record.duration_seconds,
                '是否完成': '是' if record.is_completed else '否',
                '创建时间': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        if format_type == 'excel':
            import pandas as pd
            from io import BytesIO
            
            df = pd.DataFrame(export_data)
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="practice_records_{timezone.now().strftime("%Y%m%d")}.xlsx"'
            return response
        
        from django.http import HttpResponse
        return Response({
            'code': 200,
            'data': export_data,
            'message': f'导出{len(export_data)}条记录'
        })


class LLMConfigViewSet(viewsets.ModelViewSet):
    """
    用户自定义LLM模型配置管理

    list: 列出当前用户的所有模型配置
    retrieve: 获取单个配置详情
    create: 创建新的模型配置
    update: 更新配置
    partial_update: 部分更新
    destroy: 删除配置
    set_default: 设为默认模型
    test_connection: 测试API连接
    my_configs: 获取当前用户的所有配置（前端列表用）
    """

    queryset = LLMConfig.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'is_active']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LLMConfigCreateSerializer
        if self.action == 'test_connection':
            return LLMConfigTestSerializer
        return LLMConfigSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user).order_by('-is_default', '-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_configs(self, request):
        configs = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(configs, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        config = self.get_object()
        config.is_default = True
        config.save()
        return Response({'code': 200, 'message': f'已将 {config.name} 设为默认模型'})

    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from ..services.llm_service import llm_service
        result = llm_service.test_connection(
            api_url=serializer.validated_data['api_url'],
            api_key=serializer.validated_data.get('api_key', ''),
            model_id=serializer.validated_data['model_id']
        )

        if result['success']:
            return Response({'code': 200, 'data': result})
        return Response({'code': 400, 'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
