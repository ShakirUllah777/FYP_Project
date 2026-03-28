from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.home,         name='home'),
    path('register/',                   views.register,     name='register'),
    path('login/',                      views.login_view,   name='login'),
    path('logout/',                     views.logout_view,  name='logout'),
    path('tasks/',                      views.tasks,        name='tasks'),
    path('posts/add/',                  views.add_post,     name='add_post'),
    path('posts/my/',                   views.my_posts,     name='my_posts'),
    path('posts/<int:pk>/edit/',        views.edit_post,    name='edit_post'),
    path('posts/<int:pk>/delete/',      views.delete_post,  name='delete_post'),
    path('profile/',                    views.my_profile,   name='my_profile'),
    path('profile/skills/',             views.add_skills,   name='add_skills'),
    path('profile/<str:username>/',     views.user_profile, name='user_profile'),
    path('messages/',                   views.inbox,        name='inbox'),
    path('messages/send/',              views.send_message, name='send_message'),
    path('messages/<str:username>/',    views.chat,         name='chat'),
    path('api/ai-suggest/', views.ai_suggest, name='ai_suggest'),
]