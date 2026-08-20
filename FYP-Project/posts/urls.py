from django.urls import path
from . import views

urlpatterns = [
    path('tasks/',                    views.tasks,           name='tasks'),
    path('posts/add/',                views.add_post,        name='add_post'),
    path('posts/my/',                 views.my_posts,        name='my_posts'),
    path('posts/<int:pk>/',           views.post_detail,     name='post_detail'),
    path('posts/<int:pk>/edit/',      views.edit_post,       name='edit_post'),
    path('posts/<int:pk>/delete/',    views.delete_post,     name='delete_post'),
    path('posts/<int:pk>/complete/',  views.toggle_complete, name='toggle_complete'),
    path('posts/<int:pk>/bookmark/',  views.toggle_bookmark, name='toggle_bookmark'),
    path('posts/saved/',              views.my_bookmarks,    name='my_bookmarks'),
    path('p/<int:pk>/',               views.public_post,     name='public_post'),
]
