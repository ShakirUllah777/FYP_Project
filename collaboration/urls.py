from django.urls import path
from . import views

urlpatterns = [
    path('posts/<int:post_id>/start-team/', views.start_team, name='start_team'),
    path('team/<int:pk>/', views.team_detail, name='team_detail'),
    path('team/<int:pk>/add-member/', views.add_member, name='add_member'),

    path('team/<int:pk>/tasks/add/', views.add_task, name='add_task'),
    path('team/<int:pk>/tasks/<int:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('team/<int:pk>/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),

    path('team/<int:pk>/milestones/add/', views.add_milestone, name='add_milestone'),
    path('team/<int:pk>/milestones/<int:milestone_id>/update/', views.update_milestone, name='update_milestone'),

    path('team/<int:pk>/files/upload/', views.upload_file, name='upload_file'),
    path('team/<int:pk>/files/<int:file_id>/delete/', views.delete_file, name='delete_file'),

    path('team/<int:pk>/meetings/schedule/', views.schedule_meeting, name='schedule_meeting'),

    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/posts/<int:post_id>/endorse/', views.endorse_post, name='endorse_post'),
]
