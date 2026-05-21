from django.urls import path
from shop_chat.views import chat_index_page

urlpatterns = [
    path('room/<str:room_name>/', chat_index_page, name='chat_page')
]
