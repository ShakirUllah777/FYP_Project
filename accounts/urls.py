from django.urls import path
from . import views

urlpatterns = [
    path('register/',                   views.register,     name='register'),
    path('login/',                      views.login_view,   name='login'),
    path('logout/',                     views.logout_view,  name='logout'),
    path('profile/',                    views.my_profile,   name='my_profile'),
    path('profile/skills/',             views.add_skills,   name='add_skills'),
    path('profile/<str:username>/',     views.user_profile, name='user_profile'),
    path('seniors/',                    views.seniors,      name='seniors'),
]
