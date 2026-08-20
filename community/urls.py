from django.urls import path
from . import views

urlpatterns = [
    path('community/', views.community_list, name='community_list'),
    path('community/<slug:slug>/', views.community_detail, name='community_detail'),
    path('community/<slug:slug>/join/', views.toggle_join, name='community_toggle_join'),
]
