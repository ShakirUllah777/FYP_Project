from django.urls import path
from . import views

urlpatterns = [
    path('messages/',                   views.inbox,        name='inbox'),
    path('messages/send/',              views.send_message, name='send_message'),
    path('messages/<str:username>/',    views.chat,         name='chat'),
    path('profile/<str:username>/block/', views.toggle_block, name='toggle_block'),
]
