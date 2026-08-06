from django.urls import path
from . import views

urlpatterns = [
    path('api/ai-suggest/', views.ai_suggest, name='ai_suggest'),
    path('api/chatbot/',    views.chatbot,    name='chatbot'),
]
