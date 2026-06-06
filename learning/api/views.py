from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import LearningMaterial, MaterialInteraction
from .serializers import (
    LearningMaterialListSerializer,
    LearningMaterialDetailSerializer,
    LearningMaterialCreateSerializer,
    LearningMaterialUpdateSerializer,
)
from users.permissions import IsAdmin, IsTeacher


class LearningMaterialViewSet(viewsets.ModelViewSet):
    """
    学习资料管理 ViewSet - 完整的 CRUD + 发布/下架 + 批量操作
    
    list: 返回学习资料列表（支持搜索、筛选、排序）
    retrieve: 返回学习资料详情
    create: 创建学习资料（管理员/教师）
    update: 更新学习资料（管理员或作者）
    partial_update: 部分更新
    destroy: 删除学习资料（仅管理员）
    
    自定义 action:
    - publish: 发布内容
    - archive: 下架内容
    - bulk_delete: 批量删除
    - statistics: 获取统计数据
    """
    
    queryset = LearningMaterial.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['category', 'status', 'author']
    search_fields = ['title', 'summary', 'content', 'tags']
    ordering_fields = [
        'created_at', 'updated_at', 'view_count', 
        'like_count', 'order_index', 'title'
    ]
    ordering = ['-order_index', '-created_at']

    def list(self, request, *args, **kwargs):
        """返回学习资料列表（包装响应格式）"""
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

    def get_permissions(self):
        """根据 action 动态设置权限"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAdmin | IsTeacher]
        elif self.action in ['update', 'partial_update', 'publish', 'archive']:
            permission_classes = [IsAdmin | IsTeacher]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        elif self.action in ['bulk_delete']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """根据用户角色和查询参数过滤数据"""
        user = self.request.user
        
        if not user.is_authenticated:
            return LearningMaterial.objects.none()
        
        queryset = LearningMaterial.objects.select_related('author')
        
        # 非管理员只能看到已发布的内容（除了自己创建的）
        if user.role != 'admin':
            queryset = queryset.filter(
                Q(status='published') | Q(author=user)
            )
        
        return queryset

    def get_serializer_class(self):
        """根据 action 选择序列化器"""
        if self.action == 'list':
            return LearningMaterialListSerializer
        elif self.action == 'retrieve':
            return LearningMaterialDetailSerializer
        elif self.action == 'create':
            return LearningMaterialCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LearningMaterialUpdateSerializer
        return LearningMaterialListSerializer

    def retrieve(self, request, *args, **kwargs):
        """获取详情时增加阅读量"""
        instance = self.get_object()
        
        # 增加阅读量（排除作者自己查看）
        if request.user != instance.author:
            instance.increment_view_count()
        
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """创建学习资料"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            material = serializer.save()
            
            return Response({
                'code': 201,
                'message': '学习资料创建成功',
                'data': LearningMaterialDetailSerializer(material).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """更新学习资料"""
        instance = self.get_object()
        
        # 权限检查：非管理员只能修改自己的内容
        if request.user.role != 'admin' and instance.author != request.user:
            return Response({
                'code': 403,
                'message': '您没有权限修改此内容'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            material = serializer.save()
            
            return Response({
                'code': 200,
                'message': '学习资料更新成功',
                'data': LearningMaterialDetailSerializer(material).data
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布学习资料"""
        material = self.get_object()
        
        try:
            material.publish()
            
            return Response({
                'code': 200,
                'message': f'《{material.title}》已发布',
                'data': LearningMaterialDetailSerializer(material).data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'发布失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """下架学习资料"""
        material = self.get_object()
        
        try:
            material.archive()
            
            return Response({
                'code': 200,
                'message': f'《{material.title}》已下架',
                'data': LearningMaterialDetailSerializer(material).data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'下架失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量删除学习资料"""
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请提供要删除的学习资料 ID 列表'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = LearningMaterial.objects.filter(id__in=ids).delete()
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个学习资料'
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取学习资料统计数据"""
        total_materials = LearningMaterial.objects.count()
        
        published_count = LearningMaterial.objects.filter(status='published').count()
        draft_count = LearningMaterial.objects.filter(status='draft').count()
        archived_count = LearningMaterial.objects.filter(status='archived').count()
        
        total_views = LearningMaterial.objects.aggregate(
            total=Count('view_count')
        )['total'] or 0
        
        category_stats = LearningMaterial.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        recent_materials = LearningMaterial.objects.filter(
            status='published'
        ).order_by('-created_at')[:5]
        
        popular_materials = LearningMaterial.objects.filter(
            status='published'
        ).order_by('-view_count')[:5]
        
        return Response({
            'code': 200,
            'data': {
                'overview': {
                    'total': total_materials,
                    'published': published_count,
                    'draft': draft_count,
                    'archived': archived_count,
                    'total_views': total_views
                },
                'by_category': list(category_stats),
                'recent_materials': LearningMaterialListSerializer(
                    recent_materials, many=True
                ).data,
                'popular_materials': LearningMaterialListSerializer(
                    popular_materials, many=True
                ).data
            }
        })

    @action(detail=False, methods=['get'])
    def my_materials(self, request):
        """获取当前用户创建的学习资料列表"""
        materials = LearningMaterial.objects.filter(
            author=request.user
        ).order_by('-updated_at')

        page = self.paginate_queryset(materials)
        if page is not None:
            serializer = LearningMaterialListSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)

        serializer = LearningMaterialListSerializer(
            materials, many=True, context=self.get_serializer_context()
        )
        return Response({
            'code': 200,
            'data': serializer.data,
            'total': materials.count()
        })

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        """切换点赞状态"""
        material = self.get_object()
        user = request.user

        existing = MaterialInteraction.objects.filter(
            user=user, material=material, interaction_type='like'
        ).first()

        if existing:
            existing.delete()
            material.like_count = max(0, material.like_count - 1)
            material.save(update_fields=['like_count'])
            return Response({
                'code': 200,
                'message': '取消点赞',
                'data': {'liked': False, 'like_count': material.like_count}
            })

        MaterialInteraction.objects.create(
            user=user, material=material, interaction_type='like'
        )
        material.like_count += 1
        material.save(update_fields=['like_count'])
        return Response({
            'code': 200,
            'message': '点赞成功',
            'data': {'liked': True, 'like_count': material.like_count}
        })

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """切换收藏状态"""
        material = self.get_object()
        user = request.user

        existing = MaterialInteraction.objects.filter(
            user=user, material=material, interaction_type='favorite'
        ).first()

        if existing:
            existing.delete()
            return Response({
                'code': 200,
                'message': '取消收藏',
                'data': {'favorited': False}
            })

        MaterialInteraction.objects.create(
            user=user, material=material, interaction_type='favorite'
        )
        return Response({
            'code': 200,
            'message': '收藏成功',
            'data': {'favorited': True}
        })

    @action(detail=False, methods=['get'])
    def my_favorites(self, request):
        """我的收藏列表"""
        fav_ids = MaterialInteraction.objects.filter(
            user=request.user, interaction_type='favorite'
        ).values_list('material_id', flat=True)
        materials = LearningMaterial.objects.filter(id__in=fav_ids).order_by('-created_at')

        page = self.paginate_queryset(materials)
        if page is not None:
            serializer = LearningMaterialListSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)

        serializer = LearningMaterialListSerializer(
            materials, many=True, context=self.get_serializer_context()
        )
        return Response({
            'code': 200,
            'data': serializer.data,
            'total': materials.count()
        })
