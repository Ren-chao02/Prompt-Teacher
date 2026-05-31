from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from ..models import Notification, NotificationTemplate
from .serializers import (
    NotificationSerializer,
    NotificationDetailSerializer,
    UnreadCountSerializer,
    SendNotificationSerializer,
    NotificationTemplateSerializer
)
from ..services.notification_service import NotificationService


class NotificationViewSet(viewsets.ModelViewSet):
    """通知管理 ViewSet - 提供完整的CRUD和自定义操作"""

    queryset = Notification.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'priority', '-created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        根据action选择不同的序列化器
        """
        if self.action == 'retrieve':
            return NotificationDetailSerializer
        elif self.action == 'send':
            return SendNotificationSerializer
        elif self.action in ['templates', 'template_detail']:
            return NotificationTemplateSerializer
        return NotificationSerializer

    def get_queryset(self):
        """
        只返回当前用户的通知（管理员可查看所有）
        """
        user = self.request.user
        queryset = super().get_queryset()

        if getattr(user, 'role', '') == 'admin':
            return queryset

        return queryset.filter(recipient=user)

    def list(self, request, *args, **kwargs):
        """
        获取通知列表 (支持分页、筛选、搜索)

        Query Parameters:
            - page: 页码 (默认: 1)
            - page_size: 每页数量 (默认: 20, 最大: 100)
            - notification_type: 筛选类型 (system/learning/practice/interaction/announcement)
            - is_read: 筛选已读状态 (true/false)
            - priority: 筛选优先级 (low/medium/high/urgent)
            - search: 搜索标题和内容
            - ordering: 排序字段 (created_at/-created_at/priority)

        Response:
            {
                "code": 200,
                "message": "获取通知列表成功",
                "data": {
                    "count": 150,
                    "total_pages": 8,
                    "current_page": 1,
                    "results": [...],
                    "unread_count": 12
                }
            }
        """
        response = super().list(request, *args, **kwargs)

        # 添加未读数量到响应数据
        unread_count = NotificationService.get_unread_count(request.user)
        response.data['unread_count'] = unread_count

        return Response({
            'code': 200,
            'message': '获取通知列表成功',
            'data': response.data
        })

    def retrieve(self, request, *args, **kwargs):
        """
        获取通知详情

        URL: /api/v1/notifications/{id}/
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取通知详情成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['put'])
    def mark_read(self, request, pk=None):
        """
        标记单条通知为已读

        URL: PUT /api/v1/notifications/{id}/mark_read/

        Returns:
            {"code": 200, "message": "标记已读成功", "data": {...}}
        """
        notification = self.get_object()
        notification.mark_as_read()

        serializer = self.get_serializer(notification)
        return Response({
            'code': 200,
            'message': '标记已读成功',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        批量标记所有通知为已读

        URL: POST /api/v1/notifications/mark_all_read/

        Returns:
            {"code": 200, "message": "全部标记已读成功", "data": {"updated_count": 10}}
        """
        updated_count = NotificationService.mark_all_as_read(request.user)

        return Response({
            'code': 200,
            'message': f'成功标记 {updated_count} 条通知为已读',
            'data': {'updated_count': updated_count}
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        获取未读通知数量

        URL: GET /api/v1/notifications/unread_count/

        Returns:
            {
                "code": 200,
                "message": "获取未读数量成功",
                "data": {
                    "count": 12,
                    "breakdown": {
                        "system": 2,
                        "learning": 5,
                        "practice": 3,
                        "interaction": 2
                    }
                }
            }
        """
        count = NotificationService.get_unread_count(request.user)
        breakdown = NotificationService.get_unread_count_by_type(request.user)

        serializer = UnreadCountSerializer({
            'count': count,
            'breakdown': breakdown
        })

        return Response({
            'code': 200,
            'message': '获取未读数量成功',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def send(self, request):
        """
        发送通知 (仅管理员/教师可用)

        URL: POST /api/v1/notifications/send/

        Request Body:
            方式1 - 使用模板:
                {
                    "recipient_id": 5 或 "recipients": [5, 6, 7],
                    "template_code": "practice_completed",
                    "context": {"score": 85}
                }

            方式2 - 直接指定内容:
                {
                    "recipient_id": 5 或 "recipients": [5, 6, 7],
                    "title": "自定义标题",
                    "content": "自定义内容",
                    "notification_type": "system",
                    "priority": "high"
                }

        Permission:
            - admin: 可发送给任何人
            - teacher: 可发送给学生

        Returns:
            {"code": 201, "message": "通知发送成功", "data": {"sent_count": 3}}
        """
        # 权限检查
        user_role = getattr(request.user, 'role', '')
        if user_role not in ['admin', 'teacher']:
            return Response(
                {'error': '无权执行此操作，仅管理员和教师可发送通知'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 确定接收者列表
        recipients = []
        if data.get('recipients'):
            from users.models import UserProfile
            recipients = list(UserProfile.objects.filter(id__in=data['recipients']))
        elif data.get('recipient_id'):
            from users.models import UserProfile
            try:
                recipient = UserProfile.objects.get(id=data['recipient_id'])
                recipients = [recipient]
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': f'接收者ID {data["recipient_id"]} 不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not recipients:
            return Response(
                {'error': '未指定有效的接收者'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 准备参数
        send_params = {}
        for key in ['template_code', 'context', 'title', 'content',
                     'notification_type', 'priority', 'link',
                     'is_persistent', 'expires_at']:
            if key in data:
                send_params[key] = data[key]

        # 设置发送者
        send_params['sender'] = request.user

        # 发送通知
        results = NotificationService.broadcast(recipients=recipients, **send_params)

        success_count = sum(1 for r in results if r.get('success'))

        return Response({
            'code': 201,
            'message': f'成功发送 {success_count} 条通知',
            'data': {
                'sent_count': success_count,
                'total_recipients': len(recipients),
                'results': results
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def templates(self, request):
        """
        获取通知模板列表 (仅管理员/教师可见)

        URL: GET /api/v1/notifications/templates/
        """
        user_role = getattr(request.user, 'role', '')
        if user_role not in ['admin', 'teacher']:
            return Response(
                {'error': '无权访问模板列表'},
                status=status.HTTP_403_FORBIDDEN
            )

        templates = NotificationTemplate.objects.filter(is_active=True)
        serializer = NotificationTemplateSerializer(templates, many=True)

        return Response({
            'code': 200,
            'message': '获取模板列表成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='templates/(?P<template_pk>[^/.]+)')
    def template_detail(self, request, template_pk=None, **kwargs):
        """
        获取单个通知模板详情

        URL: GET /api/v1/notifications/templates/{template_code}/
        """
        try:
            template = NotificationTemplate.objects.get(
                template_code=template_pk,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return Response(
                {'error': f'模板 "{template_pk}" 不存在或未启用'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NotificationTemplateSerializer(template)
        return Response({
            'code': 200,
            'message': '获取模板详情成功',
            'data': serializer.data
        })
