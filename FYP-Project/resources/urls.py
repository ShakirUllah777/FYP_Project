from django.urls import path
from . import views

urlpatterns = [
    path('resources/', views.resource_library, name='resource_library'),
]
