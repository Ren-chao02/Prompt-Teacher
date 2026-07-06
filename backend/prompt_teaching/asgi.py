"""
ASGI config for prompt_teaching project.

Configured for Django Channels (WebSocket support).
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import notifications.ws.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            notifications.ws.routing.websocket_urlpatterns
        )
    ),
})
