from django.urls import path
from . import views

urlpatterns = [
    path('profile/<str:username>/review/', views.leave_review, name='leave_review'),
    path('profile/<str:username>/report/', views.report_user, name='report_user'),
    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('moderation/<int:pk>/update/', views.update_report_status, name='update_report_status'),
]
