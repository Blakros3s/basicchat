# use the real project name; replace 'config' with 'chatapp' if your project root is chatapp
import os

# load Django settings path into environment so Django can be configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')

# get_asgi_application initializes Django and returns the ASGI app that handles normal HTTP requests.
# We call this first so Django models/settings are ready before we import routing that may import models.
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# Channels routing and middleware helpers
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator  # ensures Host/Origin checks

# Import your websocket url patterns (do this after Django setup)
from core.routing import websocket_urlpatterns

# ProtocolTypeRouter maps protocol names to ASGI apps.
# - "http" goes to the normal Django ASGI app
# - "websocket" gets wrapped with security + auth and routed to websocket_urlpatterns
application = ProtocolTypeRouter({
    # Handles regular HTTP requests with Django's ASGI app
    "http": django_asgi_app,

    # Handles WebSocket connections
    "websocket": AllowedHostsOriginValidator(               # optional security layer
        AuthMiddlewareStack(                               # adds Django user/auth support on websocket
            URLRouter(websocket_urlpatterns)               # routes websocket paths to consumers
        )
    ),
})

"""from channels.security.websocket import OriginValidator

allowed_origins = ["https://yourdomain.com", "https://www.yourdomain.com"]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": OriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
        allowed_origins=allowed_origins
    ),
})"""