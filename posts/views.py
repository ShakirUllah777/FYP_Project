from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Post
from .forms import PostForm
from accounts.models import Skill


@login_required
def tasks(request):
    posts        = Post.objects.exclude(author=request.user).select_related('author__profile')
    skill_filter = request.GET.get('skill')
    type_filter  = request.GET.get('type')
    if skill_filter:
        posts = posts.filter(skills_required__name=skill_filter)
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    skills = Skill.objects.all()
    return render(request, 'posts/tasks.html', {'posts': posts, 'skills': skills})


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post        = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post created successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
        return redirect(request.META.get('HTTP_REFERER', 'tasks'))
    else:
        form = PostForm()
    return render(request, 'posts/add_post.html', {'form': form, 'editing': False})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/add_post.html', {'form': form, 'editing': True})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('my_posts')


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'posts/my_posts.html', {'posts': posts})
