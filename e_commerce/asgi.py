"""
ASGI config for e_commerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from asgi_cors import asgi_cors
import shop_chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                shop_chat.routing.websocket_urlpatterns
            )
        )
    )
})

application = asgi_cors(application, allow_all=True)

# application = get_asgi_application()
