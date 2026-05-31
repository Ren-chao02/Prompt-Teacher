from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import UserProfile
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from ..permissions import IsAdmin, IsTeacher


class LoginAPIView(TokenObtainPairView):
    """自定义登录视图 - 扩展返回用户信息"""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)
        
        # 获取用户信息
        user_serializer = UserSerializer(user)
        
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_serializer.data
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """注销视图 - 将 refresh token 加入黑名单"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'code': 200,
                'message': '注销成功'
            })
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'注销失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    """获取当前登录用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    def put(self, request):
        """更新当前用户信息"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': UserSerializer(request.user).data
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            
            return Response({
                'code': 200,
                'message': '密码修改成功，请重新登录'
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理 ViewSet - 完整的 CRUD + 批量操作
    
    list: 返回用户列表（支持搜索、筛选、排序）
    retrieve: 返回用户详情
    create: 创建新用户（仅管理员）
    update: 更新用户信息（管理员或本人）
    partial_update: 部分更新
    destroy: 删除用户（仅管理员）
    
    自定义 action:
    - bulk_delete: 批量删除
    - reset_password: 重置密码
    - my_students: 获取我的学生列表（教师专用）
    """
    
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active', 'major', 'semester']
    search_fields = ['username', 'email', 'student_id', 'phone', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username', 'id']
    ordering = ['-date_joined']

    def get_permissions(self):
        """根据 action 动态设置权限"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        elif self.action in ['bulk_delete', 'reset_password']:
            permission_classes = [IsAdmin]
        elif self.action == 'my_students':
            permission_classes = [IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """根据用户角色过滤数据"""
        user = self.request.user
        
        if not user.is_authenticated:
            return UserProfile.objects.none()
        
        if user.role == 'admin':
            queryset = UserProfile.objects.all()
        elif user.role == 'teacher':
            queryset = UserProfile.objects.filter(
                models.Q(pk=user.pk) | models.Q(teacher=user)
            )
        else:
            queryset = UserProfile.objects.filter(pk=user.pk)
        
        return queryset

    def get_serializer_class(self):
        """根据 action 选择序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """创建用户（仅管理员）"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'code': 201,
                'message': '用户创建成功',
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """更新用户信息（支持管理员或本人）"""
        instance = self.get_object()
        
        # 权限检查：非管理员只能修改自己的信息
        if request.user.role != 'admin' and instance.pk != request.user.pk:
            return Response({
                'code': 403,
                'message': '您没有权限修改其他用户的信息'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': UserSerializer(user).data
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量删除用户"""
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请提供要删除的用户 ID 列表'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = UserProfile.objects.filter(id__in=ids).delete()
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个用户'
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'code': 400,
                'message': '请提供新密码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({
                'code': 400,
                'message': '密码长度不能少于6位'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'code': 200,
            'message': f'用户 {user.username} 的密码已重置成功'
        })

    @action(detail=False, methods=['get'])
    def my_students(self, request):
        """获取当前教师的学生列表"""
        teacher = request.user
        
        if teacher.role not in ['admin', 'teacher']:
            return Response({
                'code': 403,
                'message': '只有教师才能查看学生列表'
            }, status=status.HTTP_403_FORBIDDEN)
        
        students = UserProfile.objects.filter(teacher=teacher)
        
        # 应用搜索
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            students = students.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(student_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # 应用排序
        ordering = request.query_params.get('ordering', '-date_joined')
        students = students.order_by(ordering)
        
        # 分页
        page = self.paginate_queryset(students)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(students, many=True)
        return Response({
            'code': 200,
            'data': serializer.data,
            'total': students.count()
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取用户统计数据"""
        total_users = UserProfile.objects.count()
        admin_count = UserProfile.objects.filter(role='admin').count()
        teacher_count = UserProfile.objects.filter(role='teacher').count()
        student_count = UserProfile.objects.filter(role='student').count()
        
        recent_users = UserProfile.objects.order_by('-date_joined')[:5]
        
        return Response({
            'code': 200,
            'data': {
                'total': total_users,
                'by_role': {
                    'admin': admin_count,
                    'teacher': teacher_count,
                    'student': student_count
                },
                'recent_users': UserSerializer(recent_users, many=True).data
            }
        })

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None):
        """启用/禁用用户账号"""
        user = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response({
                'code': 400,
                'message': '请提供 is_active 参数 (true/false)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = is_active
        user.save()
        
        status_text = '启用' if is_active else '禁用'
        
        return Response({
            'code': 200,
            'message': f'用户 {user.username} 已{status_text}',
            'data': UserSerializer(user).data
        })
