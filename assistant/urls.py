from django.urls import path
from . import views

urlpatterns = [
    path('api/ai-suggest/', views.ai_suggest, name='ai_suggest'),
    path('api/chatbot/',    views.chatbot,    name='chatbot'),
    path('resume-extractor/', views.resume_skill_extractor, name='resume_skill_extractor'),
]
