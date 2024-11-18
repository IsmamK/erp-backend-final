import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from api import routing
from django.urls import re_path
from api import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
from django.urls import path

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            
            path("ws/driver/<int:driver_id>/", consumers.DriverConsumer.as_asgi()),

        ])
    ),
})
