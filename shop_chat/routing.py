from django.urls import re_path
from shop_chat.consumer import ShopChatConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ShopChatConsumer.as_asgi()),
]
