from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Resource


@login_required
def resource_library(request):
    category = request.GET.get('category', '')
    resources = Resource.objects.all()
    if category:
        resources = resources.filter(category=category)

    profile = getattr(request.user, 'profile', None)
    if profile and profile.department:
        from django.db.models import Q
        resources = resources.filter(Q(department='') | Q(department=profile.department))

    return render(request, 'resources/library.html', {
        'resources': resources,
        'categories': Resource.CATEGORY_CHOICES,
        'active_category': category,
    })
