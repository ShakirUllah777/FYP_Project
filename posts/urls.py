from django.urls import path
from . import views

urlpatterns = [
    path('tasks/',                 views.tasks,       name='tasks'),
    path('posts/add/',             views.add_post,    name='add_post'),
    path('posts/my/',              views.my_posts,    name='my_posts'),
    path('posts/<int:pk>/edit/',   views.edit_post,   name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
]
