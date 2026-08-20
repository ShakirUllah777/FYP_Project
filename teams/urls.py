from django.urls import path
from . import views

urlpatterns = [
    path('teams/<int:post_pk>/',              views.workspace,       name='workspace'),
    path('teams/<int:post_pk>/create/',       views.create_team,     name='create_team'),
    path('teams/<int:post_pk>/join/',         views.join_team,       name='join_team'),
    path('teams/<int:post_pk>/tasks/',        views.kanban,          name='kanban'),
    path('teams/<int:post_pk>/tasks/add/',    views.add_task,        name='add_task'),
    path('teams/tasks/<int:task_pk>/update/', views.update_task,     name='update_task'),
    path('teams/tasks/<int:task_pk>/delete/', views.delete_task,     name='delete_task'),
    path('teams/<int:post_pk>/files/',        views.team_files,      name='team_files'),
    path('teams/<int:post_pk>/files/upload/', views.upload_file,     name='upload_team_file'),
    path('teams/files/<int:file_pk>/delete/', views.delete_file,     name='delete_team_file'),
    path('teams/<int:post_pk>/milestones/',   views.milestones,      name='milestones'),
    path('teams/<int:post_pk>/milestones/add/',     views.add_milestone,    name='add_milestone'),
    path('teams/milestones/<int:ms_pk>/update/',    views.update_milestone, name='update_milestone'),
    path('teams/milestones/<int:ms_pk>/delete/',    views.delete_milestone, name='delete_milestone'),
]
