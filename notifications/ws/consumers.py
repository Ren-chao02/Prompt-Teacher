import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    通知WebSocket消费者

    功能:
    - JWT认证连接
    - 实时接收通知消息
    - 心跳保活机制
    - 在线状态管理

    协议格式:
    - Client -> Server: {"type": "heartbeat"}
    - Server -> Client: {"type": "new_notification", "payload": {...}, "timestamp": "..."}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.group_name = None

    async def connect(self):
        """
        WebSocket连接建立时调用

        流程:
        1. 从query_string获取token
        2. 验证JWT token
        3. 认证成功后加入用户专属group
        """
        await self.accept()

        # 获取认证token
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        token = params.get('token', '')

        if not token:
            await self.send_error('Missing authentication token', close=True)
            return

        # 验证用户身份
        user = await self.authenticate_user(token)
        if not user:
            await self.send_error('Invalid or expired token', close=True)
            return

        self.user = user
        self.user_id = user.id
        self.group_name = f'user_{self.user_id}'

        # 加入用户的专属channel group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # 发送连接成功消息
        await self.send_json({
            'type': 'connected',
            'message': f'WebSocket connected (User #{self.user_id})',
            'user_id': self.user_id,
            'timestamp': timezone.now().isoformat()
        })

        print(f'[WebSocket] User {self.user.username} (ID:{self.user_id}) connected')

    async def disconnect(self, close_code):
        """WebSocket断开连接"""
        if hasattr(self, 'group_name') and self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f'[WebSocket] User {self.user_id} disconnected (code: {close_code})')

    async def receive(self, text_data=None, bytes_data=None):
        """
        接收客户端消息

        支持的消息类型:
        - heartbeat: 心跳包，保持连接活跃
        - ping: 简单ping测试
        """
        try:
            data = json.loads(text_data) if text_data else {}
            message_type = data.get('type', '')

            if message_type == 'heartbeat':
                await self.handle_heartbeat()
            elif message_type == 'ping':
                await self.send_json({'type': 'pong', 'timestamp': timezone.now().isoformat()})
            else:
                await self.send_error(f'Unknown message type: {message_type}')

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')

    async def notify(self, event):
        """
        处理来自Channel Layer的通知消息

        当NotificationService._push_to_user()调用时会触发此方法

        Args:
            event: {
                'type': 'notify',
                'message': {
                    'type': 'new_notification',
                    'payload': {...},
                    'timestamp': '...'
                }
            }
        """
        message = event['message']

        # 转发给客户端
        await self.send_json(message)

    async def handle_heartbeat(self):
        """处理心跳请求"""
        await self.send_json({
            'type': 'heartbeat_ack',
            'timestamp': timezone.now().isoformat()
        })

    @database_sync_to_async
    def authenticate_user(self, token: str):
        """
        验证JWT Token并返回用户实例

        Args:
            token: JWT access token字符串

        Returns:
            UserProfile实例 或 None
        """
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework.request import Request

            # 构造虚拟request对象用于JWT验证
            class FakeRequest:
                META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

            authenticator = JWTAuthentication()
            result = authenticator.authenticate(Request(FakeRequest()))

            if result:
                user, _ = result
                return user

            return None

        except Exception as e:
            print(f'[WebSocket] Authentication failed: {e}')
            return None

    async def send_json(self, data: dict):
        """发送JSON格式的消息给客户端"""
        try:
            await self.send(text_data=json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print(f'[WebSocket] Failed to send message: {e}')

    async def send_error(self, message: str, close: bool = False):
        """发送错误消息"""
        error_data = {
            'type': 'error',
            'error': message,
            'timestamp': timezone.now().isoformat()
        }

        await self.send_json(error_data)

        if close:
            await self.close(code=4000)
