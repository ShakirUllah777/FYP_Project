from django.urls import path
from . import views

urlpatterns = [
    path('community/', views.community_list, name='community_list'),
    path('community/create/', views.create_community, name='create_community'),
    path('community/<slug:slug>/', views.community_detail, name='community_detail'),
    path('community/<slug:slug>/join/', views.toggle_join, name='community_toggle_join'),
    path('community/<slug:slug>/post/create/', views.create_community_post, name='create_community_post'),
    path('community/post/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
]

