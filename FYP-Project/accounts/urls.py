from django.urls import path
from . import views

urlpatterns = [
    path('register/',                   views.register,     name='register'),
    path('login/',                      views.login_view,   name='login'),
    path('logout/',                     views.logout_view,  name='logout'),
    path('verify-email/<str:token>/',   views.verify_email,  name='verify_email'),
    path('verify-email/resend/',        views.resend_verification, name='resend_verification'),

    path('profile/',                    views.my_profile,   name='my_profile'),
    path('profile/skills/',             views.add_skills,   name='add_skills'),

    path('seniors/',                    views.seniors,      name='seniors'),
    path('leaderboard/',                views.leaderboard,  name='leaderboard'),
    path('teammates/recommended/',      views.recommended_teammates, name='recommended_teammates'),

    path('searches/save/',              views.save_search,        name='save_search'),
    path('searches/',                   views.my_saved_searches,  name='my_saved_searches'),
    path('searches/<int:pk>/delete/',   views.delete_saved_search, name='delete_saved_search'),

    path('profile/<str:username>/',     views.user_profile, name='user_profile'),
]
